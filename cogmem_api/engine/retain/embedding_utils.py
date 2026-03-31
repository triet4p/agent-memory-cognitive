"""Embedding helper functions for retain pipeline."""

from __future__ import annotations

import hashlib
import math
from collections.abc import Sequence

from cogmem_api.config import EMBEDDING_DIMENSION


def _deterministic_embedding(text: str, dimension: int) -> list[float]:
    """Create a stable embedding vector without external model dependencies."""
    if dimension <= 0:
        return []

    vector = [0.0] * dimension
    if not text:
        return vector

    for token in text.split():
        digest = hashlib.sha256(token.encode("utf-8")).digest()
        slot = int.from_bytes(digest[:4], "big") % dimension
        raw = int.from_bytes(digest[4:8], "big") / 0xFFFFFFFF
        vector[slot] += raw

    norm = math.sqrt(sum(v * v for v in vector))
    if norm == 0:
        return vector
    return [v / norm for v in vector]


async def generate_embeddings_batch(embeddings_model, texts: list[str], dimension: int | None = None) -> list[list[float]]:
    """Generate embeddings using a provided model or fallback deterministic encoder."""
    target_dim = dimension or EMBEDDING_DIMENSION
    if not texts:
        return []

    if embeddings_model is not None and hasattr(embeddings_model, "encode"):
        raw = embeddings_model.encode(texts)
        if isinstance(raw, Sequence):
            return [list(map(float, row)) for row in raw]

    return [_deterministic_embedding(text, target_dim) for text in texts]
