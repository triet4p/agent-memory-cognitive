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
        repo_root / "docker" / "test-image.sh",
        repo_root / "scripts" / "smoke-test-cogmem.sh",
        repo_root / "README.md",
        repo_root / "logs" / "task_504_summary.md",
    ]
    missing = [str(path.relative_to(repo_root)) for path in required if not path.exists()]
    assert not missing, f"Missing T5.4 files: {missing}"


def assert_isolation(repo_root: Path) -> None:
    scope = [
        repo_root / "docker" / "test-image.sh",
        repo_root / "scripts" / "smoke-test-cogmem.sh",
    ]

    violations: list[str] = []
    for path in scope:
        text = path.read_text(encoding="utf-8")
        if "hindsight_api" in text:
            violations.append(str(path.relative_to(repo_root)))
        if "hindsight:" in text:
            violations.append(str(path.relative_to(repo_root)))

    assert not violations, f"Found forbidden HINDSIGHT runtime references: {violations}"


def assert_script_contract(repo_root: Path) -> None:
    docker_test = (repo_root / "docker" / "test-image.sh").read_text(encoding="utf-8")
    required_test_snippets = [
        "scripts/smoke-test-cogmem.sh",
        "COGMEM_API_DATABASE_URL",
        "/health",
        "docker run",
    ]
    missing_test = [snippet for snippet in required_test_snippets if snippet not in docker_test]
    assert not missing_test, f"docker/test-image.sh missing required snippets: {missing_test}"

    smoke_script = (repo_root / "scripts" / "smoke-test-cogmem.sh").read_text(encoding="utf-8")
    required_smoke_snippets = [
        "/v1/default/banks/$BANK_ID/memories",
        "/v1/default/banks/$BANK_ID/memories/recall",
        "retain",
        "recall",
    ]
    missing_smoke = [snippet for snippet in required_smoke_snippets if snippet not in smoke_script]
    assert not missing_smoke, f"scripts/smoke-test-cogmem.sh missing required snippets: {missing_smoke}"


def assert_readme_contract(repo_root: Path) -> None:
    readme = (repo_root / "README.md").read_text(encoding="utf-8")
    required_snippets = [
        "docker/standalone/Dockerfile",
        "docker/docker-compose/external-pg/docker-compose.yaml",
        "scripts/smoke-test-cogmem.sh",
        "docker/test-image.sh",
    ]
    missing = [snippet for snippet in required_snippets if snippet not in readme]
    assert not missing, f"README missing Docker runbook snippets: {missing}"


def run_api_smoke_behavior(repo_root: Path) -> None:
    repo_root_str = str(repo_root)
    if repo_root_str not in sys.path:
        sys.path.insert(0, repo_root_str)

    from fastapi.testclient import TestClient

    from cogmem_api import MemoryEngine
    from cogmem_api.api.http import create_app

    app = create_app(memory=MemoryEngine(), initialize_memory=False)

    with TestClient(app) as client:
        bank_id = "task504-smoke"
        retain_resp = client.post(
            f"/v1/default/banks/{bank_id}/memories",
            json={"items": [{"content": "Alice is a software engineer who likes Python."}]},
        )
        assert retain_resp.status_code == 200
        retain_json = retain_resp.json()
        assert retain_json.get("success") is True
        assert retain_json.get("count") == 1

        recall_resp = client.post(
            f"/v1/default/banks/{bank_id}/memories/recall",
            json={"query": "What does Alice do?"},
        )
        assert recall_resp.status_code == 200
        recall_json = recall_resp.json()
        results = recall_json.get("results", [])
        assert results, "Expected at least one recall result"
        assert any("software engineer" in item.get("text", "") for item in results)


def maybe_run_docker_smoke(repo_root: Path) -> None:
    should_run = os.getenv("COGMEM_TASK504_RUN_DOCKER_SMOKE", "0") == "1"
    docker_bin = shutil.which("docker")

    if docker_bin is None:
        print("Task 504: Docker binary not found; skipping optional Docker smoke.")
        return

    if not should_run:
        print("Task 504: optional Docker smoke skipped (set COGMEM_TASK504_RUN_DOCKER_SMOKE=1 to enable).")
        return

    tag = f"cogmem-task504-{uuid.uuid4().hex[:8]}"
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
        "18889:8888",
        "-e",
        "COGMEM_API_DATABASE_URL=pg0",
        tag,
    ]
    subprocess.run(run_cmd, check=True)

    try:
        health_url = "http://127.0.0.1:18889/health"
        retain_url = "http://127.0.0.1:18889/v1/default/banks/task504/memories"
        recall_url = "http://127.0.0.1:18889/v1/default/banks/task504/memories/recall"

        deadline = time.time() + 120
        while time.time() < deadline:
            try:
                with urllib.request.urlopen(health_url, timeout=3) as response:
                    if response.status == 200:
                        break
            except Exception:
                time.sleep(2)
        else:
            raise AssertionError("Timed out waiting for Dockerized CogMem health endpoint")

        retain_payload = b'{"items": [{"content": "Alice is a software engineer who likes Python."}]}'
        retain_req = urllib.request.Request(
            retain_url,
            data=retain_payload,
            method="POST",
            headers={"Content-Type": "application/json"},
        )
        with urllib.request.urlopen(retain_req, timeout=5) as response:
            assert response.status == 200, "Retain request failed in Docker smoke"

        recall_payload = b'{"query": "What does Alice do?"}'
        recall_req = urllib.request.Request(
            recall_url,
            data=recall_payload,
            method="POST",
            headers={"Content-Type": "application/json"},
        )
        with urllib.request.urlopen(recall_req, timeout=5) as response:
            assert response.status == 200, "Recall request failed in Docker smoke"
            body = response.read().decode("utf-8")
            assert "results" in body and "Alice" in body, "Unexpected recall response body"

        print("Task 504: Docker retain/recall smoke passed.")
    finally:
        subprocess.run([docker_bin, "rm", "-f", container], check=False)


def main() -> None:
    repo_root = Path(__file__).resolve().parents[2]
    assert_required_files(repo_root)
    assert_isolation(repo_root)
    assert_script_contract(repo_root)
    assert_readme_contract(repo_root)
    run_api_smoke_behavior(repo_root)
    maybe_run_docker_smoke(repo_root)
    print("Task 504 Docker smoke contract check passed.")


if __name__ == "__main__":
    main()
