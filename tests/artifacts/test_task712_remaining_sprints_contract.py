from __future__ import annotations

from pathlib import Path


def assert_required_files(repo_root: Path) -> None:
    required = [
        repo_root / "docs" / "PLAN.md",
        repo_root / "logs" / "task_712_summary.md",
        repo_root / "tests" / "artifacts" / "test_task712_remaining_sprints_contract.py",
    ]
    missing = [str(path.relative_to(repo_root)) for path in required if not path.exists()]
    assert not missing, f"Missing task712 files/artifacts: {missing}"


def get_section(plan_text: str, heading: str, next_heading: str | None) -> str:
    start = plan_text.find(heading)
    assert start != -1, f"Missing heading: {heading}"

    if next_heading is None:
        return plan_text[start:]

    end = plan_text.find(next_heading, start)
    assert end != -1, f"Missing next heading: {next_heading}"
    return plan_text[start:end]


def assert_execution_contract(section: str, heading: str) -> None:
    required_markers = [
        "Mục tiêu sprint:",
        "Phụ thuộc:",
        "Inputs bắt buộc:",
        "Atomic tasks:",
        "File tác động dự kiến:",
        "Outputs bắt buộc:",
        "Verification (gợi ý lệnh):",
        "Exit gate:",
        "Rủi ro và fallback:",
    ]
    missing = [marker for marker in required_markers if marker not in section]
    assert not missing, f"Section {heading} is still too shallow, missing: {missing}"


def assert_s11_to_s18_depth(plan_text: str) -> None:
    sections = [
        ("### Sprint S11 - Delete hindsight_api only", "### Sprint S12 - Close C1 to FULL"),
        ("### Sprint S12 - Close C1 to FULL", "### Sprint S13 - Close C3 to FULL"),
        ("### Sprint S13 - Close C3 to FULL", "### Sprint S14 - Close C4 to FULL"),
        ("### Sprint S14 - Close C4 to FULL", "### Sprint S15 - Full Gate trước tutorial"),
        ("### Sprint S15 - Full Gate trước tutorial", "## Phase C - Tutorial (unlock sau S15 PASS)"),
        ("### Sprint S16 - Tutorial Framework", "### Sprint S17 - Tutorial Core"),
        ("### Sprint S17 - Tutorial Core", "### Sprint S18 - Tutorial Non-core + Capstone"),
        ("### Sprint S18 - Tutorial Non-core + Capstone", "## 5) Bảng tiến độ hợp nhất"),
    ]

    for heading, next_heading in sections:
        section = get_section(plan_text, heading, next_heading)
        assert_execution_contract(section, heading)


def main() -> None:
    repo_root = Path(__file__).resolve().parents[2]
    assert_required_files(repo_root)

    plan_text = (repo_root / "docs" / "PLAN.md").read_text(encoding="utf-8")
    assert_s11_to_s18_depth(plan_text)

    print("Task 712 remaining sprints contract checks passed.")


if __name__ == "__main__":
    main()
