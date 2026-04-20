"""Artifact test for retain audit report v7 (task 742).

Validates that the latest retest audit report exists and records expected
summary counts and known failing tests.
"""
from __future__ import annotations

from pathlib import Path


def run_test() -> None:
    repo_root = Path(__file__).resolve().parents[2]
    report = repo_root / "reports" / "audit_retain_20260420_v7.md"

    assert report.exists(), f"Missing report file: {report}"
    content = report.read_text(encoding="utf-8")

    required_snippets = [
        "# Audit Report — Retain Tests",
        "## Summary",
        "## Failure Details",
        "Total: 18 passed, 2 failed, 0 errors",
        "test_dialogue_all_six_types.py",
        "test_dialogue_team_collaboration.py",
        "AssertionError: Expected at least 4/6 types",
        "AssertionError: Missing 'habit' fact. Got: {'experience', 'world'}",
    ]

    missing = [snippet for snippet in required_snippets if snippet not in content]
    assert not missing, f"Report missing expected snippets: {missing}"

    print("OK  retain audit v7 report exists and contains expected results")


def main() -> None:
    run_test()
    print("All task742 retain audit v7 artifact tests passed.")


if __name__ == "__main__":
    main()
