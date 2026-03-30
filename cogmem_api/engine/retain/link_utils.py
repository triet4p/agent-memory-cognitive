"""Utility functions for memory link creation in retain pipeline."""

from __future__ import annotations

import math
from datetime import datetime, timedelta

from ..memory_engine import fq_table

# Link tuple format:
# (from_unit_id, to_unit_id, link_type, transition_type, entity_id, weight)
LinkRecord = tuple[str, str, str, str | None, str | None, float]


def cosine_similarity(vec_a: list[float], vec_b: list[float]) -> float:
    """Compute cosine similarity with defensive numeric handling."""
    if not vec_a or not vec_b or len(vec_a) != len(vec_b):
        return 0.0

    dot = sum(a * b for a, b in zip(vec_a, vec_b))
    norm_a = math.sqrt(sum(a * a for a in vec_a))
    norm_b = math.sqrt(sum(b * b for b in vec_b))
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot / (norm_a * norm_b)


def build_temporal_links(unit_dates: dict[str, datetime], window_hours: int = 24) -> list[LinkRecord]:
    """Create bidirectional temporal links for close timestamps."""
    links: list[LinkRecord] = []
    if len(unit_dates) < 2:
        return links

    items = list(unit_dates.items())
    window = timedelta(hours=window_hours)

    for i, (left_id, left_date) in enumerate(items):
        for right_id, right_date in items[i + 1 :]:
            delta = abs(left_date - right_date)
            if delta > window:
                continue

            weight = max(0.3, 1.0 - (delta.total_seconds() / window.total_seconds()))
            links.append((left_id, right_id, "temporal", None, None, weight))
            links.append((right_id, left_id, "temporal", None, None, weight))

    return links


def build_semantic_links(unit_ids: list[str], embeddings: list[list[float]], threshold: float = 0.75) -> list[LinkRecord]:
    """Create directed semantic links for similar pairs within a batch."""
    links: list[LinkRecord] = []
    if len(unit_ids) < 2:
        return links

    for i, source_id in enumerate(unit_ids):
        for j, target_id in enumerate(unit_ids):
            if i == j:
                continue
            score = cosine_similarity(embeddings[i], embeddings[j])
            if score >= threshold:
                links.append((source_id, target_id, "semantic", None, None, float(score)))

    return links


async def insert_links(conn, links: list[LinkRecord]) -> int:
    """Persist links via fake-connection hook or SQL insert path."""
    if not links:
        return 0

    if hasattr(conn, "insert_memory_links"):
        await conn.insert_memory_links(links)
        return len(links)

    await conn.executemany(
        f"""
        INSERT INTO {fq_table("memory_links")}
            (from_unit_id, to_unit_id, link_type, transition_type, entity_id, weight)
        VALUES
            ($1::uuid, $2::uuid, $3, $4, $5::uuid, $6)
        ON CONFLICT
            (from_unit_id, to_unit_id, link_type, COALESCE(entity_id, '00000000-0000-0000-0000-000000000000'::uuid))
        DO NOTHING
        """,
        links,
    )
    return len(links)


async def fetch_event_dates(conn, unit_ids: list[str]) -> dict[str, datetime]:
    """Fetch event dates for a list of units."""
    if not unit_ids:
        return {}

    if hasattr(conn, "get_unit_event_dates"):
        return await conn.get_unit_event_dates(unit_ids)

    rows = await conn.fetch(
        f"""
        SELECT id::text AS id, event_date
        FROM {fq_table("memory_units")}
        WHERE id::text = ANY($1)
        """,
        unit_ids,
    )
    return {str(row["id"]): row["event_date"] for row in rows if row["event_date"] is not None}
