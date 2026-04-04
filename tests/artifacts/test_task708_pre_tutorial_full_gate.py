from __future__ import annotations

from pathlib import Path


def assert_required_outputs(repo_root: Path) -> None:
    required = [
        repo_root / "reports" / "pre_tutorial_full_gate.md",
        repo_root / "logs" / "task_708_summary.md",
        repo_root / "tests" / "artifacts" / "test_task708_pre_tutorial_full_gate.py",
    ]
    missing = [str(path.relative_to(repo_root)) for path in required if not path.exists()]
    assert not missing, f"Missing task708 outputs: {missing}"


def assert_report_regression_results(report_text: str) -> None:
    required = [
        "uv run python tests/artifacts/test_task702_hindsight_removal_gate.py",
        "uv run python tests/artifacts/test_task703_removal_playbook_contract.py",
        "uv run python tests/artifacts/test_task705_c1_full_gate.py",
        "uv run python tests/artifacts/test_task706_c3_sum_default_gate.py",
        "uv run python tests/artifacts/test_task707_c4_adaptive_full_gate.py",
        "| `PASS` |",
    ]
    missing = [snippet for snippet in required if snippet not in report_text]
    assert not missing, f"Pre-tutorial report missing regression evidence snippets: {missing}"


def assert_c1_to_c4_checklist(report_text: str) -> None:
    required = [
        "## Checklist C1-C4",
        "| C1 |",
        "| C2 |",
        "| C3 |",
        "| C4 |",
        "| `PASS` |",
    ]
    missing = [snippet for snippet in required if snippet not in report_text]
    assert not missing, f"Pre-tutorial report missing C1-C4 checklist snippets: {missing}"


def assert_gate_decision(report_text: str) -> None:
    required = [
        "## Gate Decision",
        "Decision: PASS",
        "Tutorial unlock:",
        "YES",
    ]
    missing = [snippet for snippet in required if snippet not in report_text]
    assert not missing, f"Pre-tutorial gate decision contract missing: {missing}"


def assert_log_contract(repo_root: Path) -> None:
    log_text = (repo_root / "logs" / "task_708_summary.md").read_text(encoding="utf-8")
    required = [
        "## Scope",
        "## Outputs Created",
        "## Verification Strategy Applied",
        "reports/pre_tutorial_full_gate.md",
        "tests/artifacts/test_task708_pre_tutorial_full_gate.py",
    ]
    missing = [snippet for snippet in required if snippet not in log_text]
    assert not missing, f"Task708 summary missing required contract snippets: {missing}"


def main() -> None:
    repo_root = Path(__file__).resolve().parents[2]
    assert_required_outputs(repo_root)

    report_text = (repo_root / "reports" / "pre_tutorial_full_gate.md").read_text(encoding="utf-8")
    assert_report_regression_results(report_text)
    assert_c1_to_c4_checklist(report_text)
    assert_gate_decision(report_text)
    assert_log_contract(repo_root)

    print("Task 708 pre-tutorial full gate checks passed.")


if __name__ == "__main__":
    main()
