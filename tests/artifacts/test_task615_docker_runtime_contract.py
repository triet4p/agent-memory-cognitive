from __future__ import annotations

import os
import shutil
import subprocess
from pathlib import Path


def assert_required_files(repo_root: Path) -> None:
    required = [
        repo_root / "scripts" / "docker.sh",
        repo_root / "scripts" / "docker.ps1",
        repo_root / "scripts" / "smoke-test-cogmem.sh",
        repo_root / "scripts" / "smoke-test-cogmem.ps1",
        repo_root / "docker" / "test-image.sh",
        repo_root / "docker" / "test-image.ps1",
        repo_root / "README.md",
        repo_root / "logs" / "task_615_summary.md",
        repo_root / "tests" / "artifacts" / "test_task615_docker_runtime_contract.py",
    ]
    missing = [str(path.relative_to(repo_root)) for path in required if not path.exists()]
    assert not missing, f"Missing B5 files/artifacts: {missing}"


def assert_isolation(repo_root: Path) -> None:
    scope = [
        repo_root / "scripts" / "docker.sh",
        repo_root / "scripts" / "docker.ps1",
        repo_root / "scripts" / "smoke-test-cogmem.sh",
        repo_root / "scripts" / "smoke-test-cogmem.ps1",
        repo_root / "docker" / "test-image.sh",
        repo_root / "docker" / "test-image.ps1",
        repo_root / "README.md",
        repo_root / "tests" / "artifacts" / "test_task615_docker_runtime_contract.py",
    ]

    forbidden_tokens = (
        "hindsight" + "_api",
        "ghcr.io/vectorize-io/" + "hindsight",
        "hindsight" + ":latest",
    )
    violations: list[str] = []
    for file_path in scope:
        text = file_path.read_text(encoding="utf-8")
        if any(token in text for token in forbidden_tokens):
            violations.append(str(file_path.relative_to(repo_root)))

    assert not violations, f"Isolation violation detected: {violations}"


def assert_scripts_docker_contract(repo_root: Path) -> None:
    script_sh = (repo_root / "scripts" / "docker.sh").read_text(encoding="utf-8")
    script_ps1 = (repo_root / "scripts" / "docker.ps1").read_text(encoding="utf-8")

    required_snippets = [
        "MODE=\"${1:-embedded}\"",
        "COGMEM_EXTERNAL_DATABASE_URL",
        "COGMEM_DOCKER_INCLUDE_LOCAL_MODELS",
        "COGMEM_DOCKER_PRELOAD_ML_MODELS",
        "docker compose",
        "COGMEM_API_DATABASE_URL=pg0",
        "COGMEM_API_LLM_PROVIDER",
        "COGMEM_API_LLM_BASE_URL",
        "COGMEM_API_LLM_MODEL",
        "COGMEM_API_LLM_TIMEOUT",
        "COGMEM_API_RETAIN_LLM_TIMEOUT",
        "COGMEM_API_REFLECT_LLM_TIMEOUT",
        "COGMEM_API_RETAIN_MAX_COMPLETION_TOKENS",
        "COGMEM_API_RETAIN_EXTRACTION_MODE",
        "docker run",
        "embedded)",
        "external)",
    ]
    missing_sh = [snippet for snippet in required_snippets if snippet not in script_sh]
    assert not missing_sh, f"scripts/docker.sh missing contract snippets: {missing_sh}"

    required_ps1_snippets = [
        "param(",
        "ValidateSet(\"embedded\", \"external\")",
        "COGMEM_EXTERNAL_DATABASE_URL",
        "COGMEM_DOCKER_INCLUDE_LOCAL_MODELS",
        "COGMEM_DOCKER_PRELOAD_ML_MODELS",
        "docker compose",
        "COGMEM_API_DATABASE_URL=pg0",
        "COGMEM_API_LLM_PROVIDER",
        "COGMEM_API_LLM_BASE_URL",
        "COGMEM_API_LLM_MODEL",
        "COGMEM_API_LLM_TIMEOUT",
        "COGMEM_API_RETAIN_LLM_TIMEOUT",
        "COGMEM_API_REFLECT_LLM_TIMEOUT",
        "COGMEM_API_RETAIN_MAX_COMPLETION_TOKENS",
        "COGMEM_API_RETAIN_EXTRACTION_MODE",
        "docker run",
    ]
    missing_ps1 = [snippet for snippet in required_ps1_snippets if snippet not in script_ps1]
    assert not missing_ps1, f"scripts/docker.ps1 missing contract snippets: {missing_ps1}"


def assert_smoke_script_contract(repo_root: Path) -> None:
    smoke_sh = (repo_root / "scripts" / "smoke-test-cogmem.sh").read_text(encoding="utf-8")
    smoke_ps1 = (repo_root / "scripts" / "smoke-test-cogmem.ps1").read_text(encoding="utf-8")

    required_sh = [
        "/v1/default/banks/$BANK_ID/memories",
        "/v1/default/banks/$BANK_ID/memories/recall",
    ]
    missing_sh = [snippet for snippet in required_sh if snippet not in smoke_sh]
    assert not missing_sh, f"scripts/smoke-test-cogmem.sh missing snippets: {missing_sh}"

    required_ps1 = [
        "/v1/default/banks/$bankId/memories",
        "/v1/default/banks/$bankId/memories/recall",
        "Invoke-RestMethod",
    ]
    missing_ps1 = [snippet for snippet in required_ps1 if snippet not in smoke_ps1]
    assert not missing_ps1, f"scripts/smoke-test-cogmem.ps1 missing snippets: {missing_ps1}"


def assert_test_image_contract(repo_root: Path) -> None:
    script_sh = (repo_root / "docker" / "test-image.sh").read_text(encoding="utf-8")
    script_ps1 = (repo_root / "docker" / "test-image.ps1").read_text(encoding="utf-8")

    required_sh_snippets = [
        "COGMEM_SMOKE_DATABASE_URL",
        "COGMEM_SMOKE_PG0_VOLUME_DIR",
        "COGMEM_API_LLM_PROVIDER",
        "COGMEM_API_LLM_BASE_URL",
        "COGMEM_API_LLM_MODEL",
        "COGMEM_API_LLM_TIMEOUT",
        "COGMEM_API_RETAIN_LLM_TIMEOUT",
        "COGMEM_API_REFLECT_LLM_TIMEOUT",
        "COGMEM_API_RETAIN_MAX_COMPLETION_TOKENS",
        "COGMEM_API_RETAIN_EXTRACTION_MODE",
        "COGMEM_API_EMBEDDINGS_PROVIDER",
        "COGMEM_SMOKE_REQUIRE_NON_DETERMINISTIC",
        "scripts/smoke-test-cogmem.sh",
        "COGMEM_API_DATABASE_URL=${SMOKE_DATABASE_URL}",
    ]
    missing_sh = [snippet for snippet in required_sh_snippets if snippet not in script_sh]
    assert not missing_sh, f"docker/test-image.sh missing contract snippets: {missing_sh}"

    required_ps1_snippets = [
        "COGMEM_SMOKE_DATABASE_URL",
        "COGMEM_SMOKE_PG0_VOLUME_DIR",
        "COGMEM_API_LLM_PROVIDER",
        "COGMEM_API_LLM_BASE_URL",
        "COGMEM_API_LLM_MODEL",
        "COGMEM_API_LLM_TIMEOUT",
        "COGMEM_API_RETAIN_LLM_TIMEOUT",
        "COGMEM_API_REFLECT_LLM_TIMEOUT",
        "COGMEM_API_RETAIN_MAX_COMPLETION_TOKENS",
        "COGMEM_API_RETAIN_EXTRACTION_MODE",
        "COGMEM_API_EMBEDDINGS_PROVIDER",
        "COGMEM_SMOKE_REQUIRE_NON_DETERMINISTIC",
        "scripts/smoke-test-cogmem.ps1",
        "COGMEM_API_DATABASE_URL=$smokeDatabaseUrl",
    ]
    missing_ps1 = [snippet for snippet in required_ps1_snippets if snippet not in script_ps1]
    assert not missing_ps1, f"docker/test-image.ps1 missing contract snippets: {missing_ps1}"


def assert_readme_contract(repo_root: Path) -> None:
    readme = (repo_root / "README.md").read_text(encoding="utf-8")
    required_snippets = [
        "scripts/docker.sh embedded",
        "scripts/docker.sh external",
        "scripts\\docker.ps1 -Mode embedded",
        "scripts\\docker.ps1 -Mode external",
        "COGMEM_DOCKER_INCLUDE_LOCAL_MODELS",
        "scripts/smoke-test-cogmem.sh",
        "scripts\\smoke-test-cogmem.ps1",
        "docker/test-image.sh",
        "docker\\test-image.ps1",
        "COGMEM_API_LLM_BASE_URL",
        "COGMEM_API_RETAIN_LLM_TIMEOUT",
        "COGMEM_API_RETAIN_EXTRACTION_MODE",
        "COGMEM_SMOKE_DATABASE_URL",
    ]
    missing = [snippet for snippet in required_snippets if snippet not in readme]
    assert not missing, f"README missing B5 contract snippets: {missing}"


def maybe_run_shell_syntax_checks(repo_root: Path) -> None:
    if os.name == "nt":
        print("Task 615: running on Windows host; skip bash syntax checks.")
        return

    bash_bin = shutil.which("bash")
    if not bash_bin:
        print("Task 615: bash not available; skip shell syntax checks.")
        return

    scripts = [
        repo_root / "scripts" / "docker.sh",
        repo_root / "scripts" / "smoke-test-cogmem.sh",
        repo_root / "docker" / "test-image.sh",
    ]
    for script_path in scripts:
        subprocess.run([bash_bin, "-n", str(script_path)], check=True)


def maybe_run_powershell_syntax_checks(repo_root: Path) -> None:
    pwsh_bin = shutil.which("pwsh")
    if not pwsh_bin:
        print("Task 615: pwsh not available; skip PowerShell syntax checks.")
        return

    scripts = [
        repo_root / "scripts" / "docker.ps1",
        repo_root / "scripts" / "smoke-test-cogmem.ps1",
        repo_root / "docker" / "test-image.ps1",
    ]
    for script_path in scripts:
        subprocess.run(
            [
                pwsh_bin,
                "-NoProfile",
                "-Command",
                f"[void][ScriptBlock]::Create((Get-Content -LiteralPath '{script_path}' -Raw))",
            ],
            check=True,
        )


def main() -> None:
    repo_root = Path(__file__).resolve().parents[2]
    assert_required_files(repo_root)
    assert_isolation(repo_root)
    assert_scripts_docker_contract(repo_root)
    assert_smoke_script_contract(repo_root)
    assert_test_image_contract(repo_root)
    assert_readme_contract(repo_root)
    maybe_run_shell_syntax_checks(repo_root)
    maybe_run_powershell_syntax_checks(repo_root)
    print("Task 615 Docker runtime contract check passed.")


if __name__ == "__main__":
    main()
