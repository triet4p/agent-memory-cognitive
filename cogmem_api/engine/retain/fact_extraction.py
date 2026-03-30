"""Fact extraction for CogMem retain pipeline.

This baseline module supports two modes:
1) Seeded facts supplied in input payload (`facts` key)
2) Simple sentence fallback extraction when no seeded facts exist
"""

from __future__ import annotations

import re
from datetime import UTC, datetime

from ..response_models import TokenUsage
from .types import CausalRelation, ChunkMetadata, ExtractedFact, RetainContent, coerce_fact_type


def _safe_datetime(value: datetime | None) -> datetime | None:
    if value is None:
        return None
    return value if value.tzinfo else value.replace(tzinfo=UTC)


def _extract_entities(raw_entities) -> list[str]:
    entities: list[str] = []
    if not raw_entities:
        return entities

    for entry in raw_entities:
        if isinstance(entry, str) and entry.strip():
            entities.append(entry.strip())
        elif isinstance(entry, dict):
            text = str(entry.get("text", "")).strip()
            if text:
                entities.append(text)

    # Preserve order while de-duplicating.
    seen: set[str] = set()
    deduped: list[str] = []
    for entity in entities:
        lowered = entity.lower()
        if lowered not in seen:
            seen.add(lowered)
            deduped.append(entity)
    return deduped


def _extract_causal_relations(raw_relations) -> list[CausalRelation]:
    relations: list[CausalRelation] = []
    if not raw_relations:
        return relations

    for relation in raw_relations:
        if not isinstance(relation, dict):
            continue
        if "target_fact_index" not in relation:
            continue

        target = relation.get("target_fact_index")
        if not isinstance(target, int):
            continue

        strength = relation.get("strength", 1.0)
        try:
            numeric_strength = float(strength)
        except (TypeError, ValueError):
            numeric_strength = 1.0

        relations.append(
            CausalRelation(
                target_fact_index=target,
                relation_type=str(relation.get("relation_type", "caused_by")),
                strength=max(0.0, min(1.0, numeric_strength)),
            )
        )

    return relations


def _fallback_fact_splits(text: str) -> list[str]:
    candidates = [segment.strip() for segment in re.split(r"[.!?]\s+", text) if segment.strip()]
    if not candidates and text.strip():
        return [text.strip()]
    return candidates[:3]


async def extract_facts_from_contents(
    contents: list[RetainContent],
    llm_config,
    agent_name: str,
    config,
    pool=None,
    operation_id: str | None = None,
    schema: str | None = None,
) -> tuple[list[ExtractedFact], list[ChunkMetadata], TokenUsage]:
    """Extract facts from normalized retain content list.

    This baseline implementation does not call LLM directly; it consumes seeded
    facts when available and falls back to sentence-based extraction.
    """
    extracted: list[ExtractedFact] = []
    chunks: list[ChunkMetadata] = []

    for content_index, content in enumerate(contents):
        seeded_facts = list(content.facts)

        if seeded_facts:
            fact_count = 0
            for payload in seeded_facts:
                fact_text = str(payload.get("text") or payload.get("fact") or payload.get("what") or "").strip()
                if not fact_text:
                    continue

                extracted.append(
                    ExtractedFact(
                        fact_text=fact_text,
                        fact_type=coerce_fact_type(str(payload.get("fact_type", "world"))),
                        entities=_extract_entities(payload.get("entities")),
                        occurred_start=_safe_datetime(content.event_date),
                        occurred_end=_safe_datetime(content.event_date),
                        mentioned_at=_safe_datetime(content.event_date),
                        context=content.context,
                        metadata=content.metadata,
                        content_index=content_index,
                        chunk_index=content_index,
                        causal_relations=_extract_causal_relations(payload.get("causal_relations")),
                        raw_snippet=content.content,
                    )
                )
                fact_count += 1

            chunks.append(
                ChunkMetadata(
                    chunk_text=content.content,
                    fact_count=fact_count,
                    content_index=content_index,
                    chunk_index=content_index,
                )
            )
            continue

        fallback_segments = _fallback_fact_splits(content.content)
        for segment in fallback_segments:
            extracted.append(
                ExtractedFact(
                    fact_text=segment,
                    fact_type="world",
                    entities=_extract_entities(content.entities),
                    occurred_start=_safe_datetime(content.event_date),
                    occurred_end=_safe_datetime(content.event_date),
                    mentioned_at=_safe_datetime(content.event_date),
                    context=content.context,
                    metadata=content.metadata,
                    content_index=content_index,
                    chunk_index=content_index,
                    raw_snippet=content.content,
                )
            )

        chunks.append(
            ChunkMetadata(
                chunk_text=content.content,
                fact_count=len(fallback_segments),
                content_index=content_index,
                chunk_index=content_index,
            )
        )

    return extracted, chunks, TokenUsage()
