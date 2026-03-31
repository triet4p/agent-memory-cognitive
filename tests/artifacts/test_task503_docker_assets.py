from __future__ import annotations

import os
import shutil
import subprocess
import sys
import time
import urllib.error
import urllib.request
import uuid
from pathlib import Path


def assert_required_files(repo_root: Path) -> None:
    required = [
        repo_root / "docker" / "standalone" / "Dockerfile",
        repo_root / "docker" / "standalone" / "start-all.sh",
        repo_root / "docker" / "docker-compose" / "external-pg" / "docker-compose.yaml",
        repo_root / ".env.example",
        repo_root / "logs" / "task_503_summary.md",
    ]
    missing = [str(path.relative_to(repo_root)) for path in required if not path.exists()]
    assert not missing, f"Missing T5.3 files: {missing}"


def assert_isolation(repo_root: Path) -> None:
    scope = [
        repo_root / "docker" / "standalone" / "Dockerfile",
        repo_root / "docker" / "standalone" / "start-all.sh",
        repo_root / "docker" / "docker-compose" / "external-pg" / "docker-compose.yaml",
        repo_root / ".env.example",
    ]
    violations: list[str] = []
    for path in scope:
        text = path.read_text(encoding="utf-8")
        if "hindsight_api" in text:
            violations.append(str(path.relative_to(repo_root)))
    assert not violations, f"Found forbidden hindsight_api references: {violations}"


def assert_dockerfile_contract(repo_root: Path) -> None:
    dockerfile = (repo_root / "docker" / "standalone" / "Dockerfile").read_text(encoding="utf-8")
    required_snippets = [
        "FROM python:3.13-slim",
        "uv sync --frozen --extra embedded-db",
        'COGMEM_API_COMMAND="python -m cogmem_api.main"',
        "COPY docker/standalone/start-all.sh /app/start-all.sh",
        "EXPOSE 8888",
    ]
    missing = [snippet for snippet in required_snippets if snippet not in dockerfile]
    assert not missing, f"Dockerfile is missing expected snippets: {missing}"


def assert_start_script_contract(repo_root: Path) -> None:
    script = (repo_root / "docker" / "standalone" / "start-all.sh").read_text(encoding="utf-8")
    required_snippets = [
        "COGMEM_API_COMMAND",
        "COGMEM_API_HEALTH_URL",
        "COGMEM_API_STARTUP_WAIT_SECONDS",
        "COGMEM_WAIT_FOR_DEPS",
        "COGMEM_API_DATABASE_URL",
        "curl -sf",
    ]
    missing = [snippet for snippet in required_snippets if snippet not in script]
    assert not missing, f"start-all.sh is missing expected snippets: {missing}"


def assert_compose_contract(repo_root: Path) -> None:
    compose = (repo_root / "docker" / "docker-compose" / "external-pg" / "docker-compose.yaml").read_text(
        encoding="utf-8"
    )
    required_snippets = [
        "pgvector/pgvector",
        "services:",
        "db:",
        "cogmem:",
        "docker/standalone/Dockerfile",
        "COGMEM_API_DATABASE_URL",
        "depends_on:",
    ]
    missing = [snippet for snippet in required_snippets if snippet not in compose]
    assert not missing, f"docker-compose external-pg is missing expected snippets: {missing}"


def assert_env_example_contract(repo_root: Path) -> None:
    env_content = (repo_root / ".env.example").read_text(encoding="utf-8")
    required_keys = [
        "COGMEM_API_HOST=",
        "COGMEM_API_PORT=",
        "COGMEM_API_DATABASE_URL=",
        "COGMEM_DB_USER=",
        "COGMEM_DB_PASSWORD=",
        "COGMEM_DB_NAME=",
    ]
    missing = [key for key in required_keys if key not in env_content]
    assert not missing, f".env.example missing required keys: {missing}"


def maybe_run_docker_smoke(repo_root: Path) -> None:
    docker_bin = shutil.which("docker")
    should_run = os.getenv("COGMEM_TASK503_RUN_DOCKER_SMOKE", "0") == "1"

    if docker_bin is None:
        print("Task 503: Docker binary not found; skipping optional docker smoke.")
        return

    if not should_run:
        print("Task 503: optional docker smoke skipped (set COGMEM_TASK503_RUN_DOCKER_SMOKE=1 to enable).")
        return

    tag = f"cogmem-task503-{uuid.uuid4().hex[:8]}"
    container = f"{tag}-ctr"

    build_cmd = [
        docker_bin,
        "build",
        "-f",
        str(repo_root / "docker" / "standalone" / "Dockerfile"),
        "-t",
        tag,
        str(repo_root),
    ]
    subprocess.run(build_cmd, check=True)

    run_cmd = [
        docker_bin,
        "run",
        "--rm",
        "-d",
        "--name",
        container,
        "-p",
        "18888:8888",
        "-e",
        "COGMEM_API_DATABASE_URL=pg0",
        tag,
    ]
    subprocess.run(run_cmd, check=True)

    try:
        health_url = "http://127.0.0.1:18888/health"
        deadline = time.time() + 90
        while time.time() < deadline:
            try:
                with urllib.request.urlopen(health_url, timeout=3) as response:
                    assert response.status == 200, f"Expected 200 from /health, got {response.status}"
                    body = response.read().decode("utf-8")
                    assert "healthy" in body, "Health response body did not contain 'healthy'"
                    print("Task 503: docker smoke passed.")
                    return
            except (urllib.error.URLError, AssertionError, Exception):
                time.sleep(2)

        raise AssertionError("Timed out waiting for Dockerized CogMem health endpoint")
    finally:
        subprocess.run([docker_bin, "rm", "-f", container], check=False)


def main() -> None:
    repo_root = Path(__file__).resolve().parents[2]
    repo_root_str = str(repo_root)
    if repo_root_str not in sys.path:
        sys.path.insert(0, repo_root_str)

    assert_required_files(repo_root)
    assert_isolation(repo_root)
    assert_dockerfile_contract(repo_root)
    assert_start_script_contract(repo_root)
    assert_compose_contract(repo_root)
    assert_env_example_contract(repo_root)
    maybe_run_docker_smoke(repo_root)
    print("Task 503 docker assets check passed.")


if __name__ == "__main__":
    main()
