from __future__ import annotations

from pathlib import Path


def assert_required_files(repo_root: Path) -> None:
    required = [
        repo_root / "pyproject.toml",
        repo_root / "docker" / "standalone" / "Dockerfile",
        repo_root / "docker" / "docker-compose" / "external-pg" / "docker-compose.yaml",
        repo_root / "scripts" / "docker.sh",
        repo_root / "scripts" / "docker.ps1",
        repo_root / "docker" / "test-image.sh",
        repo_root / "docker" / "test-image.ps1",
        repo_root / "logs" / "task_617_summary.md",
        repo_root / "tests" / "artifacts" / "test_task617_docker_unified_runtime.py",
    ]
    missing = [str(path.relative_to(repo_root)) for path in required if not path.exists()]
    assert not missing, f"Missing task617 files/artifacts: {missing}"


def assert_isolation(repo_root: Path) -> None:
    scope = [
        repo_root / "pyproject.toml",
        repo_root / "docker" / "standalone" / "Dockerfile",
        repo_root / "docker" / "docker-compose" / "external-pg" / "docker-compose.yaml",
        repo_root / "scripts" / "docker.sh",
        repo_root / "scripts" / "docker.ps1",
        repo_root / "docker" / "test-image.sh",
        repo_root / "docker" / "test-image.ps1",
        repo_root / "tests" / "artifacts" / "test_task617_docker_unified_runtime.py",
    ]

    forbidden = "hindsight" + "_api"
    violations: list[str] = []
    for file_path in scope:
        text = file_path.read_text(encoding="utf-8")
        if forbidden in text:
            violations.append(str(file_path.relative_to(repo_root)))

    assert not violations, f"Isolation violation detected: {violations}"


def assert_pyproject_local_ml_contract(repo_root: Path) -> None:
    text = (repo_root / "pyproject.toml").read_text(encoding="utf-8")
    required = [
        "[project.optional-dependencies]",
        "local-ml = [",
        "sentence-transformers",
    ]
    missing = [snippet for snippet in required if snippet not in text]
    assert not missing, f"pyproject.toml missing local-ml contract: {missing}"


def assert_dockerfile_local_ml_contract(repo_root: Path) -> None:
    text = (repo_root / "docker" / "standalone" / "Dockerfile").read_text(encoding="utf-8")
    required = [
        "ARG INCLUDE_LOCAL_MODELS=true",
        "ARG PRELOAD_ML_MODELS=false",
        "uv sync --frozen --extra embedded-db --extra local-ml",
        "Skipping local ML model preload",
    ]
    missing = [snippet for snippet in required if snippet not in text]
    assert not missing, f"Dockerfile missing local-ml contract: {missing}"


def assert_compose_unified_contract(repo_root: Path) -> None:
    text = (repo_root / "docker" / "docker-compose" / "external-pg" / "docker-compose.yaml").read_text(
        encoding="utf-8"
    )
    required = [
        "COGMEM_DOCKER_INCLUDE_LOCAL_MODELS",
        "COGMEM_DOCKER_PRELOAD_ML_MODELS",
        "COGMEM_WAIT_FOR_DEPS: true",
        "COGMEM_API_EMBEDDINGS_PROVIDER",
        "COGMEM_API_RERANKER_PROVIDER",
    ]
    missing = [snippet for snippet in required if snippet not in text]
    assert not missing, f"docker compose missing unified runtime contract: {missing}"


def assert_launcher_unified_contract(repo_root: Path) -> None:
    shell_script = (repo_root / "scripts" / "docker.sh").read_text(encoding="utf-8")
    ps_script = (repo_root / "scripts" / "docker.ps1").read_text(encoding="utf-8")

    required_shell = [
        "COGMEM_DOCKER_INCLUDE_LOCAL_MODELS",
        "COGMEM_DOCKER_PRELOAD_ML_MODELS",
        "COGMEM_DOCKER_COMPOSE_FILE",
        "docker compose",
        "up --build",
    ]
    missing_shell = [snippet for snippet in required_shell if snippet not in shell_script]
    assert not missing_shell, f"scripts/docker.sh missing unified launcher contract: {missing_shell}"

    required_ps = [
        "COGMEM_DOCKER_INCLUDE_LOCAL_MODELS",
        "COGMEM_DOCKER_PRELOAD_ML_MODELS",
        "COGMEM_DOCKER_COMPOSE_FILE",
        "docker compose",
        "up --build",
    ]
    missing_ps = [snippet for snippet in required_ps if snippet not in ps_script]
    assert not missing_ps, f"scripts/docker.ps1 missing unified launcher contract: {missing_ps}"


def assert_smoke_guard_contract(repo_root: Path) -> None:
    shell_script = (repo_root / "docker" / "test-image.sh").read_text(encoding="utf-8")
    ps_script = (repo_root / "docker" / "test-image.ps1").read_text(encoding="utf-8")

    required_shell = [
        "COGMEM_SMOKE_REQUIRE_NON_DETERMINISTIC",
        "COGMEM_API_EMBEDDINGS_PROVIDER",
        "Falling back to deterministic embeddings",
    ]
    missing_shell = [snippet for snippet in required_shell if snippet not in shell_script]
    assert not missing_shell, f"docker/test-image.sh missing deterministic guard contract: {missing_shell}"

    required_ps = [
        "COGMEM_SMOKE_REQUIRE_NON_DETERMINISTIC",
        "COGMEM_API_EMBEDDINGS_PROVIDER",
        "Falling back to deterministic embeddings",
    ]
    missing_ps = [snippet for snippet in required_ps if snippet not in ps_script]
    assert not missing_ps, f"docker/test-image.ps1 missing deterministic guard contract: {missing_ps}"


def main() -> None:
    repo_root = Path(__file__).resolve().parents[2]
    assert_required_files(repo_root)
    assert_isolation(repo_root)
    assert_pyproject_local_ml_contract(repo_root)
    assert_dockerfile_local_ml_contract(repo_root)
    assert_compose_unified_contract(repo_root)
    assert_launcher_unified_contract(repo_root)
    assert_smoke_guard_contract(repo_root)
    print("Task 617 Docker unified runtime checks passed.")


if __name__ == "__main__":
    main()
