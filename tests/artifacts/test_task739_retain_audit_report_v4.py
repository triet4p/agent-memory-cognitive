"""Artifact test for retain audit report v4 (task 739).

Validates the updated audit report for retest round 4 exists and captures
expected PASS/FAIL outcomes.
"""
from __future__ import annotations

from pathlib import Path


def run_test() -> None:
    repo_root = Path(__file__).resolve().parents[2]
    report = repo_root / "reports" / "audit_retain_20260420_v4.md"

    assert report.exists(), f"Missing report file: {report}"
    content = report.read_text(encoding="utf-8")

    required_snippets = [
        "# Audit Report — Retain Tests",
        "## Summary",
        "## Failure Details",
        "tests/retain/test_dialogue_action_effect.py | [FAIL]",
        "tests/retain/test_dialogue_habit_routine.py | [PASS]",
        "tests/retain/test_dialogue_intention_lifecycle.py | [FAIL]",
        "tests/retain/test_dialogue_mixed_vi.py | [PASS]",
        "tests/retain/test_dialogue_onboarding.py | [PASS]",
        "Total: 3 passed, 2 failed, 0 errors",
        "Expected a Redis action_effect fact",
        "Expected at least one intention with status 'fulfilled'",
    ]

    missing = [item for item in required_snippets if item not in content]
    assert not missing, f"Report missing expected snippets: {missing}"

    print("OK  retain audit v4 report exists and contains expected results")


def main() -> None:
    run_test()
    print("All task739 retain audit v4 artifact tests passed.")


if __name__ == "__main__":
    main()
