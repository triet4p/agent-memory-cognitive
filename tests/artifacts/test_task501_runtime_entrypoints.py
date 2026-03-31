from __future__ import annotations

import os
import sys
from pathlib import Path


def assert_required_files(repo_root: Path) -> None:
    required = [
        repo_root / "cogmem_api" / "main.py",
        repo_root / "cogmem_api" / "server.py",
        repo_root / "cogmem_api" / "api" / "__init__.py",
        repo_root / "cogmem_api" / "api" / "http.py",
        repo_root / "logs" / "task_501_summary.md",
    ]
    missing = [str(path.relative_to(repo_root)) for path in required if not path.exists()]
    assert not missing, f"Missing T5.1 files: {missing}"


def assert_isolation(repo_root: Path) -> None:
    scope = [
        repo_root / "cogmem_api" / "main.py",
        repo_root / "cogmem_api" / "server.py",
        repo_root / "cogmem_api" / "api" / "__init__.py",
        repo_root / "cogmem_api" / "api" / "http.py",
    ]

    violating: list[str] = []
    for py_file in scope:
        text = py_file.read_text(encoding="utf-8")
        if "hindsight_api" in text:
            violating.append(str(py_file.relative_to(repo_root)))

    assert not violating, f"Found forbidden hindsight imports: {violating}"


def run_health_endpoint_behavior() -> None:
    from fastapi.testclient import TestClient

    from cogmem_api.api import create_app
    from cogmem_api.engine.memory_engine import MemoryEngine

    memory = MemoryEngine()
    app = create_app(memory=memory, http_api_enabled=True, initialize_memory=True)

    with TestClient(app) as client:
        response = client.get("/health")
        assert response.status_code == 200, response.text
        payload = response.json()
        assert payload["status"] == "healthy"
        assert payload["initialized"] is True
        assert payload["database"]["url_configured"] is False
        assert payload["database"]["connected"] is False

        version_response = client.get("/version")
        assert version_response.status_code == 200, version_response.text
        version_payload = version_response.json()
        assert version_payload["service"] == "cogmem-api"

    assert memory.initialized is False, "Memory should be closed after app shutdown"


def run_cli_parser_behavior() -> None:
    from cogmem_api.main import build_parser

    previous_host = os.environ.get("COGMEM_API_HOST")
    previous_port = os.environ.get("COGMEM_API_PORT")
    previous_log_level = os.environ.get("COGMEM_API_LOG_LEVEL")

    try:
        os.environ["COGMEM_API_HOST"] = "127.0.0.2"
        os.environ["COGMEM_API_PORT"] = "9001"
        os.environ["COGMEM_API_LOG_LEVEL"] = "debug"

        parser = build_parser()
        args = parser.parse_args([])

        assert args.host == "127.0.0.2"
        assert args.port == 9001
        assert args.log_level == "debug"
    finally:
        if previous_host is None:
            os.environ.pop("COGMEM_API_HOST", None)
        else:
            os.environ["COGMEM_API_HOST"] = previous_host

        if previous_port is None:
            os.environ.pop("COGMEM_API_PORT", None)
        else:
            os.environ["COGMEM_API_PORT"] = previous_port

        if previous_log_level is None:
            os.environ.pop("COGMEM_API_LOG_LEVEL", None)
        else:
            os.environ["COGMEM_API_LOG_LEVEL"] = previous_log_level


def run_server_module_import() -> None:
    import cogmem_api.server as server_module

    assert hasattr(server_module, "app"), "ASGI app should be exposed at module level"


def main() -> None:
    repo_root = Path(__file__).resolve().parents[2]
    repo_root_str = str(repo_root)
    if repo_root_str not in sys.path:
        sys.path.insert(0, repo_root_str)

    assert_required_files(repo_root)
    assert_isolation(repo_root)
    run_health_endpoint_behavior()
    run_cli_parser_behavior()
    run_server_module_import()
    print("Task 501 runtime entrypoints check passed.")


if __name__ == "__main__":
    main()
