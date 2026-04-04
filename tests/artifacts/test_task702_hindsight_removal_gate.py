from __future__ import annotations

from pathlib import Path


def assert_required_files(repo_root: Path) -> None:
    required = [
        repo_root / "reports" / "hindsight_removal_readiness.md",
        repo_root / "logs" / "task_702_summary.md",
        repo_root / "tests" / "artifacts" / "test_task702_hindsight_removal_gate.py",
    ]
    missing = [str(path.relative_to(repo_root)) for path in required if not path.exists()]
    assert not missing, f"Missing task702 files/artifacts: {missing}"


def assert_no_runtime_imports(repo_root: Path) -> None:
    violations: list[str] = []
    for file_path in (repo_root / "cogmem_api").rglob("*.py"):
        text = file_path.read_text(encoding="utf-8")
        if "from hindsight_api" in text or "import hindsight_api" in text:
            violations.append(str(file_path.relative_to(repo_root)))

    assert not violations, f"Runtime isolation violated in cogmem_api: {violations}"


def assert_report_contract(repo_root: Path, report_text: str) -> None:
    required_snippets = [
        "## Gate Results",
        "Decision: NO-GO",
        "Blocker B1",
        "Blocker B2",
        "hindsight-client>=0.4.19",
        "scripts/run_hindsight.ps1",
        "scripts/test_hindsight.py",
    ]
    missing = [snippet for snippet in required_snippets if snippet not in report_text]
    assert not missing, f"Readiness report missing required contract snippets: {missing}"


def assert_pyproject_alignment(repo_root: Path, report_text: str) -> None:
    pyproject = (repo_root / "pyproject.toml").read_text(encoding="utf-8")
    has_hindsight_dep = "hindsight-client>=0.4.19" in pyproject

    assert has_hindsight_dep, "Expected hindsight-client dependency to still exist for current NO-GO gate baseline"
    assert "hindsight-client>=0.4.19" in report_text, "Report must mention current packaging blocker"


def assert_cli_and_docker_contract(repo_root: Path, report_text: str) -> None:
    pyproject = (repo_root / "pyproject.toml").read_text(encoding="utf-8")
    docker_sh = (repo_root / "scripts" / "docker.sh").read_text(encoding="utf-8")
    docker_ps1 = (repo_root / "scripts" / "docker.ps1").read_text(encoding="utf-8")

    assert 'cogmem-api = "cogmem_api.main:main"' in pyproject, "CogMem CLI entrypoint missing"

    forbidden_runtime = ["HINDSIGHT_API_", "ghcr.io/vectorize-io/hindsight"]
    for token in forbidden_runtime:
        assert token not in docker_sh, f"docker.sh contains legacy runtime token: {token}"
        assert token not in docker_ps1, f"docker.ps1 contains legacy runtime token: {token}"

    assert "G3 - Docker contract" in report_text, "Report must include docker contract gate"
    assert "G4 - CLI contract clarity" in report_text, "Report must include CLI contract gate"


def main() -> None:
    repo_root = Path(__file__).resolve().parents[2]
    assert_required_files(repo_root)

    report_text = (repo_root / "reports" / "hindsight_removal_readiness.md").read_text(encoding="utf-8")

    assert_no_runtime_imports(repo_root)
    assert_report_contract(repo_root, report_text)
    assert_pyproject_alignment(repo_root, report_text)
    assert_cli_and_docker_contract(repo_root, report_text)

    print("Task 702 hindsight removal readiness gate checks passed.")


if __name__ == "__main__":
    main()
