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
        "Sprint 8 - Tutorial Framework Bootstrap",
    ]
    hits = [snippet for snippet in forbidden_snippets if snippet in plan_text]
    assert not hits, f"Legacy plan snippets still present: {hits}"


def assert_plan_contains_new_sprints(plan_text: str) -> None:
    required_snippets = [
        "## PLAN - CogMem Migration (Unified, Full Trace)",
        "3. Quyết định phạm vi đang khóa:",
        "## Phase A - Delete-first",
        "## Phase B - Coverage Closure (C1-C4 -> FULL)",
        "## Phase C - Tutorial (unlock sau S15 PASS)",
        "### Sprint S11 - Delete hindsight_api only",
        "### Sprint S12 - Close C1 to FULL",
        "### Sprint S13 - Close C3 to FULL",
        "### Sprint S14 - Close C4 to FULL",
        "### Sprint S15 - Full Gate trước tutorial",
        "### Sprint S16 - Tutorial Framework",
        "docs/hindsight_removal_playbook.md",
        "C1-C4 đều FULL",
    ]
    missing = [snippet for snippet in required_snippets if snippet not in plan_text]
    assert not missing, f"Missing new roadmap snippets: {missing}"


def assert_execution_order_updated(plan_text: str) -> None:
    required = [
        "S11 -> S12 -> S13 -> S14 -> S15 -> S16 -> S17 -> S18",
        "Không vào S16 nếu S15 chưa PASS",
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
