"""Artifact test for retain audit report v5 (task 740).

Validates that the latest retain audit report exists and records the all-pass
result from the newest retest round.
"""
from __future__ import annotations

from pathlib import Path


def run_test() -> None:
    repo_root = Path(__file__).resolve().parents[2]
    report = repo_root / "reports" / "audit_retain_20260420_v5.md"

    assert report.exists(), f"Missing report file: {report}"
    content = report.read_text(encoding="utf-8")

    required_snippets = [
        "# Audit Report — Retain Tests",
        "## Summary",
        "## Failure Details",
        "tests/retain/test_dialogue_action_effect.py | [PASS]",
        "tests/retain/test_dialogue_habit_routine.py | [PASS]",
        "tests/retain/test_dialogue_intention_lifecycle.py | [PASS]",
        "tests/retain/test_dialogue_mixed_vi.py | [PASS]",
        "tests/retain/test_dialogue_onboarding.py | [PASS]",
        "Total: 5 passed, 0 failed, 0 errors",
        "No failures or errors.",
    ]

    missing = [snippet for snippet in required_snippets if snippet not in content]
    assert not missing, f"Report missing expected snippets: {missing}"

    print("OK  retain audit v5 report exists and contains expected all-pass results")


def main() -> None:
    run_test()
    print("All task740 retain audit v5 artifact tests passed.")


if __name__ == "__main__":
    main()
