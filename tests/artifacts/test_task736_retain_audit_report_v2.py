"""Artifact test for retain audit report v2 (task 736).

Ensures the generated report exists and includes expected summary and
failure markers from the latest retain test run.
"""
from __future__ import annotations

from pathlib import Path


def run_test() -> None:
    repo_root = Path(__file__).resolve().parents[2]
    report = repo_root / "reports" / "audit_retain_20260419_v2.md"

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
        "tests/retain/test_dialogue_onboarding.py | [FAIL]",
        "Total: 2 passed, 3 failed, 0 errors",
        "action_effect missing 'precondition'",
        "Expected at least one intention with status 'fulfilled'",
        "Token usage should be tracked",
    ]

    missing = [snippet for snippet in required_snippets if snippet not in content]
    assert not missing, f"Report missing expected snippets: {missing}"

    print("OK  retain audit v2 report exists and contains expected results")


def main() -> None:
    run_test()
    print("All task736 retain audit v2 artifact tests passed.")


if __name__ == "__main__":
    main()
