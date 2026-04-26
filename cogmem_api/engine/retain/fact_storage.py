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
                $5::vector,
                $6,
                $7,
                $8,
                $9,
                $10,
                $11,
                $12,
                $13,
                $14::jsonb,
                $15::text[]
            )
            RETURNING id::text
            """,
            bank_id,
            fact.document_id if fact.document_id else document_id,
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
