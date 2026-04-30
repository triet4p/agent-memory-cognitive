"""Minimal memory engine bootstrap for CogMem schema operations."""

from __future__ import annotations

import contextvars
import logging
import os
import re
from contextlib import contextmanager
from datetime import UTC, datetime
from typing import Any

import asyncpg
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

from cogmem_api import config
from cogmem_api.models import Base
from cogmem_api.engine.llm_wrapper import LLMConfig
from cogmem_api.pg0 import EmbeddedPostgres, parse_pg0_url
from .db_utils import acquire_with_retry
from .embeddings import DeterministicEmbeddings, create_embeddings_from_env

_current_schema: contextvars.ContextVar[str | None] = contextvars.ContextVar("current_schema", default=None)

_PROTECTED_TABLES = frozenset(
    [
        "memory_units",
        "memory_links",
        "unit_entities",
        "entities",
        "entity_cooccurrences",
        "banks",
        "documents",
        "chunks",
        "async_operations",
        "file_storage",
    ]
)

_VALIDATE_SQL_SCHEMAS = True
logger = logging.getLogger(__name__)


class UnqualifiedTableError(Exception):
    """Raised when SQL contains unqualified references to protected tables."""



def get_current_schema() -> str:
    """Get current schema from task context, falling back to default config."""
    schema = _current_schema.get()
    return schema if schema is not None else config.DATABASE_SCHEMA


@contextmanager
def set_schema_context(schema: str):
    """Temporarily override the active schema in the current context."""
    token = _current_schema.set(schema)
    try:
        yield
    finally:
        _current_schema.reset(token)



def fq_table(table_name: str) -> str:
    """Return fully-qualified table name using active schema context."""
    return f"{get_current_schema()}.{table_name}"



def validate_sql_schema(sql: str) -> None:
    """Ensure protected tables are always referenced with explicit schema prefix."""
    if not _VALIDATE_SQL_SCHEMAS:
        return

    sql_upper = sql.upper()
    for table in _PROTECTED_TABLES:
        table_upper = table.upper()
        patterns = [
            rf"FROM\s+{table_upper}(?:\s|$|,|\)|;)",
            rf"JOIN\s+{table_upper}(?:\s|$|,|\)|;)",
            rf"INTO\s+{table_upper}(?:\s|$|\()",
            rf"UPDATE\s+{table_upper}(?:\s|$)",
            rf"DELETE\s+FROM\s+{table_upper}(?:\s|$|;)",
        ]

        for pattern in patterns:
            match = re.search(pattern, sql_upper)
            if not match:
                continue

            start = match.start()
            table_pos = sql_upper.find(table_upper, start)
            if table_pos > 0:
                prefix = sql[:table_pos].rstrip()
                if not prefix.endswith("."):
                    raise UnqualifiedTableError(
                        f"Unqualified table reference '{table}'. Use fq_table('{table}') for schema safety."
                    )


class MemoryEngine:
    """Minimal CogMem engine scaffold for schema-safe DB bootstrap."""

    def __init__(
        self,
        db_url: str | None = None,
        database_schema: str | None = None,
        pool_min_size: int | None = None,
        pool_max_size: int | None = None,
    ):
        resolved_db_url = db_url if db_url is not None else os.getenv(config.ENV_DATABASE_URL)

        self._pg0: EmbeddedPostgres | None = None
        if resolved_db_url:
            self._use_pg0, self._pg0_instance_name, self._pg0_port = parse_pg0_url(resolved_db_url)
        else:
            self._use_pg0, self._pg0_instance_name, self._pg0_port = (False, None, None)

        if self._use_pg0:
            self.db_url = None
        else:
            self.db_url = resolved_db_url

        self.database_schema = database_schema or config.DATABASE_SCHEMA
        self._pool_min_size = pool_min_size if pool_min_size is not None else config.DB_POOL_MIN_SIZE
        self._pool_max_size = pool_max_size if pool_max_size is not None else config.DB_POOL_MAX_SIZE
        self._pool: asyncpg.Pool | None = None
        self._runtime_config = config._get_raw_config()
        self._engine_config = config.get_config()
        self._cross_encoder: Any = None
        self._embeddings_model: Any = None
        self._entity_resolver: Any = None
        self._initialized = False

    @property
    def initialized(self) -> bool:
        return self._initialized

    @property
    def pool(self) -> asyncpg.Pool | None:
        return self._pool

    async def initialize(self) -> None:
        """Initialize DB connection pool if db_url is provided."""
        if self._initialized:
            return

        _current_schema.set(self.database_schema)

        if self._use_pg0:
            kwargs: dict[str, Any] = {"name": self._pg0_instance_name}
            if self._pg0_port is not None:
                kwargs["port"] = self._pg0_port
            pg0 = EmbeddedPostgres(**kwargs)
            was_already_running = await pg0.is_running()
            self.db_url = await pg0.ensure_running()
            if not was_already_running:
                self._pg0 = pg0

        await self._initialize_embeddings_model()

        if not self.db_url:
            self._initialized = True
            return

        async def _init_pool_connection(conn: asyncpg.Connection) -> None:
            """Set per-connection HNSW search parameters for accuracy."""
            await conn.execute("SET hnsw.ef_search = 200")

        self._pool = await asyncpg.create_pool(
            self.db_url,
            min_size=self._pool_min_size,
            max_size=self._pool_max_size,
            init=_init_pool_connection,
        )

        await self._bootstrap_schema_objects()
        self._initialized = True

    async def _bootstrap_schema_objects(self) -> None:
        """Ensure required schema/tables exist for retain/recall runtime paths."""
        if not self.db_url:
            return

        sqlalchemy_url = self.db_url
        if sqlalchemy_url.startswith("postgresql://"):
            sqlalchemy_url = sqlalchemy_url.replace("postgresql://", "postgresql+asyncpg://", 1)

        engine = create_async_engine(sqlalchemy_url)
        try:
            async with engine.begin() as conn:
                await conn.execute(text(f'CREATE SCHEMA IF NOT EXISTS "{self.database_schema}"'))
                try:
                    await conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
                except Exception as exc:  # pragma: no cover - runtime guard
                    logger.warning("Unable to ensure pgvector extension: %s", exc)

                await conn.execute(text(f'SET search_path TO "{self.database_schema}"'))
                await conn.run_sync(Base.metadata.create_all)

                # Columns and indexes not expressible in SQLAlchemy ORM are created
                # idempotently here. Each DDL runs inside its own savepoint so a
                # failure (e.g. column already exists on an old DB) does not abort
                # the surrounding transaction and block subsequent statements.
                async def _safe_ddl(label: str, sql: str) -> None:
                    try:
                        async with conn.begin_nested():
                            await conn.execute(text(sql))
                    except Exception as exc:
                        logger.warning("Schema extension skipped (%s): %s", label, exc)

                # tags text[] — create_all does not ALTER existing tables, so we
                # must add this column explicitly for databases that pre-date it.
                await _safe_ddl(
                    "tags column",
                    "ALTER TABLE memory_units ADD COLUMN IF NOT EXISTS tags text[]",
                )

                # chunk_id text — added in S24.7 to track which chunk a fact came from.
                await _safe_ddl(
                    "chunk_id column",
                    "ALTER TABLE memory_units ADD COLUMN IF NOT EXISTS chunk_id text",
                )
                await _safe_ddl(
                    "idx_memory_units_chunk_id",
                    "CREATE INDEX IF NOT EXISTS idx_memory_units_chunk_id "
                    "ON memory_units (chunk_id) WHERE chunk_id IS NOT NULL",
                )

                # search_vector GENERATED ALWAYS AS STORED — SQLAlchemy ORM cannot
                # express this PostgreSQL syntax, so it is always created here.
                await _safe_ddl(
                    "search_vector column",
                    "ALTER TABLE memory_units "
                    "ADD COLUMN IF NOT EXISTS search_vector tsvector "
                    "GENERATED ALWAYS AS ("
                    "  to_tsvector('english',"
                    "    coalesce(text, '') || ' ' || coalesce(raw_snippet, ''))"
                    ") STORED",
                )

                # Specialized indexes (GIN, partial HNSW, covering) that cannot be
                # expressed in the ORM __table_args__.
                for idx_name, stmt in [
                    ("idx_memory_units_search_vector",
                     "CREATE INDEX IF NOT EXISTS idx_memory_units_search_vector "
                     "ON memory_units USING gin(search_vector)"),
                    ("idx_memory_units_tags",
                     "CREATE INDEX IF NOT EXISTS idx_memory_units_tags "
                     "ON memory_units USING gin(tags) WHERE tags IS NOT NULL"),
                    ("idx_mu_emb_world",
                     "CREATE INDEX IF NOT EXISTS idx_mu_emb_world "
                     "ON memory_units USING hnsw (embedding vector_cosine_ops) WHERE fact_type = 'world'"),
                    ("idx_mu_emb_experience",
                     "CREATE INDEX IF NOT EXISTS idx_mu_emb_experience "
                     "ON memory_units USING hnsw (embedding vector_cosine_ops) WHERE fact_type = 'experience'"),
                    ("idx_mu_emb_opinion",
                     "CREATE INDEX IF NOT EXISTS idx_mu_emb_opinion "
                     "ON memory_units USING hnsw (embedding vector_cosine_ops) WHERE fact_type = 'opinion'"),
                    ("idx_mu_emb_habit",
                     "CREATE INDEX IF NOT EXISTS idx_mu_emb_habit "
                     "ON memory_units USING hnsw (embedding vector_cosine_ops) WHERE fact_type = 'habit'"),
                    ("idx_mu_emb_intention",
                     "CREATE INDEX IF NOT EXISTS idx_mu_emb_intention "
                     "ON memory_units USING hnsw (embedding vector_cosine_ops) WHERE fact_type = 'intention'"),
                    ("idx_mu_emb_action_effect",
                     "CREATE INDEX IF NOT EXISTS idx_mu_emb_action_effect "
                     "ON memory_units USING hnsw (embedding vector_cosine_ops) WHERE fact_type = 'action_effect'"),
                    ("idx_memory_links_entity_covering",
                     "CREATE INDEX IF NOT EXISTS idx_memory_links_entity_covering "
                     "ON memory_links (from_unit_id) INCLUDE (to_unit_id, entity_id) "
                     "WHERE link_type = 'entity'"),
                    ("idx_memory_links_to_type_weight",
                     "CREATE INDEX IF NOT EXISTS idx_memory_links_to_type_weight "
                     "ON memory_links (to_unit_id, link_type, weight DESC)"),
                ]:
                    await _safe_ddl(idx_name, stmt)
        finally:
            await engine.dispose()

    async def _initialize_embeddings_model(self) -> None:
        """Initialize configured embeddings provider with deterministic fallback."""
        if self._embeddings_model is not None:
            return

        try:
            model = create_embeddings_from_env()
            await model.initialize()
            self._embeddings_model = model
            logger.info("Embeddings provider initialized: %s", model.provider_name)
        except Exception as exc:  # pragma: no cover - defensive runtime guard
            fallback = DeterministicEmbeddings(config.EMBEDDING_DIMENSION)
            await fallback.initialize()
            self._embeddings_model = fallback
            logger.warning(
                "Embeddings provider initialization failed (%s). Falling back to deterministic embeddings.",
                exc,
            )

    async def close(self) -> None:
        """Close connection pool if initialized."""
        if self._pool is not None:
            close = getattr(self._pool, "close", None)
            if callable(close):
                maybe_awaitable = close()
                if hasattr(maybe_awaitable, "__await__"):
                    await maybe_awaitable
            self._pool = None

        if self._pg0 is not None:
            await self._pg0.stop()
            self._pg0 = None

        self._initialized = False

    async def execute(self, sql: str, *args: Any) -> str:
        """Execute SQL after schema safety validation."""
        validate_sql_schema(sql)
        if self._pool is None:
            raise RuntimeError("MemoryEngine is not connected. Call initialize() with db_url first.")

        async with acquire_with_retry(self._pool) as conn:
            return await conn.execute(sql, *args)

    async def health_check(self) -> dict[str, Any]:
        """Return runtime health information for service probes."""
        health: dict[str, Any] = {
            "status": "healthy",
            "initialized": self._initialized,
            "database": {
                "url_configured": bool(self.db_url),
                "connected": False,
                "schema": self.database_schema,
            },
        }

        if self._use_pg0:
            health["database"]["mode"] = "embedded_pg0"

        if self._pool is None:
            if self.db_url:
                health["status"] = "unhealthy"
                health["reason"] = "database pool is not initialized"
            else:
                health["database"]["mode"] = "no_database_url"
            return health

        try:
            async with acquire_with_retry(self._pool) as conn:
                await conn.fetchval("SELECT 1")
            health["database"]["connected"] = True
            return health
        except Exception as exc:  # pragma: no cover - defensive runtime guard
            health["status"] = "unhealthy"
            health["reason"] = f"database check failed: {exc}"
            return health

    @staticmethod
    def _format_date(dt: datetime) -> str:
        return dt.astimezone(UTC).strftime("%Y-%m-%d")

    def _build_retain_llm_config(self) -> LLMConfig | None:
        if not self._runtime_config.llm_base_url:
            return None
        return LLMConfig(
            provider=self._runtime_config.llm_provider,
            model=self._runtime_config.llm_model,
            api_key=self._runtime_config.llm_api_key,
            base_url=self._runtime_config.llm_base_url,
            timeout=self._runtime_config.retain_llm_timeout,
        )

    def _build_judge_llm_config(self) -> LLMConfig | None:
        if not self._runtime_config.judge_llm_base_url:
            return None
        return LLMConfig(
            provider=self._runtime_config.judge_llm_provider,
            model=self._runtime_config.judge_llm_model,
            api_key=self._runtime_config.judge_llm_api_key,
            base_url=self._runtime_config.judge_llm_base_url,
            timeout=self._runtime_config.judge_llm_timeout,
        )

    def _build_generate_llm_config(self) -> LLMConfig | None:
        model = self._runtime_config.generate_llm_model or self._runtime_config.llm_model
        base_url = self._runtime_config.generate_llm_base_url or self._runtime_config.llm_base_url
        if not base_url:
            return None
        return LLMConfig(
            provider=self._runtime_config.llm_provider,
            model=model,
            api_key=self._runtime_config.generate_llm_api_key or self._runtime_config.llm_api_key,
            base_url=base_url,
            timeout=self._runtime_config.generate_llm_timeout or self._runtime_config.retain_llm_timeout,
        )

    async def retain_batch_async(
        self,
        bank_id: str,
        contents: list[dict[str, Any]],
        *,
        document_id: str | None = None,
        fact_type_override: str | None = None,
        confidence_score: float | None = None,
        document_tags: list[str] | None = None,
        return_usage: bool = False,
        operation_id: str | None = None,
    ):
        from cogmem_api.engine.retain.orchestrator import retain_batch

        if not self._initialized:
            raise RuntimeError("MemoryEngine is not initialized. Call initialize() before retain.")
        if self._pool is None:
            raise RuntimeError("MemoryEngine is not connected. Configure a database URL before retain.")

        unit_ids, usage = await retain_batch(
            pool=self._pool,
            embeddings_model=self._embeddings_model,
            llm_config=self._build_retain_llm_config(),
            entity_resolver=self._entity_resolver,
            format_date_fn=self._format_date,
            bank_id=bank_id,
            contents_dicts=contents,
            config=self._engine_config,
            document_id=document_id,
            is_first_batch=True,
            fact_type_override=fact_type_override,
            confidence_score=confidence_score,
            document_tags=document_tags,
            operation_id=operation_id,
            schema=self.database_schema,
        )
        if return_usage:
            return unit_ids, usage
        return unit_ids

    async def retain_async(
        self,
        bank_id: str,
        content: str,
        *,
        context: str = "",
        event_date: datetime | str | None = None,
        document_id: str | None = None,
        fact_type_override: str | None = None,
        confidence_score: float | None = None,
    ) -> list[str]:
        payload: dict[str, Any] = {"content": content, "context": context}
        if event_date is not None:
            payload["event_date"] = event_date
        if document_id is not None:
            payload["document_id"] = document_id

        result = await self.retain_batch_async(
            bank_id=bank_id,
            contents=[payload],
            document_id=document_id,
            fact_type_override=fact_type_override,
            confidence_score=confidence_score,
        )
        return result[0] if result else []

    async def _fallback_recall_from_conn(
        self,
        bank_id: str,
        query: str,
        fact_types: list[str],
        max_tokens: int,
        limit: int,
    ) -> list[dict[str, Any]]:
        if self._pool is None:
            raise RuntimeError("MemoryEngine is not connected. Configure a database URL before recall.")

        async with acquire_with_retry(self._pool) as conn:
            if hasattr(conn, "recall_memory_units"):
                rows = await conn.recall_memory_units(
                    bank_id=bank_id,
                    query=query,
                    fact_types=fact_types,
                    limit=limit,
                )
            else:
                rows = await conn.fetch(
                    f"""
                    SELECT
                        id::text AS id,
                        text,
                        fact_type,
                        raw_snippet,
                        document_id,
                        occurred_start,
                        mentioned_at,
                        event_date
                    FROM {fq_table("memory_units")}
                    WHERE bank_id = $1
                      AND fact_type = ANY($2)
                    ORDER BY event_date DESC
                    LIMIT $3
                    """,
                    bank_id,
                    fact_types,
                    max(limit * 4, 20),
                )

        normalized_rows: list[dict[str, Any]] = [dict(row) for row in rows]
        query_terms = {token for token in re.findall(r"[a-z0-9]+", query.lower()) if token}

        def lexical_score(text: str) -> float:
            if not query_terms:
                return 0.0
            terms = {token for token in re.findall(r"[a-z0-9]+", text.lower()) if token}
            if not terms:
                return 0.0
            return float(len(query_terms.intersection(terms)))

        scored = sorted(normalized_rows, key=lambda item: lexical_score(str(item.get("text") or "")), reverse=True)

        selected: list[dict[str, Any]] = []
        used_tokens = 0
        for row in scored:
            text = str(row.get("text") or "")
            estimated = max(1, len(text.split()))
            if max_tokens > 0 and used_tokens + estimated > max_tokens:
                break

            selected.append(
                {
                    "id": str(row.get("id") or ""),
                    "text": text,
                    "fact_type": str(row.get("fact_type") or "world"),
                    "raw_snippet": row.get("raw_snippet"),
                    "document_id": row.get("document_id"),
                    "score": lexical_score(text),
                }
            )
            used_tokens += estimated
            if len(selected) >= limit:
                break

        return selected

    async def recall_async(
        self,
        bank_id: str,
        query: str,
        *,
        budget: str = "mid",
        max_tokens: int = 4096,
        top_k: int | None = None,
        snippet_budget: int | None = None,
        enable_trace: bool = False,
        fact_types: list[str] | None = None,
        question_date: datetime | None = None,
        adaptive_router: bool = True,
        graph_retriever_override: str | None = None,
    ) -> dict[str, Any]:
        from cogmem_api.engine.retain import embedding_utils
        from cogmem_api.engine.retain.types import COGMEM_FACT_TYPES
        from cogmem_api.engine.search.reranking import CrossEncoderReranker, apply_combined_scoring
        from cogmem_api.engine.search.retrieval import fuse_parallel_results, make_graph_retriever, retrieve_all_fact_types_parallel

        if not self._initialized:
            raise RuntimeError("MemoryEngine is not initialized. Call initialize() before recall.")
        if self._pool is None:
            raise RuntimeError("MemoryEngine is not connected. Configure a database URL before recall.")

        allowed_types = set(COGMEM_FACT_TYPES)
        effective_types = [ft for ft in (fact_types or list(COGMEM_FACT_TYPES)) if ft in allowed_types]
        if not effective_types:
            return {"results": [], "trace": {"reason": "no_valid_fact_types"} if enable_trace else None}

        budget_mapping = {"low": 100, "mid": 300, "high": 1000}
        thinking_budget = budget_mapping.get(str(budget).lower(), 300)

        try:
            query_embedding = await embedding_utils.generate_embeddings_batch(
                embeddings_model=self._embeddings_model,
                texts=[query],
            )
            query_embedding_str = str(query_embedding[0]) if query_embedding else "[]"

            from cogmem_api.engine.query_analyzer import FlatQueryAnalyzer
            query_analyzer_override = None if adaptive_router else FlatQueryAnalyzer()
            graph_retriever = make_graph_retriever(graph_retriever_override) if graph_retriever_override else None

            retrieval_result = await retrieve_all_fact_types_parallel(
                pool=self._pool,
                query_text=query,
                query_embedding_str=query_embedding_str,
                bank_id=bank_id,
                fact_types=effective_types,
                thinking_budget=thinking_budget,
                question_date=question_date,
                query_analyzer=query_analyzer_override,
                graph_retriever=graph_retriever,
            )

            merged_by_id: dict[str, Any] = {}
            for ft in effective_types:
                parallel = retrieval_result.results_by_fact_type.get(ft)
                if parallel is None:
                    continue
                fused = fuse_parallel_results(
                    parallel_result=parallel,
                    query_type=retrieval_result.query_type,
                    rrf_weights=retrieval_result.rrf_weights,
                )
                for candidate in fused:
                    existing = merged_by_id.get(candidate.id)
                    if existing is None or candidate.rrf_score > existing.rrf_score:
                        merged_by_id[candidate.id] = candidate

            merged_candidates = sorted(merged_by_id.values(), key=lambda item: item.rrf_score, reverse=True)
            global_rrf_rank_by_id = {c.id: rank + 1 for rank, c in enumerate(merged_candidates)}

            reranked_results: list[dict[str, Any]] = []
            cross_encoder_ok = False
            if merged_candidates:
                candidate_limit = min(len(merged_candidates), self._engine_config.reranker_max_candidates)
                top_candidates = merged_candidates[:candidate_limit]

                try:
                    if self._cross_encoder is None:
                        self._cross_encoder = CrossEncoderReranker()

                    await self._cross_encoder.ensure_initialized()
                    scored = await self._cross_encoder.rerank(query=query, candidates=top_candidates)
                    apply_combined_scoring(scored_results=scored, now=datetime.now(UTC))
                    scored.sort(key=lambda item: item.combined_score, reverse=True)
                    cross_encoder_ok = True
                except Exception as ce_exc:
                    logger.warning("Cross-encoder reranking failed, using RRF order: %s", ce_exc)
                    # Wrap RRF-ordered candidates as ScoredResult stubs so the loop below works uniformly.
                    from cogmem_api.engine.search.types import ScoredResult
                    scored = [
                        ScoredResult(candidate=c, cross_encoder_score=0.0, cross_encoder_score_normalized=c.rrf_score)
                        for c in top_candidates
                    ]
                    for sr in scored:
                        sr.combined_score = sr.cross_encoder_score_normalized
                        sr.weight = sr.combined_score

                _ALL_CHANNELS = ("semantic", "bm25", "graph", "temporal")

                used_tokens = 0
                for scored_result in scored:
                    text = scored_result.retrieval.text
                    estimated = max(1, len(text.split()))
                    if max_tokens > 0 and used_tokens + estimated > max_tokens:
                        break

                    raw_ranks = scored_result.candidate.source_ranks
                    channel_ranks = (
                        {ch: raw_ranks.get(f"{ch}_rank") for ch in _ALL_CHANNELS}
                        if enable_trace
                        else None
                    )

                    reranked_results.append(
                        {
                            "id": scored_result.id,
                            "text": text,
                            "fact_type": scored_result.retrieval.fact_type,
                            "raw_snippet": scored_result.retrieval.raw_snippet,
                            "score": float(scored_result.combined_score),
                            "cross_encoder_score": float(scored_result.cross_encoder_score),
                            "rrf_score": float(scored_result.candidate.rrf_score),
                            "rrf_rank": int(scored_result.candidate.rrf_rank),
                            "global_rrf_rank": global_rrf_rank_by_id.get(scored_result.id, 0),
                            "document_id": scored_result.candidate.retrieval.document_id,
                            "chunk_id": scored_result.candidate.retrieval.chunk_id,
                            "channel_ranks": channel_ranks,
                        }
                    )
                    used_tokens += estimated

            if top_k is not None:
                reranked_results = reranked_results[:top_k]

            if snippet_budget is not None:
                used_chars = 0
                seen_chunk_ids: set[str] = set()
                for item in reranked_results:
                    chunk_id = item.get("chunk_id") or item.get("document_id") or ""
                    snippet = item.get("raw_snippet") or ""
                    if chunk_id and chunk_id in seen_chunk_ids:
                        item["raw_snippet"] = None
                    elif used_chars + len(snippet) <= snippet_budget:
                        used_chars += len(snippet)
                        if chunk_id:
                            seen_chunk_ids.add(chunk_id)
                    else:
                        item["raw_snippet"] = None

            trace = None
            if enable_trace:
                trace = {
                    "query_type": retrieval_result.query_type,
                    "rrf_weights": retrieval_result.rrf_weights,
                    "fact_types": effective_types,
                    "timings": retrieval_result.timings,
                    "cross_encoder_ok": cross_encoder_ok,
                }

            return {"results": reranked_results, "trace": trace}
        except Exception as exc:
            logger.warning("Recall main path failed, using lexical fallback: %s", exc)
            fallback = await self._fallback_recall_from_conn(
                bank_id=bank_id,
                query=query,
                fact_types=effective_types,
                max_tokens=max_tokens,
                limit=max(thinking_budget // 10, 10),
            )
            trace = {"fallback": "lexical_db_scan"} if enable_trace else None
            return {"results": fallback, "trace": trace}

    async def list_banks(self) -> list[dict[str, Any]]:
        """Return all banks with memory unit counts."""
        if self._pool is None:
            raise RuntimeError("MemoryEngine is not connected.")
        async with acquire_with_retry(self._pool) as conn:
            rows = await conn.fetch(
                f"""
                SELECT b.bank_id,
                       COUNT(m.id) AS unit_count
                FROM {fq_table("banks")} b
                LEFT JOIN {fq_table("memory_units")} m ON m.bank_id = b.bank_id
                GROUP BY b.bank_id
                ORDER BY b.bank_id
                """
            )
        return [{"bank_id": r["bank_id"], "unit_count": r["unit_count"]} for r in rows]

    async def delete_bank(self, bank_id: str) -> dict[str, Any]:
        """Delete a bank and all its associated memory units, documents, and edges."""
        if self._pool is None:
            raise RuntimeError("MemoryEngine is not connected.")
        async with acquire_with_retry(self._pool) as conn:
            async with conn.transaction():
                # memory_edges and memory_unit_entities cascade from memory_units FK
                tag = await conn.execute(
                    f"DELETE FROM {fq_table('memory_units')} WHERE bank_id = $1",
                    bank_id,
                )
                units_deleted = int(tag.split()[-1]) if tag else 0
                await conn.execute(
                    f"DELETE FROM {fq_table('documents')} WHERE bank_id = $1",
                    bank_id,
                )
                deleted_bank = await conn.fetchval(
                    f"DELETE FROM {fq_table('banks')} WHERE bank_id = $1 RETURNING bank_id",
                    bank_id,
                )
        return {
            "bank_id": bank_id,
            "deleted": deleted_bank is not None,
            "units_deleted": units_deleted,
        }
