"""Artifact test for retain audit report v3 (task 738).

Validates existence and expected summary/failure snippets in the generated
retain audit report after rerun.
"""
from __future__ import annotations

from pathlib import Path


def run_test() -> None:
    repo_root = Path(__file__).resolve().parents[2]
    report = repo_root / "reports" / "audit_retain_20260419_v3.md"

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
        "Expected a Redis action_effect fact",
        "Expected at least one intention with status 'fulfilled'",
        "Token usage should be tracked",
    ]

    missing = [s for s in required_snippets if s not in content]
    assert not missing, f"Report missing expected snippets: {missing}"

    print("OK  retain audit v3 report exists and contains expected results")


def main() -> None:
    run_test()
    print("All task738 retain audit v3 artifact tests passed.")


if __name__ == "__main__":
    main()
