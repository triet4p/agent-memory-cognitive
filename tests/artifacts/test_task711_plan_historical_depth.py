from __future__ import annotations

from pathlib import Path


def assert_required_files(repo_root: Path) -> None:
    required = [
        repo_root / "docs" / "PLAN.md",
        repo_root / "logs" / "task_711_summary.md",
        repo_root / "tests" / "artifacts" / "test_task711_plan_historical_depth.py",
    ]
    missing = [str(path.relative_to(repo_root)) for path in required if not path.exists()]
    assert not missing, f"Missing task711 files/artifacts: {missing}"


def get_section(plan_text: str, heading: str, next_heading: str | None) -> str:
    start = plan_text.find(heading)
    assert start != -1, f"Missing heading: {heading}"

    if next_heading is None:
        return plan_text[start:]

    end = plan_text.find(next_heading, start)
    assert end != -1, f"Missing next heading: {next_heading}"
    return plan_text[start:end]


def assert_historical_depth(plan_text: str) -> None:
    sections = [
        ("### 3.2 Sprint 1 - Nền tảng schema/engine", "### 3.3 Sprint 2 - Retain pipeline + mạng mới", "Mục tiêu sprint:"),
        ("### 3.3 Sprint 2 - Retain pipeline + mạng mới", "### 3.4 Sprint 3 - Retrieval intelligence", "Mục tiêu sprint:"),
        ("### 3.4 Sprint 3 - Retrieval intelligence", "### 3.5 Sprint 4 - Reflect", "Mục tiêu sprint:"),
        ("### 3.5 Sprint 4 - Reflect", "### 3.6 Sprint 5 - Runtime + Docker", "Mục tiêu sprint:"),
        ("### 3.6 Sprint 5 - Runtime + Docker", "### 3.7 Sprint 6 - Completeness trước track eval", "Mục tiêu sprint:"),
        ("### 3.7 Sprint 6 - Completeness trước track eval", "### 3.8 Backfill B1-B5 (đã triển khai)", "Mục tiêu sprint:"),
        ("### 3.8 Backfill B1-B5 (đã triển khai)", "### 3.9 Sprint 7 readiness (đã hoàn tất)", "Mục tiêu backfill:"),
        ("### 3.9 Sprint 7 readiness (đã hoàn tất)", "## 4) Lộ trình còn lại (hợp nhất, có chiều sâu thi công)", "Mục tiêu sprint:"),
    ]

    for heading, next_heading, objective_marker in sections:
        section = get_section(plan_text, heading, next_heading)
        assert objective_marker in section, f"Section too shallow, missing objective marker in: {heading}"
        assert "Atomic tasks đã hoàn tất:" in section, f"Section too shallow, missing atomic tasks in: {heading}"
        assert "Verification trọng tâm:" in section, f"Section too shallow, missing verification detail in: {heading}"
        assert "Artifacts chính:" in section, f"Section missing artifacts list in: {heading}"


def main() -> None:
    repo_root = Path(__file__).resolve().parents[2]
    assert_required_files(repo_root)

    plan_text = (repo_root / "docs" / "PLAN.md").read_text(encoding="utf-8")
    assert_historical_depth(plan_text)

    print("Task 711 PLAN historical depth checks passed.")


if __name__ == "__main__":
    main()
