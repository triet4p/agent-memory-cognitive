from __future__ import annotations

from pathlib import Path


def assert_required_outputs(repo_root: Path) -> None:
    required = [
        repo_root / "docs" / "migration_idea_coverage_matrix.md",
        repo_root / "logs" / "task_705_summary.md",
        repo_root / "tests" / "artifacts" / "test_task705_c1_full_gate.py",
    ]
    missing = [str(path.relative_to(repo_root)) for path in required if not path.exists()]
    assert not missing, f"Missing task705 outputs: {missing}"


def assert_c1_full_in_matrix(repo_root: Path) -> None:
    matrix_text = (repo_root / "docs" / "migration_idea_coverage_matrix.md").read_text(encoding="utf-8")

    required_snippets = [
        "| C1 - 6 networks + 7 edge types |",
        "| `FULL` |",
        "Observation/consolidation đã loại bỏ khỏi đường chạy CogMem | `FULL`",
        "Đồng bộ link-type cho causal traversal | `FULL`",
    ]
    missing = [snippet for snippet in required_snippets if snippet not in matrix_text]
    assert not missing, f"Coverage matrix missing C1 full evidence snippets: {missing}"


def assert_no_observation_branch(repo_root: Path) -> None:
    link_expansion = (
        repo_root / "cogmem_api" / "engine" / "search" / "link_expansion_retrieval.py"
    ).read_text(encoding="utf-8")

    forbidden = [
        "_expand_observations",
        "fact_type == \"observation\"",
    ]
    hits = [snippet for snippet in forbidden if snippet in link_expansion]
    assert not hits, f"Legacy observation branch still present: {hits}"


def assert_causal_link_contract(repo_root: Path) -> None:
    targets = [
        repo_root / "cogmem_api" / "engine" / "search" / "retrieval.py",
        repo_root / "cogmem_api" / "engine" / "search" / "link_expansion_retrieval.py",
        repo_root / "cogmem_api" / "engine" / "search" / "graph_retrieval.py",
        repo_root / "cogmem_api" / "engine" / "search" / "mpfp_retrieval.py",
    ]

    forbidden_aliases = ["'causes'", "'caused_by'", "'enables'", "'prevents'"]
    violations: list[str] = []

    for file_path in targets:
        text = file_path.read_text(encoding="utf-8")
        for alias in forbidden_aliases:
            if alias in text:
                violations.append(f"{file_path.relative_to(repo_root)}:{alias}")

    assert not violations, f"Found legacy causal aliases in retrieval readers: {violations}"

    retrieval_text = (repo_root / "cogmem_api" / "engine" / "search" / "retrieval.py").read_text(encoding="utf-8")
    link_expansion_text = (
        repo_root / "cogmem_api" / "engine" / "search" / "link_expansion_retrieval.py"
    ).read_text(encoding="utf-8")

    assert "AND ml.link_type IN ('temporal', 'causal')" in retrieval_text, (
        "Temporal spreading must include canonical causal link type"
    )
    assert "AND ml.link_type = 'causal'" in link_expansion_text, (
        "Link expansion causal traversal must use canonical causal link type"
    )


def main() -> None:
    repo_root = Path(__file__).resolve().parents[2]
    assert_required_outputs(repo_root)
    assert_c1_full_in_matrix(repo_root)
    assert_no_observation_branch(repo_root)
    assert_causal_link_contract(repo_root)

    print("Task 705 C1 full gate checks passed.")


if __name__ == "__main__":
    main()
