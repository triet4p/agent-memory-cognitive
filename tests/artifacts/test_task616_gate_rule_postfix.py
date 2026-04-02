from __future__ import annotations

from pathlib import Path


def assert_required_files(repo_root: Path) -> None:
    required = [
        repo_root / "logs" / "task_616_summary.md",
        repo_root / "tests" / "artifacts" / "test_task616_gate_rule_postfix.py",
        repo_root / "cogmem_api" / "engine" / "memory_engine.py",
        repo_root / "cogmem_api" / "engine" / "retain" / "link_utils.py",
        repo_root / "scripts" / "docker.ps1",
        repo_root / "scripts" / "smoke-test-cogmem.ps1",
        repo_root / "docker" / "test-image.ps1",
    ]
    missing = [str(path.relative_to(repo_root)) for path in required if not path.exists()]
    assert not missing, f"Missing Gate postfix files/artifacts: {missing}"


def assert_isolation(repo_root: Path) -> None:
    scope = [
        repo_root / "cogmem_api" / "engine" / "memory_engine.py",
        repo_root / "cogmem_api" / "engine" / "retain" / "link_utils.py",
        repo_root / "scripts" / "docker.ps1",
        repo_root / "scripts" / "smoke-test-cogmem.ps1",
        repo_root / "docker" / "test-image.ps1",
        repo_root / "tests" / "artifacts" / "test_task616_gate_rule_postfix.py",
    ]

    forbidden = "hindsight" + "_api"
    violations: list[str] = []
    for file_path in scope:
        text = file_path.read_text(encoding="utf-8")
        if forbidden in text:
            violations.append(str(file_path.relative_to(repo_root)))

    assert not violations, f"Isolation violation detected: {violations}"


def assert_memory_bootstrap_contract(repo_root: Path) -> None:
    text = (repo_root / "cogmem_api" / "engine" / "memory_engine.py").read_text(encoding="utf-8")
    required_snippets = [
        "async def _bootstrap_schema_objects",
        "CREATE SCHEMA IF NOT EXISTS",
        "CREATE EXTENSION IF NOT EXISTS vector",
        "Base.metadata.create_all",
        "await self._bootstrap_schema_objects()",
    ]
    missing = [snippet for snippet in required_snippets if snippet not in text]
    assert not missing, f"memory_engine.py missing bootstrap snippets: {missing}"


def assert_link_insert_contract(repo_root: Path) -> None:
    text = (repo_root / "cogmem_api" / "engine" / "retain" / "link_utils.py").read_text(encoding="utf-8")
    required_snippets = [
        "_PLACEHOLDER_ENTITY_ID",
        "INSERT INTO {fq_table(\"entities\")}",
        "COALESCE($5::uuid, $7::uuid)",
        "ON CONFLICT DO NOTHING",
    ]
    missing = [snippet for snippet in required_snippets if snippet not in text]
    assert not missing, f"link_utils.py missing runtime fix snippets: {missing}"


def assert_powershell_param_contract(repo_root: Path) -> None:
    files = [
        repo_root / "scripts" / "docker.ps1",
        repo_root / "scripts" / "smoke-test-cogmem.ps1",
        repo_root / "docker" / "test-image.ps1",
    ]

    violations: list[str] = []
    for file_path in files:
        text = file_path.read_text(encoding="utf-8")
        param_pos = text.find("param(")
        strict_pos = text.find("Set-StrictMode")
        if param_pos == -1 or strict_pos == -1 or param_pos > strict_pos:
            violations.append(str(file_path.relative_to(repo_root)))

    assert not violations, f"PowerShell param placement contract violated: {violations}"


def main() -> None:
    repo_root = Path(__file__).resolve().parents[2]
    assert_required_files(repo_root)
    assert_isolation(repo_root)
    assert_memory_bootstrap_contract(repo_root)
    assert_link_insert_contract(repo_root)
    assert_powershell_param_contract(repo_root)
    print("Task 616 gate postfix checks passed.")


if __name__ == "__main__":
    main()
