"""FastAPI application factory and runtime routes for CogMem."""

from __future__ import annotations

from contextlib import asynccontextmanager
from datetime import datetime
from typing import Any, Literal

from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel, ConfigDict, Field, field_validator

from cogmem_api import MemoryEngine, __version__
from cogmem_api.engine import eval_helpers


class HealthResponse(BaseModel):
    """Health response payload for readiness and liveness probes."""

    status: str
    initialized: bool
    database: dict[str, Any]
    reason: str | None = None


class VersionResponse(BaseModel):
    """Version metadata for diagnostics."""

    version: str
    service: str


class MessageInput(BaseModel):
    """Single message in a structured conversation format."""

    role: str
    content: str


class EntityInput(BaseModel):
    """Entity attached to a retained memory item."""

    text: str
    type: str | None = None


class RetainItem(BaseModel):
    """Single retain item accepted by retain endpoint."""

    model_config = ConfigDict(populate_by_name=True)

    content: str | None = None
    messages: list[MessageInput] | None = None
    timestamp: datetime | str | None = None
    context: str | None = None
    metadata: dict[str, str] | None = None
    document_id: str | None = None
    entities: list[EntityInput] | None = None
    tags: list[str] | None = None

    def model_post_init(self, __context) -> None:
        has_content = bool(self.content and self.content.strip())
        has_messages = bool(self.messages and len(self.messages) > 0)
        if not has_content and not has_messages:
            raise ValueError("At least one of 'content' or 'messages' must be non-empty")


class RetainRequest(BaseModel):
    """Retain request payload."""

    model_config = ConfigDict(populate_by_name=True)

    items: list[RetainItem]
    async_: bool = Field(default=False, alias="async")


class RetainResponse(BaseModel):
    """Retain response payload."""

    success: bool
    bank_id: str
    items_count: int
    unit_ids: list[list[str]]


class RecallRequest(BaseModel):
    """Recall request payload."""

    query: str
    types: list[str] | None = None
    budget: Literal["low", "mid", "high"] = "mid"
    max_tokens: int = 4096
    top_k: int | None = None
    snippet_budget: int | None = None
    trace: bool = False
    query_timestamp: str | None = None
    adaptive_router: bool = True
    graph_retriever: str | None = None


class RecallResult(BaseModel):
    """Recall result payload entry."""

    id: str
    text: str
    type: str
    score: float = 0.0
    cross_encoder_score: float = 0.0
    rrf_score: float = 0.0
    rrf_rank: int = 0
    global_rrf_rank: int = 0
    raw_snippet: str | None = None
    document_id: str | None = None
    chunk_id: str | None = None
    channel_ranks: dict[str, int | None] | None = None


class RecallResponse(BaseModel):
    """Recall response payload."""

    results: list[RecallResult]
    trace: dict[str, Any] | None = None


class GenerateRequest(BaseModel):
    """Request payload for generation endpoint."""

    query: str
    evidence: list[dict]
    max_tokens: int = 2048


class GenerateResponse(BaseModel):
    """Response payload for generation endpoint."""

    answer: str


class JudgeRequest(BaseModel):
    """Request payload for judge endpoint."""

    question: str
    gold_answer: str
    predicted_answer: str
    category: str | None = None

    @field_validator("gold_answer", "predicted_answer", "question", mode="before")
    @classmethod
    def _coerce_str(cls, v: object) -> str:
        return str(v) if v is not None else ""


class JudgeResponse(BaseModel):
    """Response payload for judge endpoint."""

    correct: bool
    score: float
    reason: str
    raw: str


class BankInfo(BaseModel):
    """Summary info for a single bank."""

    bank_id: str
    unit_count: int


class DeleteBankResponse(BaseModel):
    """Response for bank deletion."""

    bank_id: str
    deleted: bool
    units_deleted: int


def _parse_query_timestamp(value: str | None) -> datetime | None:
    if value is None:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=f"Invalid query_timestamp: {exc}") from exc


def _derive_content_from_messages(messages: list[MessageInput]) -> str:
    """Render structured messages as a plain text string for backward compat."""
    parts = []
    for msg in messages:
        role_marker = f"[{msg.role}]: " if msg.role else ""
        parts.append(f"{role_marker}{msg.content}")
    return "\n\n".join(parts)


def _build_retain_payload(item: RetainItem) -> dict[str, Any] | None:
    if item.messages:
        content = _derive_content_from_messages(item.messages)
    else:
        content = item.content.strip() if item.content else ""

    if not content:
        return None

    payload: dict[str, Any] = {"content": content}
    if item.messages:
        payload["messages"] = [{"role": m.role, "content": m.content} for m in item.messages]
    if item.context:
        payload["context"] = item.context
    if item.timestamp is not None:
        payload["event_date"] = item.timestamp
    if item.metadata:
        payload["metadata"] = item.metadata
    if item.document_id:
        payload["document_id"] = item.document_id
    if item.entities:
        payload["entities"] = [
            {"text": entity.text, "type": entity.type or "CONCEPT"}
            for entity in item.entities
            if entity.text.strip()
        ]
    if item.tags:
        payload["tags"] = [tag for tag in item.tags if tag.strip()]
    return payload


def create_app(
    memory: MemoryEngine,
    initialize_memory: bool = True,
) -> FastAPI:
    """Create and configure the FastAPI application."""

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        app.state.memory = memory
        if initialize_memory:
            await memory.initialize()
        try:
            yield
        finally:
            await memory.close()

    app = FastAPI(
        title="CogMem HTTP API",
        version=__version__,
        description="HTTP API for CogMem",
        lifespan=lifespan,
    )

    app.state.memory = memory

    @app.get(
        "/health",
        response_model=HealthResponse,
        summary="Health check endpoint",
        description="Checks the health of the API and database connectivity.",
        tags=["Monitoring"],
    )
    async def health_endpoint() -> JSONResponse:
        health = await app.state.memory.health_check()
        status_code = 200 if health.get("status") == "healthy" else 503
        return JSONResponse(content=health, status_code=status_code)

    @app.get(
        "/version",
        response_model=VersionResponse,
        summary="Version endpoint",
        description="Returns service and package version.",
        tags=["Monitoring"],
    )
    async def version_endpoint() -> VersionResponse:
        return VersionResponse(version=__version__, service="cogmem-api")

    @app.get(
        "/v1/banks",
        response_model=list[BankInfo],
        summary="List all banks",
        description="Returns all memory banks with their unit counts.",
        operation_id="list_banks",
        tags=["Memory"],
    )
    async def list_banks() -> list[BankInfo]:
        try:
            banks = await app.state.memory.list_banks()
            return [BankInfo(**b) for b in banks]
        except RuntimeError as exc:
            raise HTTPException(status_code=503, detail=str(exc)) from exc

    @app.delete(
        "/v1/default/banks/{bank_id}",
        response_model=DeleteBankResponse,
        summary="Delete a bank",
        description="Deletes a bank and all its memory units, documents, and edges.",
        operation_id="delete_bank",
        tags=["Memory"],
    )
    async def delete_bank(bank_id: str) -> DeleteBankResponse:
        try:
            result = await app.state.memory.delete_bank(bank_id)
            return DeleteBankResponse(**result)
        except RuntimeError as exc:
            raise HTTPException(status_code=503, detail=str(exc)) from exc

    @app.post(
        "/v1/default/banks/{bank_id}/memories",
        response_model=RetainResponse,
        summary="Retain memories",
        description="Stores memory items using CogMem retain_batch runtime path.",
        operation_id="retain_memories",
        tags=["Memory"],
    )
    async def retain_memories(bank_id: str, payload: RetainRequest) -> RetainResponse:
        contents = [candidate for candidate in (_build_retain_payload(item) for item in payload.items) if candidate]
        if not contents:
            return RetainResponse(success=True, bank_id=bank_id, items_count=0, unit_ids=[])

        if payload.async_:
            raise HTTPException(status_code=400, detail="Async retain is not available in CogMem runtime yet.")

        try:
            unit_ids = await app.state.memory.retain_batch_async(bank_id=bank_id, contents=contents)
            return RetainResponse(success=True, bank_id=bank_id, items_count=len(contents), unit_ids=unit_ids)
        except RuntimeError as exc:
            raise HTTPException(status_code=503, detail=str(exc)) from exc

    @app.post(
        "/v1/default/banks/{bank_id}/memories/recall",
        response_model=RecallResponse,
        summary="Recall memories",
        description="Recalls memories through CogMem recall stack.",
        operation_id="recall_memories",
        tags=["Memory"],
    )
    async def recall_memories(bank_id: str, payload: RecallRequest) -> RecallResponse:
        question_date = _parse_query_timestamp(payload.query_timestamp)

        try:
            recall_result = await app.state.memory.recall_async(
                bank_id=bank_id,
                query=payload.query,
                budget=payload.budget,
                max_tokens=payload.max_tokens,
                top_k=payload.top_k,
                snippet_budget=payload.snippet_budget,
                enable_trace=payload.trace,
                fact_types=payload.types,
                question_date=question_date,
                adaptive_router=payload.adaptive_router,
                graph_retriever_override=payload.graph_retriever,
            )
        except RuntimeError as exc:
            raise HTTPException(status_code=503, detail=str(exc)) from exc

        results = [
            RecallResult(
                id=str(item.get("id") or ""),
                text=str(item.get("text") or ""),
                type=str(item.get("fact_type") or "world"),
                score=float(item.get("score") or 0.0),
                cross_encoder_score=float(item.get("cross_encoder_score") or 0.0),
                rrf_score=float(item.get("rrf_score") or 0.0),
                rrf_rank=int(item.get("rrf_rank") or 0),
                global_rrf_rank=int(item.get("global_rrf_rank") or 0),
                raw_snippet=item.get("raw_snippet"),
                document_id=item.get("document_id"),
                chunk_id=item.get("chunk_id"),
                channel_ranks=item.get("channel_ranks"),
            )
            for item in recall_result.get("results", [])
            if item.get("id") and item.get("text")
        ]
        return RecallResponse(results=results, trace=recall_result.get("trace"))

    @app.post(
        "/v1/default/banks/{bank_id}/memories/generate",
        response_model=GenerateResponse,
        summary="Generate answer from recall evidence",
        description="Uses the generate LLM to produce a grounded answer from recall evidence.",
        operation_id="generate_answer",
        tags=["Memory"],
    )
    async def generate_answer(bank_id: str, payload: GenerateRequest) -> GenerateResponse:
        llm_config = app.state.memory._build_generate_llm_config()
        if llm_config is None:
            raise HTTPException(status_code=503, detail="Generate LLM not configured")

        prompt = eval_helpers.build_generation_prompt(payload.query, payload.evidence)
        messages = [{"role": "user", "content": prompt}]

        try:
            answer = await llm_config.call(
                messages=messages,
                temperature=0.1,
                max_completion_tokens=payload.max_tokens,
            )
            return GenerateResponse(answer=str(answer or ""))
        except Exception as exc:
            raise HTTPException(status_code=500, detail=str(exc)) from exc

    @app.post(
        "/v1/default/judge",
        response_model=JudgeResponse,
        summary="Judge predicted answer against gold answer",
        description="Uses a dedicated judge LLM to evaluate prediction quality.",
        operation_id="judge_answer",
        tags=["Evaluation"],
    )
    async def judge_answer(payload: JudgeRequest) -> JudgeResponse:
        if not app.state.memory._runtime_config.judge_llm_base_url:
            raise HTTPException(status_code=503, detail="Judge LLM not configured")

        llm_config = app.state.memory._build_judge_llm_config()
        if llm_config is None:
            raise HTTPException(status_code=503, detail="Judge LLM not available")

        system_prompt = eval_helpers.build_judge_system_prompt(payload.category)
        user_prompt = (
            f"Question: {payload.question}\n"
            f"Gold Answer: {payload.gold_answer}\n"
            f"Predicted Answer: {payload.predicted_answer}\n"
            "Return JSON only."
        )

        try:
            raw = await llm_config.call(
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=0.1,
                max_completion_tokens=40000,
            )
            parsed = eval_helpers.parse_judge_response(str(raw or "{}"))
            return JudgeResponse(
                correct=parsed.get("correct", False),
                score=float(parsed.get("score", 0.0)),
                reason=parsed.get("reason", ""),
                raw=parsed.get("raw", ""),
            )
        except Exception as exc:
            import logging as _logging
            _logging.getLogger(__name__).error(
                "Judge LLM call failed | type=%s | detail=%s | raw_response=%r",
                type(exc).__name__, exc,
                getattr(exc, "response_text", None) or getattr(exc, "response", None),
                exc_info=True,
            )
            raise HTTPException(status_code=500, detail=f"{type(exc).__name__}: {exc}") from exc

    @app.get(
        "/v1/default/banks/{bank_id}/facts",
        summary="List facts with optional filters",
        description="Returns memory units filtered by keyword and/or fact type, with pagination.",
        operation_id="list_facts",
        tags=["Memory"],
    )
    async def list_facts(
        bank_id: str,
        keyword: str | None = None,
        type: str | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> list[dict[str, Any]]:
        pool = app.state.memory.pool
        if pool is None:
            raise HTTPException(status_code=503, detail="Database pool not initialized")

        from cogmem_api.engine.db_utils import acquire_with_retry
        from cogmem_api.engine.retain.fact_storage import get_facts

        async with acquire_with_retry(pool) as conn:
            facts = await get_facts(
                conn,
                bank_id,
                keyword=keyword,
                fact_type=type,
                limit=limit,
                offset=offset,
            )
        return facts

    @app.get(
        "/v1/default/banks/{bank_id}/facts/all",
        summary="List all facts (paginated)",
        description="Returns all memory units for a bank with limit/offset pagination.",
        operation_id="list_all_facts",
        tags=["Memory"],
    )
    async def list_all_facts(
        bank_id: str,
        limit: int = 100,
        offset: int = 0,
    ) -> list[dict[str, Any]]:
        pool = app.state.memory.pool
        if pool is None:
            raise HTTPException(status_code=503, detail="Database pool not initialized")

        from cogmem_api.engine.db_utils import acquire_with_retry
        from cogmem_api.engine.retain.fact_storage import get_all_facts

        async with acquire_with_retry(pool) as conn:
            facts = await get_all_facts(conn, bank_id, limit=limit, offset=offset)
        return facts

    @app.get(
        "/v1/default/banks/{bank_id}/relationships",
        summary="List all relationships (paginated)",
        description="Returns all memory links (relationships) for a bank with pagination.",
        operation_id="list_relationships",
        tags=["Memory"],
    )
    async def list_relationships(
        bank_id: str,
        limit: int = 100,
        offset: int = 0,
    ) -> list[dict[str, Any]]:
        pool = app.state.memory.pool
        if pool is None:
            raise HTTPException(status_code=503, detail="Database pool not initialized")

        from cogmem_api.engine.db_utils import acquire_with_retry
        from cogmem_api.engine.retain.fact_storage import get_relationships

        async with acquire_with_retry(pool) as conn:
            links = await get_relationships(conn, bank_id, limit=limit, offset=offset)
        return links

    @app.get(
        "/v1/default/banks/{bank_id}/relationships/by-type/{link_type}",
        summary="List relationships by type",
        description="Returns memory links filtered by link type (causal, semantic, temporal, entity, s_r_link, a_o_causal, transition).",
        operation_id="list_relationships_by_type",
        tags=["Memory"],
    )
    async def list_relationships_by_type(
        bank_id: str,
        link_type: str,
        limit: int = 100,
        offset: int = 0,
    ) -> list[dict[str, Any]]:
        pool = app.state.memory.pool
        if pool is None:
            raise HTTPException(status_code=503, detail="Database pool not initialized")

        from cogmem_api.engine.db_utils import acquire_with_retry
        from cogmem_api.engine.retain.fact_storage import get_relationships_by_type

        async with acquire_with_retry(pool) as conn:
            links = await get_relationships_by_type(conn, bank_id, link_type, limit=limit, offset=offset)
        return links

    return app
