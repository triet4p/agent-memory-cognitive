"""
Task 786: Adaptive query routing fix.

Verifies that classify_query_type:
1. Decouples from temporal_constraint — query type determined by text only
2. Routes aggregation queries (how many, how much, list all, count, total)
   to multi_hop, not temporal

Run:
    uv run python tests/artifacts/test_task786_query_routing.py
"""

from __future__ import annotations

import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from cogmem_api.engine.query_analyzer import classify_query_type


def test_aggregation_queries_route_to_multi_hop():
    """Count/list queries should route to multi_hop, not temporal."""
    cases = [
        "How many model kits have I worked on or bought?",
        "How many times did I visit the museum?",
        "How much did I spend on paints?",
        "List all the places I've visited",
        "What are all the projects I've done?",
        "Count my completed builds",
        "Total spending on model kits this year",
        "All the tools I own",
        "Across all my experience, what topics came up?",
    ]
    for query in cases:
        result = classify_query_type(query, None)
        assert result == "multi_hop", (
            f"Query '{query}' => {result!r}, expected 'multi_hop'"
        )
    print("  test_aggregation_queries_route_to_multi_hop: PASS")


def test_temporal_constraint_does_not_force_temporal():
    """temporal_constraint param must not influence query type classification."""
    query = "How many model kits have I worked on or bought?"
    result_with_tc = classify_query_type(query, object())
    result_without_tc = classify_query_type(query, None)
    assert result_with_tc == result_without_tc == "multi_hop", (
        f"Query with temporal_constraint={object()} => {result_with_tc!r}, "
        f"without => {result_without_tc!r}, both should be 'multi_hop'"
    )
    print("  test_temporal_constraint_does_not_force_temporal: PASS")


def test_pure_temporal_queries_still_work():
    """Time-based queries without aggregation should route to temporal."""
    cases = [
        "What did I do last week?",
        "When did I buy the B-29?",
        "What happened during my last visit?",
        "What did I do this morning?",
    ]
    for query in cases:
        result = classify_query_type(query, None)
        assert result == "temporal", (
            f"Query '{query}' => {result!r}, expected 'temporal'"
        )
    print("  test_pure_temporal_queries_still_work: PASS")


def test_preference_queries():
    """Opinions/preferences should route to preference."""
    cases = [
        "I prefer Vallejo paints",
        "What's my favorite paint brand?",
        "Do I like FastAPI or Django better?",
    ]
    for query in cases:
        result = classify_query_type(query, None)
        assert result == "preference", (
            f"Query '{query}' => {result!r}, expected 'preference'"
        )
    print("  test_preference_queries: PASS")


def test_multi_hop_connection_queries():
    """Connection/relationship queries should route to multi_hop."""
    cases = [
        "What's related to the Spitfire build?",
        "What's connected to my Vallejo paints?",
        "How are these projects connected?",
        "What's between these two topics?",
    ]
    for query in cases:
        result = classify_query_type(query, None)
        assert result == "multi_hop", (
            f"Query '{query}' => {result!r}, expected 'multi_hop'"
        )
    print("  test_multi_hop_connection_queries: PASS")


def main():
    print("Task 786: Adaptive query routing fix")
    print("=" * 60)
    test_aggregation_queries_route_to_multi_hop()
    test_temporal_constraint_does_not_force_temporal()
    test_pure_temporal_queries_still_work()
    test_preference_queries()
    test_multi_hop_connection_queries()
    print()
    print("ALL TESTS PASSED")


if __name__ == "__main__":
    main()