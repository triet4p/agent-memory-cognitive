"""Two-pass chunking strategies for retain pipeline.

Pass 1: sentence-split, pack into chunks ≤ max_chars, emit role markers
        at speaker boundaries (including when a turn spans multiple chunks).
Pass 2: filter by target_role, further sub-chunk if turn exceeds max_chars.

Used by fact_extraction.py to prepare chunks for 2-pass LLM extraction.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import NamedTuple


@dataclass(slots=True)
class Pass1Chunk:
    """A chunk prepared for Pass 1 LLM extraction (all fact types, wide context)."""

    text: str
    chunk_index: int
    chunk_id_suffix: str
    messages_covered: list[int]


@dataclass(slots=True)
class Pass2Chunk:
    """A chunk prepared for Pass 2 LLM extraction (user-only, persona-focused)."""

    text: str
    chunk_index: int
    sub_chunk_index: int
    chunk_id_suffix: str
    source_message_idx: int
    target_role: str


class RoleSegment(NamedTuple):
    """A sentence with its role marker and source message index."""

    role: str
    sentence: str
    msg_idx: int


def _sentence_split(text: str) -> list[str]:
    """Split text into sentences preserving period spacing."""
    sentences = re.split(r"(?<=[.!?])\s+", text)
    return [s.strip() for s in sentences if s.strip()]


def _render_chunk(segments: list[RoleSegment], is_first: bool) -> str:
    """Render a list of (role, sentence) into a chunk string with role markers.

    A role marker is emitted when:
    (a) it is the first segment of the chunk, OR
    (b) the role differs from the previous segment in this chunk.
    """
    parts = []
    prev_role: str | None = None
    for role, sentence, _ in segments:
        emit_marker = is_first or role != prev_role
        marker = f"[{role}]: " if emit_marker else ""
        parts.append(f"{marker}{sentence}")
        prev_role = role
        is_first = False
    return " ".join(parts)


def chunk_for_pass1(
    messages: list[dict[str, str]],
    max_chars: int = 10000,
) -> list[Pass1Chunk]:
    """Chunk messages for Pass 1 extraction (full mixed-speaker context).

    Sentence-split each message and pack sentences into chunks not exceeding
    max_chars. When a single turn exceeds max_chars, split mid-turn and emit
    the same role marker at the start of the next chunk (role marker duplication).

    Args:
        messages: List of {"role": str, "content": str} dicts, in order.
        max_chars: Maximum character length per chunk (default 10000).

    Returns:
        List of Pass1Chunk objects with rendered text and metadata.
    """
    if not messages:
        return []

    role_segments: list[tuple[str, int, str]] = []
    for msg_idx, msg in enumerate(messages):
        role = str(msg.get("role", "")).strip().lower()
        content = str(msg.get("content", "")).strip()
        if not content or not role:
            continue
        sentences = _sentence_split(content)
        for sentence in sentences:
            role_segments.append((role, msg_idx, sentence))

    if not role_segments:
        return []

    chunks: list[Pass1Chunk] = []
    current_segments: list[RoleSegment] = []
    current_size = 0
    chunk_index = 0
    covered_msg_indices: set[int] = set()

    def _finish_chunk() -> None:
        nonlocal chunk_index, current_segments, current_size, covered_msg_indices
        if not current_segments:
            return
        text = _render_chunk(current_segments, is_first=True)
        suffix = f"p1_{chunk_index}"
        chunks.append(
            Pass1Chunk(
                text=text,
                chunk_index=chunk_index,
                chunk_id_suffix=suffix,
                messages_covered=sorted(set(seg.msg_idx for seg in current_segments)),
            )
        )
        chunk_index += 1
        current_segments = []
        current_size = 0
        covered_msg_indices = set()

    for role, msg_idx, sentence in role_segments:
        sentence_size = len(sentence) + (1 if current_segments else 0)
        if current_segments and current_size + sentence_size > max_chars:
            _finish_chunk()

        current_segments.append(RoleSegment(role=role, sentence=sentence, msg_idx=msg_idx))
        current_size += sentence_size
        covered_msg_indices.add(msg_idx)

    _finish_chunk()

    return chunks


def chunk_for_pass2(
    messages: list[dict[str, str]],
    target_role: str = "user",
    max_chars: int = 3000,
) -> list[Pass2Chunk]:
    """Chunk messages for Pass 2 extraction (filtered by target role).

    Extract only turns matching target_role. If a turn exceeds max_chars,
    sentence-split and pack into sub-chunks.

    Args:
        messages: List of {"role": str, "content": str} dicts, in order.
        target_role: Role to filter on (default "user").
        max_chars: Maximum character length per sub-chunk (default 3000).

    Returns:
        List of Pass2Chunk objects with rendered text and metadata.
    """
    if not messages:
        return []

    target_lower = target_role.strip().lower()
    target_turns: list[tuple[int, str]] = []
    for msg_idx, msg in enumerate(messages):
        role = str(msg.get("role", "")).strip().lower()
        content = str(msg.get("content", "")).strip()
        if role == target_lower and content:
            target_turns.append((msg_idx, content))

    chunks: list[Pass2Chunk] = []

    for msg_idx, content in target_turns:
        sentences = _sentence_split(content)
        current_segments: list[str] = []
        current_size = 0
        sub_idx = 0

        def _finish_subchunk(msg_idx: int, sub_idx: int) -> None:
            nonlocal current_segments, current_size
            if not current_segments:
                return
            text = " ".join(current_segments)
            suffix = f"p2_{msg_idx}_{sub_idx}"
            chunks.append(
                Pass2Chunk(
                    text=text,
                    chunk_index=msg_idx,
                    sub_chunk_index=sub_idx,
                    chunk_id_suffix=suffix,
                    source_message_idx=msg_idx,
                    target_role=target_role,
                )
            )
            current_segments = []
            current_size = 0

        for sentence in sentences:
            sentence_size = len(sentence) + (1 if current_segments else 0)
            if current_segments and current_size + sentence_size > max_chars:
                _finish_subchunk(msg_idx, sub_idx)
                sub_idx += 1

            current_segments.append(sentence)
            current_size += sentence_size

        _finish_subchunk(msg_idx, sub_idx)

    return chunks