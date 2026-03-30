"""Fact extraction for CogMem retain pipeline.

This baseline module supports two modes:
1) Seeded facts supplied in input payload (`facts` key)
2) Simple sentence fallback extraction when no seeded facts exist
"""

from __future__ import annotations

import re
from datetime import UTC, datetime

from ..response_models import TokenUsage
from .types import (
    ActionEffectRelation,
    CausalRelation,
    ChunkMetadata,
    ExtractedFact,
    RetainContent,
    TransitionRelation,
    coerce_fact_type,
)


_HABIT_PATTERNS: tuple[str, ...] = (
    r"\balways\b",
    r"\busually\b",
    r"\boften\b",
    r"\bevery\s+(day|morning|evening|night|week|weekday|weekend)\b",
    r"\btends\s+to\b",
    r"\broutine\b",
    r"\bhabit\b",
)

_ACTION_EFFECT_PATTERNS: tuple[str, ...] = (
    r"\b(if|when)\b.+\b(then|so)\b",
    r"\b(resulted in|led to|caused|therefore)\b",
    r"\b(precondition|outcome)\b",
)

_SUPPORTED_TRANSITION_TYPES: set[str] = {
    "fulfilled_by",
    "abandoned",
    "triggered",
    "enabled_by",
    "revised_to",
    "contradicted_by",
}


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


def _extract_entities_from_text(text: str) -> list[str]:
    """Lightweight fallback NER for title-cased names when no entities are provided."""
    candidates = re.findall(r"\b[A-Z][a-z]{2,}\b", text)
    if not candidates:
        return []

    blocked = {"The", "This", "That", "When", "Then", "Because", "User", "Assistant"}
    return [candidate for candidate in candidates if candidate not in blocked]


def _infer_fact_type(segment: str, default_fact_type: str = "world") -> str:
    """Classify fallback segments into CogMem fact types using lightweight heuristics."""
    lowered = segment.lower()

    for pattern in _ACTION_EFFECT_PATTERNS:
        if re.search(pattern, lowered):
            return "action_effect"

    for pattern in _HABIT_PATTERNS:
        if re.search(pattern, lowered):
            return "habit"
    return default_fact_type


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


def _extract_action_effect_relations(raw_relations) -> list[ActionEffectRelation]:
    relations: list[ActionEffectRelation] = []
    if not raw_relations:
        return relations

    for relation in raw_relations:
        if not isinstance(relation, dict):
            continue

        target = relation.get("target_fact_index")
        if not isinstance(target, int):
            continue

        strength_raw = relation.get("strength", 1.0)
        try:
            strength = float(strength_raw)
        except (TypeError, ValueError):
            strength = 1.0

        relation_type = str(relation.get("relation_type", "a_o_causal")).strip().lower()
        if relation_type != "a_o_causal":
            relation_type = "a_o_causal"

        relations.append(
            ActionEffectRelation(
                target_fact_index=target,
                relation_type=relation_type,
                strength=max(0.0, min(1.0, strength)),
            )
        )

    return relations


def _parse_action_effect_triplet(text: str) -> tuple[str, str, str] | None:
    """Extract precondition/action/outcome from causal utterances."""
    normalized = " ".join(text.split())

    pattern = re.compile(
        r"(?i)(?:if|when)\s+(?P<pre>[^,.;]+),\s*(?P<act>[^,.;]+?)\s*(?:,\s*)?(?:so|then|therefore|which led to|leading to|resulting in)\s+(?P<out>[^.;]+)"
    )
    match = pattern.search(normalized)
    if match:
        pre = match.group("pre").strip()
        act = match.group("act").strip()
        out = match.group("out").strip()
        if pre and act and out:
            return pre, act, out

    pattern2 = re.compile(
        r"(?i)(?P<act>[^,.;]+?)\s+(?:resulted in|led to|caused)\s+(?P<out>[^.;]+)"
    )
    match2 = pattern2.search(normalized)
    if match2:
        act = match2.group("act").strip()
        out = match2.group("out").strip()
        if act and out:
            return "N/A", act, out

    return None


def _extract_transition_relations(raw_relations) -> list[TransitionRelation]:
    relations: list[TransitionRelation] = []
    if not raw_relations:
        return relations

    for relation in raw_relations:
        if not isinstance(relation, dict):
            continue

        transition_type = str(relation.get("transition_type", "")).strip().lower()
        if transition_type not in _SUPPORTED_TRANSITION_TYPES:
            continue

        target_idx_raw = relation.get("target_fact_index")
        target_idx: int | None
        if isinstance(target_idx_raw, int):
            target_idx = target_idx_raw
        else:
            target_idx = None

        strength_raw = relation.get("strength", 1.0)
        try:
            strength = float(strength_raw)
        except (TypeError, ValueError):
            strength = 1.0

        relations.append(
            TransitionRelation(
                target_fact_index=target_idx,
                transition_type=transition_type,
                strength=max(0.0, min(1.0, strength)),
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

                requested_type = str(payload.get("fact_type", "")).strip() if payload.get("fact_type") else ""
                if requested_type:
                    inferred_fact_type = coerce_fact_type(requested_type)
                else:
                    inferred_fact_type = _infer_fact_type(fact_text)

                fact_metadata = dict(content.metadata)
                intention_status = payload.get("intention_status")
                if intention_status is not None:
                    fact_metadata["intention_status"] = str(intention_status)

                action_effect_relations = _extract_action_effect_relations(payload.get("action_effect_relations"))

                if inferred_fact_type == "action_effect":
                    precondition = str(payload.get("precondition", "")).strip()
                    action = str(payload.get("action", "")).strip()
                    outcome = str(payload.get("outcome", "")).strip()

                    if not (precondition and action and outcome):
                        parsed_triplet = _parse_action_effect_triplet(fact_text)
                        if parsed_triplet is not None:
                            precondition, action, outcome = parsed_triplet

                    if precondition and action and outcome:
                        fact_metadata["precondition"] = precondition
                        fact_metadata["action"] = action
                        fact_metadata["outcome"] = outcome

                    confidence_raw = payload.get("confidence", 0.85)
                    try:
                        confidence = float(confidence_raw)
                    except (TypeError, ValueError):
                        confidence = 0.85
                    fact_metadata["confidence"] = max(0.0, min(1.0, confidence))

                    devalue_raw = payload.get("devalue_sensitive", True)
                    if isinstance(devalue_raw, bool):
                        devalue_sensitive = devalue_raw
                    elif isinstance(devalue_raw, str):
                        devalue_sensitive = devalue_raw.strip().lower() in {"1", "true", "yes", "y"}
                    else:
                        devalue_sensitive = bool(devalue_raw)
                    fact_metadata["devalue_sensitive"] = devalue_sensitive

                payload_entities = _extract_entities(payload.get("entities"))
                if not payload_entities:
                    payload_entities = _extract_entities(content.entities)
                if not payload_entities:
                    payload_entities = _extract_entities_from_text(fact_text)

                extracted.append(
                    ExtractedFact(
                        fact_text=fact_text,
                        fact_type=inferred_fact_type,
                        entities=payload_entities,
                        occurred_start=_safe_datetime(content.event_date),
                        occurred_end=_safe_datetime(content.event_date),
                        mentioned_at=_safe_datetime(content.event_date),
                        context=content.context,
                        metadata=fact_metadata,
                        content_index=content_index,
                        chunk_index=content_index,
                        causal_relations=_extract_causal_relations(payload.get("causal_relations")),
                        action_effect_relations=action_effect_relations,
                        transition_relations=_extract_transition_relations(payload.get("transition_relations")),
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
        fallback_entities = _extract_entities(content.entities)
        if not fallback_entities:
            fallback_entities = _extract_entities_from_text(content.content)

        for segment in fallback_segments:
            fact_type = _infer_fact_type(segment)
            fallback_metadata = dict(content.metadata)

            if fact_type == "action_effect":
                parsed_triplet = _parse_action_effect_triplet(segment)
                if parsed_triplet is not None:
                    precondition, action, outcome = parsed_triplet
                    fallback_metadata["precondition"] = precondition
                    fallback_metadata["action"] = action
                    fallback_metadata["outcome"] = outcome
                fallback_metadata["confidence"] = 0.8
                fallback_metadata["devalue_sensitive"] = True

            extracted.append(
                ExtractedFact(
                    fact_text=segment,
                    fact_type=fact_type,
                    entities=fallback_entities,
                    occurred_start=_safe_datetime(content.event_date),
                    occurred_end=_safe_datetime(content.event_date),
                    mentioned_at=_safe_datetime(content.event_date),
                    context=content.context,
                    metadata=fallback_metadata,
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
