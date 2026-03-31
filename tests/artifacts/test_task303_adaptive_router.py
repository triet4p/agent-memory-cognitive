from __future__ import annotations

import sys
from pathlib import Path


def assert_required_files(repo_root: Path) -> None:
    required = [
        repo_root / "cogmem_api" / "engine" / "query_analyzer.py",
        repo_root / "cogmem_api" / "engine" / "search" / "fusion.py",
        repo_root / "cogmem_api" / "engine" / "search" / "retrieval.py",
    ]
    missing = [str(path.relative_to(repo_root)) for path in required if not path.exists()]
    assert not missing, f"Missing T3.3 files: {missing}"


def assert_isolation(repo_root: Path) -> None:
    scope = [
        repo_root / "cogmem_api" / "engine" / "query_analyzer.py",
        repo_root / "cogmem_api" / "engine" / "search" / "fusion.py",
        repo_root / "cogmem_api" / "engine" / "search" / "retrieval.py",
    ]

    violating: list[str] = []
    for py_file in scope:
        text = py_file.read_text(encoding="utf-8")
        if "hindsight_api" in text:
            violating.append(str(py_file.relative_to(repo_root)))

    assert not violating, f"Found forbidden hindsight imports: {violating}"


def run_query_type_matrix() -> None:
    from cogmem_api.engine.query_analyzer import build_query_analysis, get_adaptive_rrf_weights

    cases = [
        ("What happened last week?", "temporal"),
        ("Why did the outage happen?", "causal"),
        ("What should we do next quarter?", "prospective"),
        ("Which cuisine do I prefer?", "preference"),
        ("How are alpha and beta projects connected?", "multi_hop"),
        ("Summarize my profile.", "semantic"),
    ]

    for query, expected_type in cases:
        analysis = build_query_analysis(query)
        assert analysis.query_type == expected_type, f"Unexpected route for '{query}': {analysis.query_type}"
        assert analysis.rrf_weights == get_adaptive_rrf_weights(expected_type)


def run_weighted_rrf_ranking_matrix() -> None:
    from cogmem_api.engine.query_analyzer import get_adaptive_rrf_weights
    from cogmem_api.engine.search.fusion import weighted_reciprocal_rank_fusion
    from cogmem_api.engine.search.retrieval import ParallelRetrievalResult, fuse_parallel_results
    from cogmem_api.engine.search.types import RetrievalResult

    semantic = [RetrievalResult(id="S1", text="semantic", fact_type="world", similarity=0.9)]
    bm25 = [RetrievalResult(id="B1", text="bm25", fact_type="world", bm25_score=10.0)]
    graph = [RetrievalResult(id="G1", text="graph", fact_type="world", activation=0.9)]
    temporal = [RetrievalResult(id="T1", text="temporal", fact_type="world", temporal_score=0.9)]

    expected_top = {
        "semantic": "S1",  # equal weights fallback keeps semantic first by source order
        "temporal": "T1",
        "causal": "G1",
        "prospective": "G1",
        "preference": "G1",
        "multi_hop": "G1",
    }

    for query_type, top_id in expected_top.items():
        weights = get_adaptive_rrf_weights(query_type)

        merged = weighted_reciprocal_rank_fusion(
            result_lists=[semantic, bm25, graph, temporal],
            source_weights=weights,
            source_names=["semantic", "bm25", "graph", "temporal"],
            k=60,
        )
        assert merged[0].id == top_id, f"Unexpected top result for query_type={query_type}"

        # Verify retrieval-level helper applies the same adaptive weights.
        parallel_result = ParallelRetrievalResult(
            semantic=semantic,
            bm25=bm25,
            graph=graph,
            temporal=temporal,
            query_type=query_type,
            rrf_weights=weights,
        )
        fused = fuse_parallel_results(parallel_result)
        assert fused[0].id == top_id, f"Retrieval helper mismatch for query_type={query_type}"


def main() -> None:
    repo_root = Path(__file__).resolve().parents[2]
    repo_root_str = str(repo_root)
    if repo_root_str not in sys.path:
        sys.path.insert(0, repo_root_str)

    assert_required_files(repo_root)
    assert_isolation(repo_root)
    run_query_type_matrix()
    run_weighted_rrf_ranking_matrix()
    print("Task 303 adaptive routing check passed.")


if __name__ == "__main__":
    main()
