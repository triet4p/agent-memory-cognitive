"""Type definitions for the CogMem retain pipeline."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any, TypedDict


COGMEM_FACT_TYPES: tuple[str, ...] = (
    "world",
    "experience",
    "opinion",
    "habit",
    "intention",
    "action_effect",
)

ALLOWED_INTENTION_STATUSES: set[str] = {"planning", "fulfilled", "abandoned"}

# Typed transition edge rules from CogMem design.
# Value is (source_fact_type, target_fact_type).
TRANSITION_EDGE_RULES: dict[str, tuple[str, str]] = {
    "fulfilled_by": ("intention", "experience"),
    "triggered": ("experience", "intention"),
    "enabled_by": ("intention", "intention"),
    "revised_to": ("opinion", "opinion"),
    "contradicted_by": ("world", "world"),
}


def coerce_fact_type(raw: str | None) -> str:
    """Normalize a source fact type into CogMem-supported network/fact types."""
    if not raw:
        return "world"

    lowered = raw.strip().lower()
    if lowered == "assistant":
        return "experience"
    if lowered in COGMEM_FACT_TYPES:
        return lowered
    if lowered == "observation":
        return "world"
    return "world"


def clamp_relation_strength(value: Any, default: float = 1.0) -> float:
    """Clamp relation strength to [0.0, 1.0] with defensive parsing."""
    try:
        numeric = float(value)
    except (TypeError, ValueError):
        numeric = default
    return max(0.0, min(1.0, numeric))


def normalize_intention_status(value: Any) -> str | None:
    """Normalize intention status to CogMem-supported values."""
    if value is None:
        return None
    if not isinstance(value, str):
        return None
    normalized = value.strip().lower()
    if not normalized:
        return None
    if normalized in ALLOWED_INTENTION_STATUSES:
        return normalized
    return None


def _normalize_bool(value: Any, default: bool) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        normalized = value.strip().lower()
        if normalized in {"1", "true", "yes", "y", "on"}:
            return True
        if normalized in {"0", "false", "no", "n", "off"}:
            return False
        return default
    return bool(value) if value is not None else default


def sanitize_raw_snippet(raw_snippet: str | None, fact_text: str) -> str:
    """Keep a non-empty lossless raw snippet for storage and downstream synthesis."""
    if isinstance(raw_snippet, str) and raw_snippet.strip():
        return raw_snippet
    return fact_text


class RetainFactSeed(TypedDict, total=False):
    """Optional pre-extracted fact payload used to bypass LLM extraction in tests/smoke runs."""

    text: str
    fact_type: str
    entities: list[str] | list[dict[str, str]]
    causal_relations: list[dict[str, object]]
    action_effect_relations: list[dict[str, object]]
    transition_relations: list[dict[str, object]]
    intention_status: str
    precondition: str
    action: str
    outcome: str
    confidence: float
    devalue_sensitive: bool


class RetainContentDict(TypedDict, total=False):
    """Input item format consumed by retain_batch."""

    content: str
    context: str
    event_date: datetime | str | None
    metadata: dict[str, object]
    entities: list[dict[str, str]]
    tags: list[str]
    document_id: str
    facts: list[RetainFactSeed]


@dataclass(slots=True)
class RetainContent:
    """Single retain input item after normalization."""

    content: str
    context: str = ""
    event_date: datetime | None = None
    metadata: dict[str, object] = field(default_factory=dict)
    entities: list[dict[str, str]] = field(default_factory=list)
    tags: list[str] = field(default_factory=list)
    document_id: str | None = None
    facts: list[RetainFactSeed] = field(default_factory=list)

    @staticmethod
    def from_dict(payload: RetainContentDict) -> "RetainContent":
        event_date = payload.get("event_date")
        parsed_event_date: datetime | None

        if isinstance(event_date, datetime):
            parsed_event_date = event_date if event_date.tzinfo else event_date.replace(tzinfo=UTC)
        elif isinstance(event_date, str):
            dt = datetime.fromisoformat(event_date.replace("Z", "+00:00"))
            parsed_event_date = dt if dt.tzinfo else dt.replace(tzinfo=UTC)
        elif event_date is None:
            parsed_event_date = None
        else:
            raise TypeError(f"Unsupported event_date type: {type(event_date).__name__}")

        return RetainContent(
            content=payload.get("content", ""),
            context=payload.get("context", ""),
            event_date=parsed_event_date,
            metadata=dict(payload.get("metadata", {})),
            entities=list(payload.get("entities", [])),
            tags=list(payload.get("tags", [])),
            document_id=payload.get("document_id"),
            facts=list(payload.get("facts", [])),
        )


@dataclass(slots=True)
class ChunkMetadata:
    """Chunk metadata used for tracing and chunk-id mapping."""

    chunk_text: str
    fact_count: int
    content_index: int
    chunk_index: int


@dataclass(slots=True)
class CausalRelation:
    """Causal relation between two facts in a single retain batch."""

    target_fact_index: int
    relation_type: str = "caused_by"
    strength: float = 1.0


@dataclass(slots=True)
class ActionEffectRelation:
    """A-O causal relation between an action_effect fact and another fact."""

    target_fact_index: int
    relation_type: str = "a_o_causal"
    strength: float = 1.0


@dataclass(slots=True)
class TransitionRelation:
    """Lifecycle transition between facts in a single retain batch."""

    target_fact_index: int | None = None
    transition_type: str = "fulfilled_by"
    strength: float = 1.0


def _build_edge_intent_payload(
    causal_relations: list[CausalRelation],
    action_effect_relations: list[ActionEffectRelation],
    transition_relations: list[TransitionRelation],
) -> dict[str, list[dict[str, Any]]]:
    return {
        "causal": [
            {
                "target_fact_index": relation.target_fact_index,
                "relation_type": str(relation.relation_type or "caused_by").strip().lower() or "caused_by",
                "strength": clamp_relation_strength(relation.strength),
            }
            for relation in causal_relations
        ],
        "action_effect": [
            {
                "target_fact_index": relation.target_fact_index,
                "relation_type": "a_o_causal",
                "strength": clamp_relation_strength(relation.strength),
            }
            for relation in action_effect_relations
        ],
        "transition": [
            {
                "target_fact_index": relation.target_fact_index,
                "transition_type": str(relation.transition_type or "").strip().lower(),
                "strength": clamp_relation_strength(relation.strength),
            }
            for relation in transition_relations
        ],
    }


def normalize_fact_metadata(
    metadata: dict[str, object],
    *,
    fact_type: str,
    raw_snippet: str,
    causal_relations: list[CausalRelation],
    action_effect_relations: list[ActionEffectRelation],
    transition_relations: list[TransitionRelation],
) -> dict[str, object]:
    """Normalize metadata payload for stable retain behavior across ingestion paths."""
    normalized = dict(metadata)

    normalized["edge_intent"] = _build_edge_intent_payload(
        causal_relations=causal_relations,
        action_effect_relations=action_effect_relations,
        transition_relations=transition_relations,
    )

    # Keep trace-level signal that raw verbatim context exists in storage path.
    normalized["raw_snippet_present"] = bool(raw_snippet.strip())

    if fact_type == "intention":
        status = normalize_intention_status(normalized.get("intention_status"))
        normalized["intention_status"] = status or "planning"

    if fact_type == "action_effect":
        normalized["confidence"] = clamp_relation_strength(normalized.get("confidence"), default=0.85)
        normalized["devalue_sensitive"] = _normalize_bool(normalized.get("devalue_sensitive"), default=True)

    return normalized


@dataclass(slots=True)
class ExtractedFact:
    """Fact emitted by extraction step before embeddings/storage."""

    fact_text: str
    fact_type: str
    entities: list[str] = field(default_factory=list)
    occurred_start: datetime | None = None
    occurred_end: datetime | None = None
    mentioned_at: datetime | None = None
    context: str = ""
    metadata: dict[str, object] = field(default_factory=dict)
    content_index: int = 0
    chunk_index: int = 0
    causal_relations: list[CausalRelation] = field(default_factory=list)
    action_effect_relations: list[ActionEffectRelation] = field(default_factory=list)
    transition_relations: list[TransitionRelation] = field(default_factory=list)
    raw_snippet: str | None = None


@dataclass(slots=True)
class ProcessedFact:
    """Fact ready to store in DB after embedding generation."""

    fact_text: str
    fact_type: str
    embedding: list[float]
    occurred_start: datetime | None
    occurred_end: datetime | None
    mentioned_at: datetime | None
    context: str
    metadata: dict[str, object]
    entities: list[str] = field(default_factory=list)
    content_index: int = 0
    causal_relations: list[CausalRelation] = field(default_factory=list)
    action_effect_relations: list[ActionEffectRelation] = field(default_factory=list)
    transition_relations: list[TransitionRelation] = field(default_factory=list)
    raw_snippet: str | None = None
    document_id: str | None = None
    chunk_id: str | None = None

    @staticmethod
    def from_extracted_fact(extracted_fact: ExtractedFact, embedding: list[float]) -> "ProcessedFact":
        normalized_fact_type = coerce_fact_type(extracted_fact.fact_type)
        normalized_raw_snippet = sanitize_raw_snippet(extracted_fact.raw_snippet, extracted_fact.fact_text)

        normalized_causal_relations = [
            CausalRelation(
                target_fact_index=relation.target_fact_index,
                relation_type=str(relation.relation_type or "caused_by").strip().lower() or "caused_by",
                strength=clamp_relation_strength(relation.strength),
            )
            for relation in extracted_fact.causal_relations
        ]
        normalized_action_effect_relations = [
            ActionEffectRelation(
                target_fact_index=relation.target_fact_index,
                relation_type="a_o_causal",
                strength=clamp_relation_strength(relation.strength),
            )
            for relation in extracted_fact.action_effect_relations
        ]
        normalized_transition_relations = [
            TransitionRelation(
                target_fact_index=relation.target_fact_index,
                transition_type=str(relation.transition_type or "").strip().lower(),
                strength=clamp_relation_strength(relation.strength),
            )
            for relation in extracted_fact.transition_relations
            if str(relation.transition_type or "").strip()
        ]

        normalized_metadata = normalize_fact_metadata(
            extracted_fact.metadata,
            fact_type=normalized_fact_type,
            raw_snippet=normalized_raw_snippet,
            causal_relations=normalized_causal_relations,
            action_effect_relations=normalized_action_effect_relations,
            transition_relations=normalized_transition_relations,
        )

        return ProcessedFact(
            fact_text=extracted_fact.fact_text,
            fact_type=normalized_fact_type,
            embedding=embedding,
            occurred_start=extracted_fact.occurred_start,
            occurred_end=extracted_fact.occurred_end,
            mentioned_at=extracted_fact.mentioned_at,
            context=extracted_fact.context,
            metadata=normalized_metadata,
            entities=list(extracted_fact.entities),
            content_index=extracted_fact.content_index,
            causal_relations=normalized_causal_relations,
            action_effect_relations=normalized_action_effect_relations,
            transition_relations=normalized_transition_relations,
            raw_snippet=normalized_raw_snippet,
        )


@dataclass(slots=True)
class EntityLink:
    """Entity-driven graph link between two memory units."""

    from_unit_id: str
    to_unit_id: str
    entity_id: str
    link_type: str = "entity"
    weight: float = 1.0
