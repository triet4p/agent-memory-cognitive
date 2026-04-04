from __future__ import annotations

import sys
from pathlib import Path


def assert_required_outputs(repo_root: Path) -> None:
    required = [
        repo_root / "logs" / "task_707_summary.md",
        repo_root / "tests" / "artifacts" / "test_task707_c4_adaptive_full_gate.py",
    ]
    missing = [str(path.relative_to(repo_root)) for path in required if not path.exists()]
    assert not missing, f"Missing task707 outputs: {missing}"


def assert_coverage_docs_read_only(repo_root: Path) -> None:
    matrix_text = (repo_root / "docs" / "migration_idea_coverage_matrix.md").read_text(encoding="utf-8")

    forbidden_snippets = [
        "_resolve_planning_intention_ids",
        "_apply_query_type_evidence_priority",
    ]
    violations = [snippet for snippet in forbidden_snippets if snippet in matrix_text]
    assert not violations, f"Coverage matrix should remain read-only in this task: {violations}"


def assert_prospective_fact_type_routing() -> None:
    from cogmem_api.engine.search.retrieval import _select_fact_types_for_query

    routed = _select_fact_types_for_query("prospective", ["world", "experience", "intention", "action_effect"])
    assert routed == ["intention"], "Prospective routing must query only intention network"

    passthrough = _select_fact_types_for_query("causal", ["world", "action_effect", "intention"])
    assert passthrough == ["world", "action_effect", "intention"], "Non-prospective routes should keep configured fact types"


def assert_query_type_evidence_priority_boosts() -> None:
    from cogmem_api.engine.search.retrieval import _apply_query_type_evidence_priority
    from cogmem_api.engine.search.types import MergedCandidate, RetrievalResult

    causal_candidates = [
        MergedCandidate(
            retrieval=RetrievalResult(id="w1", text="world", fact_type="world"),
            rrf_score=0.050,
            source_ranks={"graph_rank": 1},
        ),
        MergedCandidate(
            retrieval=RetrievalResult(id="ae1", text="action", fact_type="action_effect"),
            rrf_score=0.045,
            source_ranks={"semantic_rank": 1},
        ),
    ]

    boosted_causal = _apply_query_type_evidence_priority(causal_candidates, "causal")
    assert boosted_causal[0].id == "ae1", "Causal routing should prioritize action-effect evidence"

    prospective_candidates = [
        MergedCandidate(
            retrieval=RetrievalResult(id="i_graph", text="planning", fact_type="intention"),
            rrf_score=0.046,
            source_ranks={"graph_rank": 1, "temporal_rank": 1},
        ),
        MergedCandidate(
            retrieval=RetrievalResult(id="i_plain", text="planning2", fact_type="intention"),
            rrf_score=0.047,
            source_ranks={"semantic_rank": 1},
        ),
    ]

    boosted_prospective = _apply_query_type_evidence_priority(prospective_candidates, "prospective")
    assert boosted_prospective[0].id == "i_graph", "Prospective routing should prioritize transition/temporal-backed intention evidence"


def assert_prospective_planning_filter() -> None:
    from cogmem_api.engine.search.retrieval import ParallelRetrievalResult, _filter_prospective_results
    from cogmem_api.engine.search.types import RetrievalResult

    parallel = ParallelRetrievalResult(
        semantic=[
            RetrievalResult(id="plan", text="p", fact_type="intention"),
            RetrievalResult(id="done", text="d", fact_type="intention"),
            RetrievalResult(id="w", text="w", fact_type="world"),
        ],
        bm25=[RetrievalResult(id="done", text="d", fact_type="intention")],
        graph=[RetrievalResult(id="plan", text="p", fact_type="intention")],
        temporal=[RetrievalResult(id="plan", text="p", fact_type="intention")],
        query_type="prospective",
    )

    filtered = _filter_prospective_results(parallel, {"plan"})
    assert [item.id for item in filtered.semantic] == ["plan"], "Semantic channel must keep only planning intentions"
    assert [item.id for item in filtered.bm25] == [], "BM25 channel must drop non-planning intentions"
    assert [item.id for item in filtered.graph] == ["plan"], "Graph channel must keep planning intentions"
    assert filtered.temporal is not None and [item.id for item in filtered.temporal] == ["plan"]


def assert_transition_signal_in_link_expansion(repo_root: Path) -> None:
    text = (repo_root / "cogmem_api" / "engine" / "search" / "link_expansion_retrieval.py").read_text(encoding="utf-8")
    assert "ml.link_type = 'transition'" in text, "Link expansion must include transition evidence traversal"


def main() -> None:
    repo_root = Path(__file__).resolve().parents[2]
    repo_root_str = str(repo_root)
    if repo_root_str not in sys.path:
        sys.path.insert(0, repo_root_str)

    assert_required_outputs(repo_root)
    assert_coverage_docs_read_only(repo_root)
    assert_prospective_fact_type_routing()
    assert_query_type_evidence_priority_boosts()
    assert_prospective_planning_filter()
    assert_transition_signal_in_link_expansion(repo_root)

    print("Task 707 C4 adaptive-full gate checks passed.")


if __name__ == "__main__":
    main()
