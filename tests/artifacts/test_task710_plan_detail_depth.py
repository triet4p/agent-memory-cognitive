from __future__ import annotations

from pathlib import Path


def assert_required_files(repo_root: Path) -> None:
    required = [
        repo_root / "docs" / "PLAN.md",
        repo_root / "logs" / "task_710_summary.md",
        repo_root / "tests" / "artifacts" / "test_task710_plan_detail_depth.py",
    ]
    missing = [str(path.relative_to(repo_root)) for path in required if not path.exists()]
    assert not missing, f"Missing task710 files/artifacts: {missing}"


def assert_deep_sections(plan_text: str) -> None:
    required = [
        "File tác động dự kiến:",
        "Verification (gợi ý lệnh):",
        "Rủi ro và fallback:",
        "Exit gate:",
        "### Sprint S11 - Delete hindsight_api only",
        "### Sprint S12 - Close C1 to FULL",
        "### Sprint S13 - Close C3 to FULL",
        "### Sprint S14 - Close C4 to FULL",
        "### Sprint S15 - Full Gate trước tutorial",
    ]
    missing = [snippet for snippet in required if snippet not in plan_text]
    assert not missing, f"PLAN detail depth is insufficient, missing: {missing}"


def assert_historical_and_future_both_present(plan_text: str) -> None:
    required = [
        "## 3) Lịch sử triển khai đã hoàn tất (không xóa)",
        "### 3.8 Backfill B1-B5 (đã triển khai)",
        "## 4) Lộ trình còn lại (hợp nhất, có chiều sâu thi công)",
        "## Phase C - Tutorial (unlock sau S15 PASS)",
    ]
    missing = [snippet for snippet in required if snippet not in plan_text]
    assert not missing, f"PLAN does not keep both historical and future tracks: {missing}"


def main() -> None:
    repo_root = Path(__file__).resolve().parents[2]
    assert_required_files(repo_root)

    plan_text = (repo_root / "docs" / "PLAN.md").read_text(encoding="utf-8")

    assert_deep_sections(plan_text)
    assert_historical_and_future_both_present(plan_text)

    print("Task 710 PLAN detail depth checks passed.")


if __name__ == "__main__":
    main()
