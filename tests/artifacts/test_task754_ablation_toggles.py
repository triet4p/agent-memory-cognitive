"""Task 754: S24 pre-flight — per-request ablation toggles (adaptive_router, graph_retriever).

Verifies:
- FlatQueryAnalyzer returns flat weights (1.0/1.0/1.0/1.0), query_type=semantic
- make_graph_retriever() returns correct retriever type by name
- RecallRequest accepts adaptive_router and graph_retriever fields
- build_recall_payload() wires AblationProfile flags correctly:
    - adaptive_router_enabled=False  → payload["adaptive_router"]=False
    - sum_activation_enabled=False   → payload["graph_retriever"]="link_expansion"
    - sum_activation_enabled=True    → payload["graph_retriever"]="bfs"
- E1-E7 payload matrix is consistent with ablation spec
"""

from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from cogmem_api.engine.query_analyzer import FlatQueryAnalyzer
from cogmem_api.engine.search.retrieval import make_graph_retriever
from cogmem_api.engine.search.graph_retrieval import BFSGraphRetriever
from cogmem_api.engine.search.link_expansion_retrieval import LinkExpansionRetriever
from cogmem_api.engine.search.mpfp_retrieval import MPFPGraphRetriever
from scripts.eval_cogmem import ABLATION_PROFILES, build_recall_payload


def test_flat_query_analyzer_returns_flat_weights():
    analyzer = FlatQueryAnalyzer()
    analyzer.load()
    result = analyzer.analyze("What did the user do last week?")
    assert result.query_type == "semantic"
    assert result.temporal_constraint is None
    for ch in ("semantic", "bm25", "graph", "temporal"):
        assert result.rrf_weights[ch] == 1.0, f"Expected 1.0 for {ch}, got {result.rrf_weights[ch]}"


def test_flat_query_analyzer_ignores_query_content():
    analyzer = FlatQueryAnalyzer()
    r1 = analyzer.analyze("when did this happen?")   # would normally be temporal
    r2 = analyzer.analyze("why did this cause that?")  # would normally be causal
    assert r1.query_type == "semantic"
    assert r2.query_type == "semantic"
    assert r1.rrf_weights == r2.rrf_weights


def test_make_graph_retriever_bfs():
    retriever = make_graph_retriever("bfs")
    assert isinstance(retriever, BFSGraphRetriever)


def test_make_graph_retriever_link_expansion():
    retriever = make_graph_retriever("link_expansion")
    assert isinstance(retriever, LinkExpansionRetriever)


def test_make_graph_retriever_mpfp():
    retriever = make_graph_retriever("mpfp")
    assert isinstance(retriever, MPFPGraphRetriever)


def test_make_graph_retriever_unknown_falls_back_to_bfs():
    retriever = make_graph_retriever("nonexistent")
    assert isinstance(retriever, BFSGraphRetriever)


def test_build_recall_payload_e1_no_adaptive_no_sum():
    profile = ABLATION_PROFILES["E1"]
    payload = build_recall_payload(profile, "test query")
    assert payload["adaptive_router"] is False
    assert payload["graph_retriever"] == "link_expansion"
    assert set(payload["types"]) == {"world", "experience", "opinion"}


def test_build_recall_payload_e5_adaptive_no_sum():
    profile = ABLATION_PROFILES["E5"]
    payload = build_recall_payload(profile, "test query")
    assert payload["adaptive_router"] is True
    assert payload["graph_retriever"] == "link_expansion"


def test_build_recall_payload_e6_no_adaptive_sum():
    profile = ABLATION_PROFILES["E6"]
    payload = build_recall_payload(profile, "test query")
    assert payload["adaptive_router"] is False
    assert payload["graph_retriever"] == "bfs"


def test_build_recall_payload_e7_full_cogmem():
    profile = ABLATION_PROFILES["E7"]
    payload = build_recall_payload(profile, "test query")
    assert payload["adaptive_router"] is True
    assert payload["graph_retriever"] == "bfs"
    assert set(payload["types"]) == {"world", "experience", "opinion", "habit", "intention", "action_effect"}


def test_ablation_matrix_consistency():
    """E1-E4 share same toggle config (no router, no SUM); E5/E6/E7 each differ."""
    for pid in ("E1", "E2", "E3", "E4"):
        p = build_recall_payload(ABLATION_PROFILES[pid], "q")
        assert p["adaptive_router"] is False, f"{pid} should have adaptive_router=False"
        assert p["graph_retriever"] == "link_expansion", f"{pid} should use link_expansion"

    e5 = build_recall_payload(ABLATION_PROFILES["E5"], "q")
    e6 = build_recall_payload(ABLATION_PROFILES["E6"], "q")
    e7 = build_recall_payload(ABLATION_PROFILES["E7"], "q")

    assert e5["adaptive_router"] is True and e5["graph_retriever"] == "link_expansion"
    assert e6["adaptive_router"] is False and e6["graph_retriever"] == "bfs"
    assert e7["adaptive_router"] is True and e7["graph_retriever"] == "bfs"


def test_recall_request_accepts_new_fields():
    from cogmem_api.api.http import RecallRequest
    req = RecallRequest(query="test", adaptive_router=False, graph_retriever="link_expansion")
    assert req.adaptive_router is False
    assert req.graph_retriever == "link_expansion"

    req_default = RecallRequest(query="test")
    assert req_default.adaptive_router is True
    assert req_default.graph_retriever is None


if __name__ == "__main__":
    print("Task 754 ablation toggle tests")
    test_flat_query_analyzer_returns_flat_weights()
    print("  test_flat_query_analyzer_returns_flat_weights PASSED")
    test_flat_query_analyzer_ignores_query_content()
    print("  test_flat_query_analyzer_ignores_query_content PASSED")
    test_make_graph_retriever_bfs()
    print("  test_make_graph_retriever_bfs PASSED")
    test_make_graph_retriever_link_expansion()
    print("  test_make_graph_retriever_link_expansion PASSED")
    test_make_graph_retriever_mpfp()
    print("  test_make_graph_retriever_mpfp PASSED")
    test_make_graph_retriever_unknown_falls_back_to_bfs()
    print("  test_make_graph_retriever_unknown_falls_back_to_bfs PASSED")
    test_build_recall_payload_e1_no_adaptive_no_sum()
    print("  test_build_recall_payload_e1_no_adaptive_no_sum PASSED")
    test_build_recall_payload_e5_adaptive_no_sum()
    print("  test_build_recall_payload_e5_adaptive_no_sum PASSED")
    test_build_recall_payload_e6_no_adaptive_sum()
    print("  test_build_recall_payload_e6_no_adaptive_sum PASSED")
    test_build_recall_payload_e7_full_cogmem()
    print("  test_build_recall_payload_e7_full_cogmem PASSED")
    test_ablation_matrix_consistency()
    print("  test_ablation_matrix_consistency PASSED")
    test_recall_request_accepts_new_fields()
    print("  test_recall_request_accepts_new_fields PASSED")
    print("Task 754 ablation toggles: all 12 tests PASSED.")
