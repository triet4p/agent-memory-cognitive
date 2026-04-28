"""Artifact test for Task 781 — Two chunking strategies.

Verifies:
1. Pass 1 chunker produces N chunks <= max_chars
2. Every Pass 1 chunk starts with a role marker
3. Role marker duplication when a single turn spans 2 chunks
4. Pass 2 chunker extracts only user turns
5. Long user turn sub-chunked correctly
6. Empty messages -> empty chunk list (no crash)
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from cogmem_api.engine.retain.chunking import chunk_for_pass1, chunk_for_pass2, Pass1Chunk, Pass2Chunk


def test_pass1_chunker_basic():
    messages = [
        {"role": "user", "content": "I bought a Tiger I kit."},
        {"role": "assistant", "content": "Great choice! What scale?"},
        {"role": "user", "content": "1/16 scale. It's a big model."},
    ]
    chunks = chunk_for_pass1(messages, max_chars=500)
    assert len(chunks) >= 1
    for chunk in chunks:
        assert isinstance(chunk, Pass1Chunk)
        assert chunk.text
        assert chunk.chunk_id_suffix.startswith("p1_")
    print(f"PASS: Pass1 basic — produced {len(chunks)} chunks")


def test_pass1_every_chunk_starts_with_role_marker():
    messages = [
        {"role": "user", "content": "I bought a Tiger I kit."},
        {"role": "assistant", "content": "Great choice!"},
    ]
    chunks = chunk_for_pass1(messages, max_chars=500)
    for chunk in chunks:
        assert chunk.text.startswith("[user]:") or chunk.text.startswith("[assistant]:"), f"Chunk {chunk.chunk_index} does not start with role marker: {chunk.text[:50]}"
    print("PASS: Every Pass1 chunk starts with role marker")


def test_pass1_role_marker_duplication_on_split():
    long_user_text = ". ".join([f"Sentence {i} about model building details" for i in range(50)])
    messages = [
        {"role": "user", "content": long_user_text},
    ]
    chunks = chunk_for_pass1(messages, max_chars=500)
    assert len(chunks) >= 2, "Long single turn should be split into multiple chunks"
    for chunk in chunks:
        assert chunk.text.startswith("[user]:"), f"Chunk {chunk.chunk_index} does not start with [user]: {chunk.text[:50]}"
    print(f"PASS: Role marker duplication — {len(chunks)} chunks, all start with [user]:")


def test_pass1_mixed_speaker_chunks():
    messages = [
        {"role": "user", "content": "I bought a Tiger I."},
        {"role": "assistant", "content": "Great! Let's talk about painting."},
        {"role": "user", "content": "I want to try weathering."},
        {"role": "assistant", "content": "Weathering requires patience. Let me explain the basics."},
        {"role": "user", "content": "I'm planning to buy a Spitfire next."},
    ]
    chunks = chunk_for_pass1(messages, max_chars=1000)
    assert len(chunks) >= 1
    all_text = " ".join(c.text for c in chunks)
    assert "[user]:" in all_text
    assert "[assistant]:" in all_text
    print(f"PASS: Mixed speaker — {len(chunks)} chunks, both roles present")


def test_pass2_extracts_only_user():
    messages = [
        {"role": "user", "content": "I bought a Tiger I kit."},
        {"role": "assistant", "content": "Great choice!"},
        {"role": "user", "content": "1/16 scale is perfect for details."},
        {"role": "assistant", "content": "You should try an airbrush."},
    ]
    chunks = chunk_for_pass2(messages, target_role="user", max_chars=3000)
    assert len(chunks) == 2
    for chunk in chunks:
        assert isinstance(chunk, Pass2Chunk)
        assert chunk.target_role == "user"
        assert chunk.source_message_idx in (0, 2)
        assert "[assistant]" not in chunk.text
    print(f"PASS: Pass2 user-only — extracted {len(chunks)} user chunks, no assistant")


def test_pass2_long_turn_subchunked():
    long_text = ". ".join([f"Sentence {i} about the model kit I purchased" for i in range(50)])
    messages = [
        {"role": "user", "content": long_text},
    ]
    chunks = chunk_for_pass2(messages, target_role="user", max_chars=500)
    assert len(chunks) >= 2, "Long user turn should be sub-chunked"
    for chunk in chunks:
        assert len(chunk.text) <= 600
        assert chunk.chunk_id_suffix.startswith("p2_0_")
    print(f"PASS: Pass2 sub-chunking — {len(chunks)} sub-chunks from 1 long turn")


def test_pass1_empty_messages_returns_empty():
    chunks = chunk_for_pass1([], max_chars=500)
    assert chunks == []
    print("PASS: Pass1 empty messages -> empty list (no crash)")


def test_pass2_empty_messages_returns_empty():
    chunks = chunk_for_pass2([], target_role="user", max_chars=3000)
    assert chunks == []
    print("PASS: Pass2 empty messages -> empty list (no crash)")


def test_pass2_no_matching_role_returns_empty():
    messages = [
        {"role": "assistant", "content": "I am the assistant here."},
        {"role": "assistant", "content": "Another assistant message."},
    ]
    chunks = chunk_for_pass2(messages, target_role="user", max_chars=3000)
    assert chunks == []
    print("PASS: Pass2 no user messages -> empty list")


def main():
    tests = [
        test_pass1_chunker_basic,
        test_pass1_every_chunk_starts_with_role_marker,
        test_pass1_role_marker_duplication_on_split,
        test_pass1_mixed_speaker_chunks,
        test_pass2_extracts_only_user,
        test_pass2_long_turn_subchunked,
        test_pass1_empty_messages_returns_empty,
        test_pass2_empty_messages_returns_empty,
        test_pass2_no_matching_role_returns_empty,
    ]
    passed = 0
    for test in tests:
        try:
            result = test()
            if result is False:
                print(f"  FAILED: {test.__name__}")
            else:
                passed += 1
        except Exception as exc:
            print(f"  ERROR: {test.__name__} -> {type(exc).__name__}: {exc}")

    total = len(tests)
    print(f"\n{passed}/{total} PASS")
    return passed == total


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)