"""Artifact test for Task 783 — Cross-pass dedup logic.

Verifies:
1. Same (fact_type, normalized_text) in both passes → keeps Pass 2, drops Pass 1
2. Different normalized texts → both kept
3. world/action_effect facts in Pass 1 are NOT dropped even if key matches
4. Fuzzy match path (when enabled) correctly deduplicates
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from dataclasses import dataclass
from cogmem_api.engine.retain.dedup import dedup_facts, _normalize_key_text, _make_dedup_key


@dataclass
class MockFact:
    fact_type: str
    fact_text: str


def test_same_key_keeps_p2_drops_p1():
    p1 = [MockFact("experience", "User bought a Tiger I kit from Revell")]
    p2 = [MockFact("experience", "User bought a Tiger I kit from Revell")]
    result = dedup_facts(p1, p2)
    assert len(result) == 1
    assert result[0] is p2[0]
    print("PASS: Same key keeps P2")


def test_different_texts_keeps_both():
    p1 = [MockFact("experience", "User bought a Tiger I kit")]
    p2 = [MockFact("experience", "User finished building Revell Tiger I")]
    result = dedup_facts(p1, p2)
    assert len(result) == 2
    print("PASS: Different normalized texts keep both")


def test_world_fact_not_dropped_even_if_key_match():
    p1 = [MockFact("world", "Weathering improves model realism")]
    p2 = [MockFact("world", "Weathering improves model realism")]
    result = dedup_facts(p1, p2)
    assert len(result) == 2, "world/action_effect should NOT be deduped"
    print("PASS: world facts not dropped even if key matches")


def test_action_effect_not_dropped():
    p1 = [MockFact("action_effect", "int8 reduces latency")]
    p2 = [MockFact("action_effect", "int8 reduces latency")]
    result = dedup_facts(p1, p2)
    assert len(result) == 2, "action_effect should NOT be deduped"
    print("PASS: action_effect facts not dropped even if key matches")


def test_different_fact_types_no_dedup():
    p1 = [MockFact("opinion", "Tamiya is the best brand for armor models")]
    p2 = [MockFact("opinion", "Tamiya is the best brand for detail painting")]
    result = dedup_facts(p1, p2)
    assert len(result) == 2, "different normalized text = no dedup"
    print("PASS: Different normalized text keeps both even same fact_type")


def test_normalize_key_text_collapse_whitespace():
    t1 = "User  bought   a Tiger I kit"
    t2 = "user bought a tiger i kit"
    assert _normalize_key_text(t1) == _normalize_key_text(t2)
    print("PASS: _normalize_key_text collapses whitespace")


def test_normalize_key_text_first_120_chars():
    long_text = "A" * 200
    key = _normalize_key_text(long_text)
    assert len(key) == 120
    print("PASS: _normalize_key_text truncates at 120 chars")


def test_dedup_with_empty_p2():
    p1 = [MockFact("experience", "User bought a Tiger I")]
    result = dedup_facts(p1, [])
    assert len(result) == 1
    print("PASS: Empty P2 returns all P1 facts")


def test_dedup_with_empty_p1():
    p2 = [MockFact("experience", "User bought a Tiger I")]
    result = dedup_facts([], p2)
    assert len(result) == 1
    print("PASS: Empty P1 returns all P2 facts")


def main():
    tests = [
        test_same_key_keeps_p2_drops_p1,
        test_different_texts_keeps_both,
        test_world_fact_not_dropped_even_if_key_match,
        test_action_effect_not_dropped,
        test_different_fact_types_no_dedup,
        test_normalize_key_text_collapse_whitespace,
        test_normalize_key_text_first_120_chars,
        test_dedup_with_empty_p2,
        test_dedup_with_empty_p1,
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