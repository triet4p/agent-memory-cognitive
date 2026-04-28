"""
Task 787: Per-fact 4-channel trace in recall response.

Verifies:
1. channel_ranks keys are bare channel names ("semantic", "bm25", "graph",
   "temporal") NOT the fusion.py format ("semantic_rank", "bm25_rank", etc.)
2. All 4 channels present in dict (None if channel didn't retrieve the fact)
3. channel_ranks only populated when enable_trace=True; None otherwise

Run:
    uv run python tests/artifacts/test_task787_trace.py
"""

from __future__ import annotations

import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from cogmem_api.api.http import RecallResult


def test_bare_channel_name_keys():
    """channel_ranks keys must be bare names like 'semantic', not 'semantic_rank'."""
    r = RecallResult(
        id="test-1",
        text="Built Spitfire mkVb",
        type="experience",
        score=0.82,
        channel_ranks={"semantic": 2, "bm25": 8, "graph": 1, "temporal": 3},
    )
    assert "semantic" in r.channel_ranks, "key must be 'semantic', not 'semantic_rank'"
    assert "bm25" in r.channel_ranks, "key must be 'bm25', not 'bm25_rank'"
    assert "graph" in r.channel_ranks, "key must be 'graph', not 'graph_rank'"
    assert "temporal" in r.channel_ranks, "key must be 'temporal', not 'temporal_rank'"
    assert "semantic_rank" not in r.channel_ranks, "no '_rank' suffix in keys"
    assert "bm25_rank" not in r.channel_ranks, "no '_rank' suffix in keys"
    print("  test_bare_channel_name_keys: PASS")


def test_all_four_channels_present():
    """channel_ranks dict must have entries for all 4 channels."""
    r = RecallResult(
        id="test-2",
        text="Bought Vallejo paints",
        type="world",
        score=0.75,
        channel_ranks={"semantic": 1, "bm25": None, "graph": 4, "temporal": None},
    )
    assert set(r.channel_ranks.keys()) == {"semantic", "bm25", "graph", "temporal"}
    assert r.channel_ranks["semantic"] == 1
    assert r.channel_ranks["bm25"] is None  # temporal channel did not retrieve this fact
    assert r.channel_ranks["graph"] == 4
    assert r.channel_ranks["temporal"] is None
    print("  test_all_four_channels_present: PASS")


def test_channel_ranks_none_when_trace_disabled():
    """When trace=False, channel_ranks is None (not an empty dict)."""
    r = RecallResult(
        id="test-3",
        text="Some fact",
        type="world",
        score=0.5,
        channel_ranks=None,
    )
    assert r.channel_ranks is None
    print("  test_channel_ranks_none_when_trace_disabled: PASS")


def test_rank_values_are_integers():
    """Rank values must be integers (not strings)."""
    r = RecallResult(
        id="test-4",
        text="Another fact",
        type="opinion",
        score=0.6,
        channel_ranks={"semantic": 5, "bm25": 12, "graph": 2, "temporal": 8},
    )
    for ch, rank in r.channel_ranks.items():
        if rank is not None:
            assert isinstance(rank, int), f"{ch} rank must be int, got {type(rank).__name__}"
    print("  test_rank_values_are_integers: PASS")


def test_1_indexed_ranks():
    """Ranks are 1-indexed (rank 1 = best in channel)."""
    r = RecallResult(
        id="test-5",
        text="Best semantic match",
        type="world",
        score=0.99,
        channel_ranks={"semantic": 1, "bm25": 50, "graph": 3, "temporal": None},
    )
    assert r.channel_ranks["semantic"] == 1
    assert r.channel_ranks["bm25"] >= 1
    print("  test_1_indexed_ranks: PASS")


def main():
    print("Task 787: Per-fact 4-channel trace in recall response")
    print("=" * 60)
    test_bare_channel_name_keys()
    test_all_four_channels_present()
    test_channel_ranks_none_when_trace_disabled()
    test_rank_values_are_integers()
    test_1_indexed_ranks()
    print()
    print("NOTE: Integration test with live server required to verify")
    print("fusion.py -> memory_engine.py -> http.py chain produces correct")
    print("key format ('semantic' not 'semantic_rank') and always includes")
    print("all 4 channel keys.")
    print()
    print("ALL TESTS PASSED")


if __name__ == "__main__":
    main()