"""Fact persistence layer for the CogMem retain pipeline."""

from __future__ import annotations

import json
from datetime import UTC, datetime

from cogmem_api.engine.memory_engine import fq_table
from .types import ProcessedFact, coerce_fact_type

_DEFAULT_DISPOSITION = {"skepticism": 3, "literalism": 3, "empathy": 3}


def _event_date_for_fact(fact: ProcessedFact) -> datetime:
    return fact.occurred_start or fact.mentioned_at or datetime.now(UTC)


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
) -> list[str]:
    """Insert processed facts and return created memory unit IDs."""
    if not facts:
        return []

    if hasattr(conn, "insert_memory_units"):
        return await conn.insert_memory_units(bank_id, facts, document_id=document_id)

    unit_ids: list[str] = []
    for fact in facts:
        normalized_type = coerce_fact_type(fact.fact_type)
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
                metadata
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
                $14::jsonb
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
        )
        unit_ids.append(created)

    return unit_ids
