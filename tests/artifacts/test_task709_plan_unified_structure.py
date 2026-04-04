from __future__ import annotations

from pathlib import Path


def assert_required_files(repo_root: Path) -> None:
    required = [
        repo_root / "docs" / "PLAN.md",
        repo_root / "logs" / "task_709_summary.md",
        repo_root / "tests" / "artifacts" / "test_task709_plan_unified_structure.py",
    ]
    missing = [str(path.relative_to(repo_root)) for path in required if not path.exists()]
    assert not missing, f"Missing task709 files/artifacts: {missing}"


def assert_historical_trace_present(plan_text: str) -> None:
    required = [
        "## 3) Lịch sử triển khai đã hoàn tất (không xóa)",
        "### 3.2 Sprint 1 - Nền tảng schema/engine",
        "### 3.3 Sprint 2 - Retain pipeline + mạng mới",
        "### 3.4 Sprint 3 - Retrieval intelligence",
        "### 3.5 Sprint 4 - Reflect",
        "### 3.6 Sprint 5 - Runtime + Docker",
        "### 3.7 Sprint 6 - Completeness trước track eval",
        "### 3.8 Backfill B1-B5 (đã triển khai)",
        "### 3.9 Sprint 7 readiness (đã hoàn tất)",
    ]
    missing = [snippet for snippet in required if snippet not in plan_text]
    assert not missing, f"Historical trace missing in PLAN: {missing}"


def assert_forward_roadmap_present(plan_text: str) -> None:
    required = [
        "### Sprint S11 - Delete hindsight_api only",
        "### Sprint S12 - Close C1 to FULL",
        "### Sprint S13 - Close C3 to FULL",
        "### Sprint S14 - Close C4 to FULL",
        "### Sprint S15 - Full Gate trước tutorial",
        "### Sprint S16 - Tutorial Framework",
        "### Sprint S17 - Tutorial Core",
        "### Sprint S18 - Tutorial Non-core + Capstone",
        "S11 -> S12 -> S13 -> S14 -> S15 -> S16 -> S17 -> S18",
    ]
    missing = [snippet for snippet in required if snippet not in plan_text]
    assert not missing, f"Forward roadmap missing in PLAN: {missing}"


def main() -> None:
    repo_root = Path(__file__).resolve().parents[2]
    assert_required_files(repo_root)

    plan_text = (repo_root / "docs" / "PLAN.md").read_text(encoding="utf-8")

    assert_historical_trace_present(plan_text)
    assert_forward_roadmap_present(plan_text)

    print("Task 709 unified PLAN structure checks passed.")


if __name__ == "__main__":
    main()
