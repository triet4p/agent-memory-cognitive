from __future__ import annotations

from pathlib import Path


def assert_required_files(repo_root: Path) -> None:
    required = [
        repo_root / "docs" / "migration_idea_coverage_matrix.md",
        repo_root / "logs" / "task_701_summary.md",
        repo_root / "tests" / "artifacts" / "test_task701_idea_coverage_matrix.py",
    ]
    missing = [str(path.relative_to(repo_root)) for path in required if not path.exists()]
    assert not missing, f"Missing task701 files/artifacts: {missing}"


def assert_matrix_sections(text: str) -> None:
    required = [
        "### C1 - Cognitively-Grounded Memory Graph",
        "### C2 - Lossless Node Metadata",
        "### C3 - Episodic Buffer SUM + Cycle Guards",
        "### C4 - Adaptive Query Routing",
        "### C5 - Hierarchical Knowledge Graph",
        "## Backlog Handover to T7.2",
    ]
    missing = [snippet for snippet in required if snippet not in text]
    assert not missing, f"Coverage matrix missing sections: {missing}"


def assert_expected_statuses(text: str) -> None:
    required = [
        "C1 - 6 networks + 7 edge types",
        "`PARTIAL`",
        "C2 - Lossless metadata",
        "`FULL`",
        "C3 - SUM + cycle guards",
        "C4 - Adaptive query routing",
        "C5 - Hierarchical Knowledge Graph",
        "`MISSING`",
        "Tổng quan: `PARTIAL`",
    ]
    missing = [snippet for snippet in required if snippet not in text]
    assert not missing, f"Coverage matrix status contract missing: {missing}"


def assert_symbol_evidence(text: str) -> None:
    required_symbols = [
        "MemoryUnit.raw_snippet",
        "create_transition_links_batch",
        "BFSGraphRetriever._retrieve_with_conn",
        "classify_query_type",
        "retrieve_all_fact_types_parallel",
        "DEFAULT_GRAPH_RETRIEVER = \"link_expansion\"",
    ]
    missing = [symbol for symbol in required_symbols if symbol not in text]
    assert not missing, f"Coverage matrix missing symbol-level evidence: {missing}"


def assert_isolation(text: str) -> None:
    forbidden = [
        "import hindsight_api",
        "from hindsight_api",
    ]
    hits = [snippet for snippet in forbidden if snippet in text]
    assert not hits, f"Isolation violation in matrix doc: {hits}"


def main() -> None:
    repo_root = Path(__file__).resolve().parents[2]
    assert_required_files(repo_root)

    matrix_text = (repo_root / "docs" / "migration_idea_coverage_matrix.md").read_text(encoding="utf-8")

    assert_matrix_sections(matrix_text)
    assert_expected_statuses(matrix_text)
    assert_symbol_evidence(matrix_text)
    assert_isolation(matrix_text)

    print("Task 701 idea coverage matrix checks passed.")


if __name__ == "__main__":
    main()
