from __future__ import annotations

from pathlib import Path


def assert_required_outputs(repo_root: Path) -> None:
    required = [
        repo_root / "reports" / "hindsight_delete_only_report.md",
        repo_root / "logs" / "task_704_summary.md",
        repo_root / "tests" / "artifacts" / "test_task704_delete_hindsight_only.py",
    ]
    missing = [str(path.relative_to(repo_root)) for path in required if not path.exists()]
    assert not missing, f"Missing task704 outputs: {missing}"


def assert_hindsight_directory_removed(repo_root: Path) -> None:
    assert not (repo_root / "hindsight_api").exists(), "hindsight_api directory must be removed in S11"


def assert_no_runtime_imports(repo_root: Path) -> None:
    violations: list[str] = []
    for file_path in (repo_root / "cogmem_api").rglob("*.py"):
        text = file_path.read_text(encoding="utf-8")
        if "from hindsight_api" in text or "import hindsight_api" in text:
            violations.append(str(file_path.relative_to(repo_root)))

    assert not violations, f"Runtime isolation violated in cogmem_api: {violations}"


def assert_report_snapshot_contract(repo_root: Path) -> None:
    report_text = (repo_root / "reports" / "hindsight_delete_only_report.md").read_text(encoding="utf-8")

    required_snippets = [
        "## Snapshot trước xóa",
        "## Snapshot sau xóa",
        "from hindsight_api|import hindsight_api",
        "NO_MATCH_IN_COGMEM_API",
        "HINDSIGHT_API_DIRECTORY_NOT_FOUND",
        "tests/artifacts/test_task001_inventory.py",
    ]
    missing = [snippet for snippet in required_snippets if snippet not in report_text]
    assert not missing, f"Delete-only report missing snapshot contracts: {missing}"


def main() -> None:
    repo_root = Path(__file__).resolve().parents[2]
    assert_required_outputs(repo_root)
    assert_hindsight_directory_removed(repo_root)
    assert_no_runtime_imports(repo_root)
    assert_report_snapshot_contract(repo_root)

    print("Task 704 delete-only checks passed.")


if __name__ == "__main__":
    main()
