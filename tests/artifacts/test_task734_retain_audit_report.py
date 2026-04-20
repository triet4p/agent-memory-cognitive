"""Artifact test for retain audit report (task 734).

Validates that the report generated from running all tests/retain exists and
contains required summary sections and expected result counts.
"""
from __future__ import annotations

from pathlib import Path


def run_test() -> None:
    repo_root = Path(__file__).resolve().parents[2]
    report = repo_root / "reports" / "audit_retain_20260419.md"

    assert report.exists(), f"Missing report file: {report}"

    content = report.read_text(encoding="utf-8")

    required_snippets = [
        "# Audit Report — Retain Tests",
        "## Summary",
        "## Failure Details",
        "tests/retain/test_dialogue_action_effect.py",
        "tests/retain/test_dialogue_habit_routine.py",
        "tests/retain/test_dialogue_intention_lifecycle.py",
        "tests/retain/test_dialogue_mixed_vi.py",
        "tests/retain/test_dialogue_onboarding.py",
        "Total: 2 passed, 3 failed, 0 errors",
    ]

    missing = [snippet for snippet in required_snippets if snippet not in content]
    assert not missing, f"Report missing expected snippets: {missing}"

    print("OK  retain audit report exists and contains expected summary")


def main() -> None:
    run_test()
    print("All task734 retain audit artifact tests passed.")


if __name__ == "__main__":
    main()
