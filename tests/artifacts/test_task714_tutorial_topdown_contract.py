from __future__ import annotations

from pathlib import Path


def _get_section(plan_text: str, start_heading: str, next_heading: str) -> str:
    start = plan_text.find(start_heading)
    assert start != -1, f"Missing heading: {start_heading}"
    end = plan_text.find(next_heading, start)
    assert end != -1, f"Missing next heading: {next_heading}"
    return plan_text[start:end]


def assert_tutorial_topdown_contract(plan_text: str) -> None:
    section_s16 = _get_section(
        plan_text,
        "### Sprint S16 - Tutorial Top-down Architecture Baseline",
        "### Sprint S17 - Tutorial Module-by-Module Decomposition",
    )
    section_s17 = _get_section(
        plan_text,
        "### Sprint S17 - Tutorial Module-by-Module Decomposition",
        "### Sprint S18 - Tutorial Function-by-Function Deep Dive",
    )
    section_s18 = _get_section(
        plan_text,
        "### Sprint S18 - Tutorial Function-by-Function Deep Dive",
        "## 5) Bảng tiến độ hợp nhất",
    )

    assert "Top-down level:" in section_s16 and "Architecture" in section_s16
    assert "Top-down level:" in section_s17 and "Module" in section_s17
    assert "Top-down level:" in section_s18 and "Function" in section_s18

    assert "Function inventory (public/private)" in section_s16
    assert "Function inventory (public/private)" in section_s17

    assert "Function deep-dive" in section_s18
    assert "public/private" in section_s18
    assert "checkpoint" in section_s18.lower()


def assert_no_core_noncore_split(plan_text: str) -> None:
    forbidden = [
        "### Sprint S17 - Tutorial Core",
        "### Sprint S18 - Tutorial Non-core + Capstone",
        "core/non-core",
        "module core",
        "module non-core",
    ]
    found = [term for term in forbidden if term in plan_text]
    assert not found, f"Legacy split terms still present: {found}"



def main() -> None:
    repo_root = Path(__file__).resolve().parents[2]
    plan_path = repo_root / "docs" / "PLAN.md"
    assert plan_path.exists(), "Missing docs/PLAN.md"

    plan_text = plan_path.read_text(encoding="utf-8")
    assert_tutorial_topdown_contract(plan_text)
    assert_no_core_noncore_split(plan_text)

    print("Task 714 top-down tutorial contract checks passed.")


if __name__ == "__main__":
    main()
