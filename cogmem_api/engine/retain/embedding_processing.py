"""Embedding orchestration utilities for retain pipeline."""

from __future__ import annotations

from datetime import datetime

from . import embedding_utils
from .types import ExtractedFact


def augment_texts_with_dates(facts: list[ExtractedFact], format_date_fn) -> list[str]:
    """Inject readable time hints into fact text prior to embedding."""
    augmented: list[str] = []
    for fact in facts:
        base = fact.fact_text
        anchor = fact.occurred_start or fact.mentioned_at
        if isinstance(anchor, datetime):
            base = f"{base} (time: {format_date_fn(anchor)})"

        if fact.entities:
            entities_repr = ", ".join(fact.entities)
            base = f"{base} [entities: {entities_repr}]"

        augmented.append(base)
    return augmented


async def generate_embeddings_batch(embeddings_model, texts: list[str]) -> list[list[float]]:
    """Generate embeddings for all augmented texts."""
    return await embedding_utils.generate_embeddings_batch(embeddings_model, texts)
