"""Chunk storage helpers for retain pipeline."""

from __future__ import annotations

from .types import ChunkMetadata


async def store_chunks_batch(conn, bank_id: str, document_id: str, chunks: list[ChunkMetadata]) -> dict[int, str]:
    """Store chunk rows and return a map from chunk index to chunk id.

    For the baseline T2.1 flow, this function supports an in-memory testing path
    and a no-op DB fallback when chunk persistence is not required yet.
    """
    if not chunks:
        return {}

    if hasattr(conn, "insert_chunks"):
        return await conn.insert_chunks(bank_id, document_id, chunks)

    # Keep deterministic IDs even when we do not persist chunks yet.
    return {chunk.chunk_index: f"{bank_id}_{document_id}_{chunk.chunk_index}" for chunk in chunks}
