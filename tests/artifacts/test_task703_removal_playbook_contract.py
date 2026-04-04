from __future__ import annotations

from pathlib import Path


def assert_required_files(repo_root: Path) -> None:
    required = [
        repo_root / "docs" / "hindsight_removal_playbook.md",
        repo_root / "logs" / "task_703_summary.md",
        repo_root / "tests" / "artifacts" / "test_task703_removal_playbook_contract.py",
    ]
    missing = [str(path.relative_to(repo_root)) for path in required if not path.exists()]
    assert not missing, f"Missing task703 files/artifacts: {missing}"


def assert_plan_alignment(repo_root: Path) -> None:
    plan_text = (repo_root / "docs" / "PLAN.md").read_text(encoding="utf-8")
    assert "docs/hindsight_removal_playbook.md" in plan_text, "PLAN is not aligned with T7.3 playbook output path"


def assert_playbook_sections(playbook_text: str) -> None:
    required = [
        "## Định nghĩa GO/NO-GO",
        "## Pha 1 - Dry-run",
        "## Pha 2 - Commit-run",
        "## Rollback Plan",
        "## Tiêu chí hoàn tất T7.3",
    ]
    missing = [snippet for snippet in required if snippet not in playbook_text]
    assert not missing, f"Playbook missing required sections: {missing}"


def assert_playbook_contracts(playbook_text: str) -> None:
    required = [
        "reports/hindsight_removal_dryrun_verdict.md",
        "reports/hindsight_removal_commitrun_report.md",
        "rg -n \"from hindsight_api|import hindsight_api\" cogmem_api",
        "uv run python tests/artifacts/test_task701_idea_coverage_matrix.py",
        "uv run python tests/artifacts/test_task702_hindsight_removal_gate.py",
        "git revert <commit_sha>",
        "không thực hiện xóa hindsight_api",
    ]
    missing = [snippet for snippet in required if snippet not in playbook_text]
    assert not missing, f"Playbook missing required operational contracts: {missing}"


def assert_no_destructive_git_reset(playbook_text: str) -> None:
    forbidden = ["git reset --hard", "git checkout --"]
    hits = [token for token in forbidden if token in playbook_text]
    assert not hits, f"Playbook contains forbidden destructive command: {hits}"


def main() -> None:
    repo_root = Path(__file__).resolve().parents[2]
    assert_required_files(repo_root)
    assert_plan_alignment(repo_root)

    playbook_text = (repo_root / "docs" / "hindsight_removal_playbook.md").read_text(encoding="utf-8")

    assert_playbook_sections(playbook_text)
    assert_playbook_contracts(playbook_text)
    assert_no_destructive_git_reset(playbook_text)

    print("Task 703 removal playbook contract checks passed.")


if __name__ == "__main__":
    main()
