"""Fact extraction for CogMem retain pipeline.

Backfill B2 upgrades this module from seeded/fallback-only extraction to an
LLM-driven path with prompt parity across four modes:
- concise
- custom
- verbatim
- verbose

Seeded and heuristic fallback extraction are kept as safety paths for tests and
runtime resilience.
"""

from __future__ import annotations

import re
from datetime import UTC, datetime
from typing import Any

from cogmem_api.engine.llm_wrapper import OutputTooLongError, parse_llm_json
from cogmem_api.engine.response_models import TokenUsage
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

_ALLOWED_MODES: set[str] = {"concise", "custom", "verbatim", "verbose"}

_BASE_PROMPT = """Extract long-term memory facts for CogMem.

Return a JSON object with key `facts` containing a list of fact objects.
Each fact may include keys like:
- what, when, where, who, why
- fact_kind (event|conversation)
- fact_type (world|assistant|experience|opinion|habit|intention|action_effect)
- occurred_start, occurred_end
- entities (list of objects with `text` or list of strings)
- causal_relations (target_index, relation_type, strength)
- action_effect_relations (target_index, relation_type, strength)
- transition_relations (target_index, transition_type, strength)
- precondition, action, outcome, confidence, devalue_sensitive, intention_status

Language rule: output values in the same language as the input text.
{mission_section}
{mode_section}
"""

_CONCISE_MODE = """Mode: concise
- Extract only durable, memory-worthy facts.
- Skip filler and pleasantries.
- Keep each fact short and precise.
"""

_CUSTOM_MODE = """Mode: custom
- Follow custom extraction instructions below strictly.
{custom_instructions}
"""

_VERBATIM_MODE = """Mode: verbatim
- Return exactly one fact object per input chunk.
- Preserve raw text in storage path; output metadata only.
- Omit detailed rewriting; focus on entities and temporal metadata.
"""

_VERBOSE_MODE = """Mode: verbose
- Capture maximal detail for each fact.
- Include context and motivation in the `why` field.
- Prefer richer entity extraction.
"""


def _safe_datetime(value: datetime | None) -> datetime | None:
    if value is None:
        return None
    return value if value.tzinfo else value.replace(tzinfo=UTC)


def _parse_datetime(value: Any) -> datetime | None:
    if value is None:
        return None
    if isinstance(value, datetime):
        return _safe_datetime(value)
    if isinstance(value, str) and value.strip():
        try:
            parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
            return _safe_datetime(parsed)
        except ValueError:
            return None
    return None


def _extract_entities(raw_entities: Any) -> list[str]:
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

    seen: set[str] = set()
    deduped: list[str] = []
    for entity in entities:
        lowered = entity.lower()
        if lowered not in seen:
            seen.add(lowered)
            deduped.append(entity)
    return deduped


def _extract_entities_from_text(text: str) -> list[str]:
    candidates = re.findall(r"\b[A-Z][a-z]{2,}\b", text)
    if not candidates:
        return []
    blocked = {"The", "This", "That", "When", "Then", "Because", "User", "Assistant"}
    return [candidate for candidate in candidates if candidate not in blocked]


def _first_non_empty(payload: dict[str, Any], keys: list[str]) -> str:
    for key in keys:
        value = payload.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
    return ""


def _normalized_optional_text(value: Any) -> str | None:
    if not isinstance(value, str):
        return None
    normalized = value.strip()
    if not normalized:
        return None
    if normalized.upper() in {"N/A", "NONE", "NULL"}:
        return None
    return normalized


def _infer_fact_type(segment: str, default_fact_type: str = "world") -> str:
    lowered = segment.lower()

    for pattern in _ACTION_EFFECT_PATTERNS:
        if re.search(pattern, lowered):
            return "action_effect"

    for pattern in _HABIT_PATTERNS:
        if re.search(pattern, lowered):
            return "habit"
    return default_fact_type


def _extract_causal_relations(raw_relations: Any) -> list[CausalRelation]:
    relations: list[CausalRelation] = []
    if not raw_relations:
        return relations

    for relation in raw_relations:
        if not isinstance(relation, dict):
            continue

        target = relation.get("target_fact_index")
        if target is None:
            target = relation.get("target_index")
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


def _extract_action_effect_relations(raw_relations: Any) -> list[ActionEffectRelation]:
    relations: list[ActionEffectRelation] = []
    if not raw_relations:
        return relations

    for relation in raw_relations:
        if not isinstance(relation, dict):
            continue

        target = relation.get("target_fact_index")
        if target is None:
            target = relation.get("target_index")
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

    pattern2 = re.compile(r"(?i)(?P<act>[^,.;]+?)\s+(?:resulted in|led to|caused)\s+(?P<out>[^.;]+)")
    match2 = pattern2.search(normalized)
    if match2:
        act = match2.group("act").strip()
        out = match2.group("out").strip()
        if act and out:
            return "N/A", act, out

    return None


def _extract_transition_relations(raw_relations: Any) -> list[TransitionRelation]:
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
        if target_idx_raw is None:
            target_idx_raw = relation.get("target_index")

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


def _chunk_content(text: str, max_chars: int) -> list[str]:
    if max_chars <= 0 or len(text) <= max_chars:
        return [text]

    sentences = [segment.strip() for segment in re.split(r"(?<=[.!?])\s+", text) if segment.strip()]
    if not sentences:
        return [text]

    chunks: list[str] = []
    current: list[str] = []
    current_size = 0

    for sentence in sentences:
        sentence_size = len(sentence) + (1 if current else 0)
        if current and current_size + sentence_size > max_chars:
            chunks.append(" ".join(current))
            current = [sentence]
            current_size = len(sentence)
        else:
            current.append(sentence)
            current_size += sentence_size

    if current:
        chunks.append(" ".join(current))

    return chunks or [text]


def _build_prompt(config: Any) -> tuple[str, str]:
    mode = str(getattr(config, "retain_extraction_mode", "concise") or "concise").strip().lower()
    if mode not in _ALLOWED_MODES:
        mode = "concise"

    mission = _normalized_optional_text(getattr(config, "retain_mission", None))
    if mission:
        mission_section = f"\nMission:\n{mission}\n"
    else:
        mission_section = ""

    if mode == "custom":
        custom_instructions = _normalized_optional_text(getattr(config, "retain_custom_instructions", None))
        if not custom_instructions:
            mode_section = _CONCISE_MODE
            mode = "concise"
        else:
            mode_section = _CUSTOM_MODE.format(custom_instructions=custom_instructions)
    elif mode == "verbatim":
        mode_section = _VERBATIM_MODE
    elif mode == "verbose":
        mode_section = _VERBOSE_MODE
    else:
        mode_section = _CONCISE_MODE

    return _BASE_PROMPT.format(mission_section=mission_section, mode_section=mode_section), mode


def _build_user_message(
    chunk: str,
    chunk_index: int,
    total_chunks: int,
    event_date: datetime | None,
    context: str,
    metadata: dict[str, Any] | None,
) -> str:
    event_date_text = event_date.isoformat() if event_date else "unknown"
    metadata_text = ""
    if metadata:
        pairs = [f"{k}={v}" for k, v in metadata.items()]
        metadata_text = f"\nMetadata: {', '.join(pairs)}"

    return (
        "Extract facts from this chunk. "
        f"Chunk {chunk_index + 1}/{total_chunks}. "
        f"Event date: {event_date_text}. "
        f"Context: {context or 'none'}."
        f"{metadata_text}\n\n"
        f"Text:\n{chunk}"
    )


async def _call_llm_chunk(
    llm_config: Any,
    prompt: str,
    user_message: str,
    max_completion_tokens: int,
) -> tuple[list[dict[str, Any]], TokenUsage]:
    usage = TokenUsage()
    if llm_config is None or not hasattr(llm_config, "call"):
        return [], usage

    try:
        response = await llm_config.call(
            messages=[{"role": "system", "content": prompt}, {"role": "user", "content": user_message}],
            scope="retain_extract_facts",
            temperature=0.1,
            max_completion_tokens=max_completion_tokens,
            return_usage=True,
            skip_validation=True,
        )
    except TypeError:
        # Fallback for fake/minimal llm callers that do not support optional kwargs.
        response = await llm_config.call(
            messages=[{"role": "system", "content": prompt}, {"role": "user", "content": user_message}],
            scope="retain_extract_facts",
            temperature=0.1,
            max_completion_tokens=max_completion_tokens,
        )
    except OutputTooLongError:
        return [], usage
    except Exception:
        return [], usage

    payload: Any
    if isinstance(response, tuple) and len(response) == 2:
        payload, maybe_usage = response
        if isinstance(maybe_usage, TokenUsage):
            usage = maybe_usage
    else:
        payload = response

    if isinstance(payload, str):
        try:
            payload = parse_llm_json(payload)
        except Exception:
            return [], usage

    if not isinstance(payload, dict):
        return [], usage

    raw_facts = payload.get("facts")
    if not isinstance(raw_facts, list):
        return [], usage

    facts: list[dict[str, Any]] = [item for item in raw_facts if isinstance(item, dict)]
    return facts, usage


def _normalize_llm_facts(
    raw_facts: list[dict[str, Any]],
    content: RetainContent,
    content_index: int,
    chunk_index: int,
    mode: str,
    chunk_text: str,
) -> list[ExtractedFact]:
    normalized: list[ExtractedFact] = []

    for payload in raw_facts:
        if mode == "verbatim":
            fact_text = chunk_text.strip() or content.content.strip()
        else:
            what = _first_non_empty(payload, ["what", "fact", "factual_core", "text"])
            if not what:
                continue

            when = _normalized_optional_text(payload.get("when"))
            who = _normalized_optional_text(payload.get("who"))
            why = _normalized_optional_text(payload.get("why"))

            parts = [what]
            if when:
                parts.append(f"When: {when}")
            if who:
                parts.append(f"Involving: {who}")
            if why:
                parts.append(why)
            fact_text = " | ".join(parts)

        raw_fact_type = str(payload.get("fact_type", "")).strip().lower()
        if raw_fact_type == "assistant":
            raw_fact_type = "experience"
        if not raw_fact_type:
            raw_fact_type = _infer_fact_type(fact_text)
        fact_type = coerce_fact_type(raw_fact_type)

        fact_metadata = dict(content.metadata)
        if isinstance(payload.get("labels"), dict):
            fact_metadata["labels"] = payload["labels"]

        intention_status = payload.get("intention_status")
        if intention_status is not None:
            fact_metadata["intention_status"] = str(intention_status)

        action_effect_relations = _extract_action_effect_relations(payload.get("action_effect_relations"))

        if fact_type == "action_effect":
            precondition = _first_non_empty(payload, ["precondition"])
            action = _first_non_empty(payload, ["action"])
            outcome = _first_non_empty(payload, ["outcome"])

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

        fact_kind = str(payload.get("fact_kind", "conversation")).strip().lower()
        occurred_start = _parse_datetime(payload.get("occurred_start"))
        occurred_end = _parse_datetime(payload.get("occurred_end"))
        if fact_kind == "event" and occurred_start is None:
            occurred_start = _safe_datetime(content.event_date)
        if fact_kind == "event" and occurred_end is None:
            occurred_end = occurred_start

        normalized.append(
            ExtractedFact(
                fact_text=fact_text,
                fact_type=fact_type,
                entities=payload_entities,
                occurred_start=occurred_start,
                occurred_end=occurred_end,
                mentioned_at=_safe_datetime(content.event_date),
                context=content.context,
                metadata=fact_metadata,
                content_index=content_index,
                chunk_index=chunk_index,
                causal_relations=_extract_causal_relations(payload.get("causal_relations")),
                action_effect_relations=action_effect_relations,
                transition_relations=_extract_transition_relations(payload.get("transition_relations")),
                raw_snippet=content.content,
            )
        )

    if mode == "verbatim" and normalized:
        return [normalized[0]]
    return normalized


async def _extract_facts_with_llm(
    content: RetainContent,
    content_index: int,
    llm_config: Any,
    config: Any,
) -> tuple[list[ExtractedFact], list[ChunkMetadata], TokenUsage]:
    usage = TokenUsage()
    if llm_config is None or not hasattr(llm_config, "call"):
        return [], [], usage

    prompt, mode = _build_prompt(config)
    max_tokens = int(getattr(config, "retain_max_completion_tokens", 64000) or 64000)
    chunk_size = int(getattr(config, "retain_chunk_size", 3000) or 3000)
    content_chunks = _chunk_content(content.content, chunk_size)

    extracted: list[ExtractedFact] = []
    chunks: list[ChunkMetadata] = []

    for chunk_idx, chunk_text in enumerate(content_chunks):
        user_message = _build_user_message(
            chunk=chunk_text,
            chunk_index=chunk_idx,
            total_chunks=len(content_chunks),
            event_date=content.event_date,
            context=content.context,
            metadata=content.metadata,
        )
        raw_facts, chunk_usage = await _call_llm_chunk(
            llm_config=llm_config,
            prompt=prompt,
            user_message=user_message,
            max_completion_tokens=max_tokens,
        )
        usage = usage + chunk_usage

        parsed_facts = _normalize_llm_facts(
            raw_facts=raw_facts,
            content=content,
            content_index=content_index,
            chunk_index=chunk_idx,
            mode=mode,
            chunk_text=chunk_text,
        )
        extracted.extend(parsed_facts)

        chunks.append(
            ChunkMetadata(
                chunk_text=chunk_text,
                fact_count=len(parsed_facts),
                content_index=content_index,
                chunk_index=chunk_idx,
            )
        )

    return extracted, chunks, usage


def _extract_seeded_facts(content: RetainContent, content_index: int) -> tuple[list[ExtractedFact], ChunkMetadata]:
    extracted: list[ExtractedFact] = []
    fact_count = 0

    for payload in list(content.facts):
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

    chunk = ChunkMetadata(
        chunk_text=content.content,
        fact_count=fact_count,
        content_index=content_index,
        chunk_index=content_index,
    )
    return extracted, chunk


def _extract_fallback_facts(content: RetainContent, content_index: int) -> tuple[list[ExtractedFact], ChunkMetadata]:
    fallback_segments = _fallback_fact_splits(content.content)
    fallback_entities = _extract_entities(content.entities)
    if not fallback_entities:
        fallback_entities = _extract_entities_from_text(content.content)

    extracted: list[ExtractedFact] = []
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

    chunk = ChunkMetadata(
        chunk_text=content.content,
        fact_count=len(fallback_segments),
        content_index=content_index,
        chunk_index=content_index,
    )
    return extracted, chunk


async def extract_facts_from_contents(
    contents: list[RetainContent],
    llm_config,
    agent_name: str,
    config,
    pool=None,
    operation_id: str | None = None,
    schema: str | None = None,
) -> tuple[list[ExtractedFact], list[ChunkMetadata], TokenUsage]:
    """Extract facts from normalized retain content list."""
    del agent_name, pool, operation_id, schema

    extracted: list[ExtractedFact] = []
    chunks: list[ChunkMetadata] = []
    usage = TokenUsage()

    for content_index, content in enumerate(contents):
        if content.facts:
            seeded_facts, seeded_chunk = _extract_seeded_facts(content, content_index)
            extracted.extend(seeded_facts)
            chunks.append(seeded_chunk)
            continue

        llm_facts, llm_chunks, llm_usage = await _extract_facts_with_llm(
            content=content,
            content_index=content_index,
            llm_config=llm_config,
            config=config,
        )
        usage = usage + llm_usage

        if llm_facts:
            extracted.extend(llm_facts)
            chunks.extend(llm_chunks)
            continue

        fallback_facts, fallback_chunk = _extract_fallback_facts(content, content_index)
        extracted.extend(fallback_facts)
        chunks.append(fallback_chunk)

    return extracted, chunks, usage
