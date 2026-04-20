"""Artifact test for retain audit report v6 (task 741).

Validates that the latest audit report exists and captures the expected
result summary for the expanded retain test suite.
"""
from __future__ import annotations

from pathlib import Path


def run_test() -> None:
    repo_root = Path(__file__).resolve().parents[2]
    report = repo_root / "reports" / "audit_retain_20260420_v6.md"

    assert report.exists(), f"Missing report file: {report}"
    content = report.read_text(encoding="utf-8")

    required_snippets = [
        "# Audit Report — Retain Tests",
        "## Summary",
        "## Failure Details",
        "Total: 17 passed, 3 failed, 0 errors",
        "test_dialogue_action_effect.py",
        "test_dialogue_conference_experience.py",
        "test_dialogue_team_collaboration.py",
        "AssertionError: Expected a caching/Redis action_effect fact",
        "AssertionError: Entity 'NeurIPS' not found",
        "AssertionError: Missing 'habit' fact. Got: {'experience', 'world'}",
    ]

    missing = [item for item in required_snippets if item not in content]
    assert not missing, f"Report missing expected snippets: {missing}"

    print("OK  retain audit v6 report exists and contains expected summary")


def main() -> None:
    run_test()
    print("All task741 retain audit v6 artifact tests passed.")


if __name__ == "__main__":
    main()
