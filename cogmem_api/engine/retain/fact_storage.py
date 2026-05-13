"""Fact persistence layer for the CogMem retain pipeline."""

from __future__ import annotations

import json
from datetime import UTC, datetime

from cogmem_api.engine.memory_engine import fq_table
from .types import ProcessedFact, coerce_fact_type, normalize_fact_metadata, sanitize_raw_snippet

_DEFAULT_DISPOSITION = {"skepticism": 3, "literalism": 3, "empathy": 3}


def _event_date_for_fact(fact: ProcessedFact) -> datetime:
    return fact.occurred_start or fact.mentioned_at or datetime.now(UTC)


def _prepare_fact_for_storage(fact: ProcessedFact) -> ProcessedFact:
    normalized_type = coerce_fact_type(fact.fact_type)
    normalized_raw_snippet = sanitize_raw_snippet(fact.raw_snippet, fact.fact_text)
    normalized_metadata = normalize_fact_metadata(
        fact.metadata,
        fact_type=normalized_type,
        raw_snippet=normalized_raw_snippet,
        causal_relations=fact.causal_relations,
        action_effect_relations=fact.action_effect_relations,
        transition_relations=fact.transition_relations,
    )

    fact.fact_type = normalized_type
    fact.raw_snippet = normalized_raw_snippet
    fact.metadata = normalized_metadata
    return fact


async def ensure_bank_exists(conn, bank_id: str) -> None:
    """Ensure bank row exists before writing memory units."""
    if hasattr(conn, "ensure_bank_exists"):
        await conn.ensure_bank_exists(bank_id)
        return

    await conn.execute(
        f"""
        INSERT INTO {fq_table("banks")} (bank_id, disposition, background)
        VALUES ($1, $2::jsonb, $3)
        ON CONFLICT (bank_id) DO NOTHING
        """,
        bank_id,
        json.dumps(_DEFAULT_DISPOSITION),
        "",
    )


async def insert_facts_batch(
    conn,
    bank_id: str,
    facts: list[ProcessedFact],
    document_id: str | None = None,
    document_tags: list[str] | None = None,
) -> list[str]:
    """Insert processed facts and return created memory unit IDs."""
    if not facts:
        return []

    prepared_facts = [_prepare_fact_for_storage(fact) for fact in facts]

    if hasattr(conn, "insert_memory_units"):
        return await conn.insert_memory_units(bank_id, prepared_facts, document_id=document_id, document_tags=document_tags)

    # Upsert document records first so FK on memory_units.document_id is satisfied
    unique_doc_ids = {f.document_id for f in prepared_facts if f.document_id}
    if document_id:
        unique_doc_ids.add(document_id)
    if unique_doc_ids:
        await conn.executemany(
            f"INSERT INTO {fq_table('documents')} (id, bank_id) VALUES ($1, $2) ON CONFLICT DO NOTHING",
            [(doc_id, bank_id) for doc_id in unique_doc_ids],
        )

    unit_ids: list[str] = []
    for fact in prepared_facts:
        normalized_type = fact.fact_type
        confidence_score = 1.0 if normalized_type == "opinion" else None

        created = await conn.fetchval(
            f"""
            INSERT INTO {fq_table("memory_units")}
            (
                bank_id,
                document_id,
                chunk_id,
                text,
                raw_snippet,
                embedding,
                context,
                event_date,
                occurred_start,
                occurred_end,
                mentioned_at,
                fact_type,
                network_type,
                confidence_score,
                metadata,
                tags
            )
            VALUES
            (
                $1,
                $2,
                $3,
                $4,
                $5,
                $6::vector,
                $7,
                $8,
                $9,
                $10,
                $11,
                $12,
                $13,
                $14,
                $15::jsonb,
                $16::text[]
            )
            RETURNING id::text
            """,
            bank_id,
            fact.document_id if fact.document_id else document_id,
            fact.chunk_id,
            fact.fact_text,
            fact.raw_snippet,
            str(fact.embedding),
            fact.context,
            _event_date_for_fact(fact),
            fact.occurred_start,
            fact.occurred_end,
            fact.mentioned_at,
            normalized_type,
            normalized_type,
            confidence_score,
            json.dumps(fact.metadata),
            document_tags or None,
        )
        unit_ids.append(created)

    return unit_ids


async def get_facts(
    conn,
    bank_id: str,
    *,
    keyword: str | None = None,
    fact_type: str | None = None,
    document_id: str | None = None,
    limit: int = 100,
    offset: int = 0,
) -> list[dict[str, Any]]:
    """Query memory units by keyword (text search), fact_type, and/or document_id filter."""
    conditions = ["bank_id = $1"]
    params: list[Any] = [bank_id]
    param_idx = 2

    if keyword:
        conditions.append(f"text ILIKE ${param_idx}")
        params.append(f"%{keyword}%")
        param_idx += 1

    if fact_type:
        conditions.append(f"fact_type = ${param_idx}")
        params.append(fact_type)
        param_idx += 1

    if document_id:
        conditions.append(f"document_id = ${param_idx}")
        params.append(document_id)
        param_idx += 1

    params.extend([limit, offset])
    query = f"""
        SELECT id::text, text, fact_type, raw_snippet, context,
               occurred_start, occurred_end, mentioned_at, event_date,
               chunk_id, document_id, metadata, tags, embedding
        FROM {fq_table("memory_units")}
        WHERE {' AND '.join(conditions)}
        ORDER BY event_date DESC NULLS LAST
        LIMIT ${param_idx} OFFSET ${param_idx + 1}
    """
    rows = await conn.fetch(query, *params)
    return [_row_to_fact_dict(row) for row in rows]


async def get_all_facts(
    conn,
    bank_id: str,
    *,
    limit: int = 100,
    offset: int = 0,
) -> list[dict[str, Any]]:
    """Get all memory units for a bank with pagination."""
    query = f"""
        SELECT id::text, text, fact_type, raw_snippet, context,
               occurred_start, occurred_end, mentioned_at, event_date,
               chunk_id, document_id, metadata, tags, embedding
        FROM {fq_table("memory_units")}
        WHERE bank_id = $1
        ORDER BY event_date DESC NULLS LAST
        LIMIT $2 OFFSET $3
    """
    rows = await conn.fetch(query, bank_id, limit, offset)
    return [_row_to_fact_dict(row) for row in rows]


async def get_relationships(
    conn,
    bank_id: str,
    *,
    limit: int = 100,
    offset: int = 0,
) -> list[dict[str, Any]]:
    """Get all memory_links for a bank with pagination."""
    query = f"""
        SELECT ml.from_unit_id::text, ml.to_unit_id::text, ml.link_type,
               ml.transition_type, ml.weight,
               mu_from.text AS from_text, mu_from.fact_type AS from_fact_type,
               mu_to.text AS to_text, mu_to.fact_type AS to_fact_type
        FROM {fq_table("memory_links")} ml
        JOIN {fq_table("memory_units")} mu_from ON mu_from.id = ml.from_unit_id
        JOIN {fq_table("memory_units")} mu_to ON mu_to.id = ml.to_unit_id
        WHERE mu_from.bank_id = $1 AND mu_to.bank_id = $1
        ORDER BY ml.link_type, ml.weight DESC
        LIMIT $2 OFFSET $3
    """
    rows = await conn.fetch(query, bank_id, limit, offset)
    return [_row_to_link_dict(row) for row in rows]


async def get_relationships_by_type(
    conn,
    bank_id: str,
    link_type: str,
    *,
    limit: int = 100,
    offset: int = 0,
) -> list[dict[str, Any]]:
    """Get memory_links filtered by link_type for a bank."""
    query = f"""
        SELECT ml.from_unit_id::text, ml.to_unit_id::text, ml.link_type,
               ml.transition_type, ml.weight,
               mu_from.text AS from_text, mu_from.fact_type AS from_fact_type,
               mu_to.text AS to_text, mu_to.fact_type AS to_fact_type
        FROM {fq_table("memory_links")} ml
        JOIN {fq_table("memory_units")} mu_from ON mu_from.id = ml.from_unit_id
        JOIN {fq_table("memory_units")} mu_to ON mu_to.id = ml.to_unit_id
        WHERE mu_from.bank_id = $1 AND mu_to.bank_id = $1 AND ml.link_type = $2
        ORDER BY ml.weight DESC
        LIMIT $3 OFFSET $4
    """
    rows = await conn.fetch(query, bank_id, link_type, limit, offset)
    return [_row_to_link_dict(row) for row in rows]


def _row_to_fact_dict(row) -> dict[str, Any]:
    return {
        "id": row["id"],
        "text": row["text"],
        "fact_type": row["fact_type"],
        "raw_snippet": row["raw_snippet"],
        "context": row["context"],
        "occurred_start": row["occurred_start"].isoformat() if row["occurred_start"] else None,
        "occurred_end": row["occurred_end"].isoformat() if row["occurred_end"] else None,
        "mentioned_at": row["mentioned_at"].isoformat() if row["mentioned_at"] else None,
        "event_date": row["event_date"].isoformat() if row["event_date"] else None,
        "chunk_id": row["chunk_id"],
        "document_id": row["document_id"],
        "metadata": row["metadata"],
        "tags": row["tags"] or [],
        "embedding": row["embedding"],
    }


async def search_relationships(
    conn,
    bank_id: str,
    *,
    keyword: str | None = None,
    link_type: str | None = None,
    from_fact_type: str | None = None,
    to_fact_type: str | None = None,
    limit: int = 200,
    offset: int = 0,
) -> list[dict[str, Any]]:
    """Search memory_links with optional filters on keyword, link_type, and fact_types.

    keyword: substring matched (case-insensitive) against from_text OR to_text.
    link_type: exact match on ml.link_type (entity, semantic, causal, temporal, s_r_link, a_o_causal, transition).
    from_fact_type: exact match on source fact type.
    to_fact_type: exact match on target fact type.
    """
    conditions = ["mu_from.bank_id = $1", "mu_to.bank_id = $1"]
    params: list = [bank_id]

    if link_type:
        params.append(link_type)
        conditions.append(f"ml.link_type = ${len(params)}")

    if from_fact_type:
        params.append(from_fact_type)
        conditions.append(f"mu_from.fact_type = ${len(params)}")

    if to_fact_type:
        params.append(to_fact_type)
        conditions.append(f"mu_to.fact_type = ${len(params)}")

    if keyword:
        params.append(f"%{keyword}%")
        idx = len(params)
        conditions.append(
            f"(mu_from.text ILIKE ${idx} OR mu_to.text ILIKE ${idx}"
            f" OR mu_from.document_id ILIKE ${idx} OR mu_to.document_id ILIKE ${idx})"
        )

    where = " AND ".join(conditions)
    params += [limit, offset]
    lim_idx = len(params) - 1
    off_idx = len(params)

    query = f"""
        SELECT ml.from_unit_id::text, ml.to_unit_id::text, ml.link_type,
               ml.transition_type, ml.weight,
               mu_from.text AS from_text, mu_from.fact_type AS from_fact_type,
               mu_from.document_id AS from_document_id,
               mu_to.text AS to_text, mu_to.fact_type AS to_fact_type,
               mu_to.document_id AS to_document_id
        FROM {fq_table("memory_links")} ml
        JOIN {fq_table("memory_units")} mu_from ON mu_from.id = ml.from_unit_id
        JOIN {fq_table("memory_units")} mu_to ON mu_to.id = ml.to_unit_id
        WHERE {where}
        ORDER BY ml.weight DESC
        LIMIT ${lim_idx} OFFSET ${off_idx}
    """
    rows = await conn.fetch(query, *params)
    return [_row_to_link_dict_extended(row) for row in rows]


def _row_to_link_dict_extended(row) -> dict[str, Any]:
    return {
        "from_unit_id": row["from_unit_id"],
        "from_document_id": row.get("from_document_id"),
        "from_fact_type": row["from_fact_type"],
        "from_text": row["from_text"],
        "to_unit_id": row["to_unit_id"],
        "to_document_id": row.get("to_document_id"),
        "to_fact_type": row["to_fact_type"],
        "to_text": row["to_text"],
        "link_type": row["link_type"],
        "transition_type": row["transition_type"],
        "weight": float(row["weight"]) if row["weight"] is not None else None,
    }


def _row_to_link_dict(row) -> dict[str, Any]:
    return {
        "from_unit_id": row["from_unit_id"],
        "to_unit_id": row["to_unit_id"],
        "link_type": row["link_type"],
        "transition_type": row["transition_type"],
        "weight": float(row["weight"]) if row["weight"] is not None else None,
        "from_text": row["from_text"],
        "from_fact_type": row["from_fact_type"],
        "to_text": row["to_text"],
        "to_fact_type": row["to_fact_type"],
    }
