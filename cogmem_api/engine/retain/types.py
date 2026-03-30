"""Type definitions for the CogMem retain pipeline."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import TypedDict


COGMEM_FACT_TYPES: tuple[str, ...] = (
    "world",
    "experience",
    "opinion",
    "habit",
    "intention",
    "action_effect",
)


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
        return ProcessedFact(
            fact_text=extracted_fact.fact_text,
            fact_type=coerce_fact_type(extracted_fact.fact_type),
            embedding=embedding,
            occurred_start=extracted_fact.occurred_start,
            occurred_end=extracted_fact.occurred_end,
            mentioned_at=extracted_fact.mentioned_at,
            context=extracted_fact.context,
            metadata=extracted_fact.metadata,
            entities=list(extracted_fact.entities),
            content_index=extracted_fact.content_index,
            causal_relations=list(extracted_fact.causal_relations),
            action_effect_relations=list(extracted_fact.action_effect_relations),
            transition_relations=list(extracted_fact.transition_relations),
            raw_snippet=extracted_fact.raw_snippet,
        )


@dataclass(slots=True)
class EntityLink:
    """Entity-driven graph link between two memory units."""

    from_unit_id: str
    to_unit_id: str
    entity_id: str
    link_type: str = "entity"
    weight: float = 1.0
