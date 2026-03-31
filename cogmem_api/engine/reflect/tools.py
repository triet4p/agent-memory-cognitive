"""Utility helpers for converting retrieval output into reflect evidence."""

from __future__ import annotations

from collections import defaultdict
from datetime import datetime
from typing import Any

from cogmem_api.engine.search.types import MergedCandidate, RetrievalResult

from .models import ReflectEvidence

_SUPPORTED_FACT_TYPES = {"world", "experience", "opinion", "habit", "intention", "action_effect"}


def _coerce_score(payload: dict[str, Any]) -> float:
    for key in ("rrf_score", "similarity", "activation", "temporal_score", "bm25_score", "score"):
        value = payload.get(key)
        if isinstance(value, (float, int)):
            return float(value)
    return 0.0


def _coerce_datetime(payload: dict[str, Any]) -> datetime | None:
    value = payload.get("event_date") or payload.get("occurred_start") or payload.get("mentioned_at")
    if isinstance(value, datetime):
        return value
    return None


def _normalize_payload(item: RetrievalResult | MergedCandidate | dict[str, Any], source: str | None) -> dict[str, Any]:
    if isinstance(item, MergedCandidate):
        payload = {
            "id": item.retrieval.id,
            "text": item.retrieval.text,
            "fact_type": item.retrieval.fact_type,
            "raw_snippet": item.retrieval.raw_snippet,
            "event_date": item.retrieval.event_date,
            "rrf_score": item.rrf_score,
        }
        payload["source"] = source or "rrf"
        return payload

    if isinstance(item, RetrievalResult):
        payload = {
            "id": item.id,
            "text": item.text,
            "fact_type": item.fact_type,
            "raw_snippet": item.raw_snippet,
            "event_date": item.event_date,
            "similarity": item.similarity,
            "activation": item.activation,
            "temporal_score": item.temporal_score,
            "bm25_score": item.bm25_score,
        }
        payload["source"] = source or "retrieval"
        return payload

    payload = dict(item)
    payload["source"] = source or str(payload.get("source") or "dict")
    return payload


def to_reflect_evidence(
    item: RetrievalResult | MergedCandidate | dict[str, Any],
    source: str | None = None,
) -> ReflectEvidence | None:
    """Convert retrieval outputs into a validated ReflectEvidence object."""
    payload = _normalize_payload(item, source)
    fact_type = str(payload.get("fact_type") or "").strip()
    if fact_type not in _SUPPORTED_FACT_TYPES:
        return None

    memory_id = str(payload.get("id") or "").strip()
    text = str(payload.get("text") or "").strip()
    if not memory_id or not text:
        return None

    raw_snippet = payload.get("raw_snippet")
    if raw_snippet is not None:
        raw_snippet = str(raw_snippet)

    return ReflectEvidence(
        id=memory_id,
        fact_type=fact_type,
        text=text,
        raw_snippet=raw_snippet,
        source=str(payload.get("source") or "unknown"),
        score=_coerce_score(payload),
        event_date=_coerce_datetime(payload),
    )


def prepare_lazy_evidence(
    items: list[RetrievalResult | MergedCandidate | dict[str, Any]],
    max_items: int = 8,
) -> list[ReflectEvidence]:
    """Prepare deduplicated, score-sorted evidence for lazy synthesis."""
    by_id: dict[str, ReflectEvidence] = {}

    for item in items:
        evidence = to_reflect_evidence(item)
        if evidence is None:
            continue

        existing = by_id.get(evidence.id)
        if existing is None or evidence.score > existing.score:
            by_id[evidence.id] = evidence

    ranked = sorted(
        by_id.values(),
        key=lambda e: (e.score, e.event_date.timestamp() if e.event_date is not None else float("-inf")),
        reverse=True,
    )

    return ranked[: max(1, max_items)]


def group_evidence_by_network(evidences: list[ReflectEvidence]) -> dict[str, list[ReflectEvidence]]:
    """Group evidence by CogMem memory network for network-aware summaries."""
    grouped: dict[str, list[ReflectEvidence]] = defaultdict(list)
    for evidence in evidences:
        grouped[evidence.fact_type].append(evidence)

    return dict(grouped)
