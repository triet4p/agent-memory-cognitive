from __future__ import annotations

from pathlib import Path


def assert_required_files(repo_root: Path) -> None:
    required = [
        repo_root / "docs" / "PLAN.md",
        repo_root / "logs" / "task_618_summary.md",
        repo_root / "tests" / "artifacts" / "test_task618_plan_refresh.py",
    ]
    missing = [str(path.relative_to(repo_root)) for path in required if not path.exists()]
    assert not missing, f"Missing task618 files/artifacts: {missing}"


def assert_plan_removed_legacy_chain(plan_text: str) -> None:
    forbidden_snippets = [
        "Atomic Task T6.4",
        "T6.1 -> T6.2 -> T6.3 -> T6.4",
        "E8 Hierarchical KG được triển khai trong Sprint 8",
    ]
    hits = [snippet for snippet in forbidden_snippets if snippet in plan_text]
    assert not hits, f"Legacy plan snippets still present: {hits}"


def assert_plan_contains_new_sprints(plan_text: str) -> None:
    required_snippets = [
        "Atomic Task T7.1",
        "Atomic Task T7.2",
        "Atomic Task T7.3",
        "Atomic Task T8.1",
        "Atomic Task T8.2",
        "Atomic Task T9.1",
        "Atomic Task T9.2",
        "Atomic Task T10.1",
        "Atomic Task T10.2",
        "Tutorial Framework Bootstrap",
        "Tutorial Non-Core Coverage",
        "function/property-level",
        "bao phủ cả module lõi và module hỗ trợ",
    ]
    missing = [snippet for snippet in required_snippets if snippet not in plan_text]
    assert not missing, f"Missing new roadmap snippets: {missing}"


def assert_execution_order_updated(plan_text: str) -> None:
    required = [
        "T6.1 -> T6.2 -> T6.3 -> T7.1 -> T7.2 -> T7.3",
        "-> T8.1 -> T8.2 -> T9.1 -> T9.2 -> T10.1 -> T10.2 -> EvalTrack",
    ]
    missing = [snippet for snippet in required if snippet not in plan_text]
    assert not missing, f"Canonical order is not updated: {missing}"


def main() -> None:
    repo_root = Path(__file__).resolve().parents[2]
    assert_required_files(repo_root)
    plan_text = (repo_root / "docs" / "PLAN.md").read_text(encoding="utf-8")

    assert_plan_removed_legacy_chain(plan_text)
    assert_plan_contains_new_sprints(plan_text)
    assert_execution_order_updated(plan_text)

    print("Task 618 PLAN refresh checks passed.")


if __name__ == "__main__":
    main()
