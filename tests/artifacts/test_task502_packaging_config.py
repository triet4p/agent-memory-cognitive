from __future__ import annotations

import asyncio
import importlib
import os
import sys
import tomllib
from pathlib import Path


def assert_required_files(repo_root: Path) -> None:
    required = [
        repo_root / "cogmem_api" / "config.py",
        repo_root / "cogmem_api" / "pg0.py",
        repo_root / "cogmem_api" / "engine" / "memory_engine.py",
        repo_root / "pyproject.toml",
        repo_root / "logs" / "task_502_summary.md",
    ]
    missing = [str(path.relative_to(repo_root)) for path in required if not path.exists()]
    assert not missing, f"Missing T5.2 files: {missing}"


def assert_isolation(repo_root: Path) -> None:
    scope = [
        repo_root / "cogmem_api" / "config.py",
        repo_root / "cogmem_api" / "pg0.py",
        repo_root / "cogmem_api" / "engine" / "memory_engine.py",
    ]
    violating: list[str] = []
    for file_path in scope:
        text = file_path.read_text(encoding="utf-8")
        if "hindsight_api" in text:
            violating.append(str(file_path.relative_to(repo_root)))

    assert not violating, f"Found forbidden hindsight imports: {violating}"


def assert_packaging_contract(repo_root: Path) -> None:
    pyproject_path = repo_root / "pyproject.toml"
    pyproject = tomllib.loads(pyproject_path.read_text(encoding="utf-8"))

    project = pyproject.get("project", {})
    scripts = project.get("scripts", {})
    assert scripts.get("cogmem-api") == "cogmem_api.main:main", "Missing or invalid cogmem-api console script"

    optional_deps = project.get("optional-dependencies", {})
    embedded_db = optional_deps.get("embedded-db")
    assert isinstance(embedded_db, list), "embedded-db optional dependency group is missing"
    assert any(dep.startswith("pg0-embedded") for dep in embedded_db), "embedded-db must include pg0-embedded"


def _restore_env(backup: dict[str, str | None]) -> None:
    for key, value in backup.items():
        if value is None:
            os.environ.pop(key, None)
        else:
            os.environ[key] = value


def run_runtime_config_behavior() -> None:
    import cogmem_api.config as config_module

    env_keys = [
        "COGMEM_API_DATABASE_URL",
        "COGMEM_API_DATABASE_SCHEMA",
        "COGMEM_API_HOST",
        "COGMEM_API_PORT",
        "COGMEM_API_LOG_LEVEL",
        "COGMEM_API_WORKERS",
        "COGMEM_API_LLM_PROVIDER",
        "COGMEM_API_LLM_MODEL",
        "COGMEM_API_LLM_API_KEY",
        "COGMEM_API_DB_POOL_MIN_SIZE",
        "COGMEM_API_DB_POOL_MAX_SIZE",
    ]
    backup = {key: os.environ.get(key) for key in env_keys}

    try:
        for key in env_keys:
            os.environ.pop(key, None)

        config_module = importlib.reload(config_module)
        default_config = config_module._get_raw_config()
        assert default_config.database_url == "pg0"
        assert default_config.database_schema == "public"
        assert default_config.host == "0.0.0.0"
        assert default_config.port == 8888
        assert default_config.log_level == "info"
        assert default_config.workers == 1

        os.environ["COGMEM_API_DATABASE_URL"] = "postgresql://u:p@db:5432/cogmem"
        os.environ["COGMEM_API_DATABASE_SCHEMA"] = "tenant_1"
        os.environ["COGMEM_API_HOST"] = "127.0.0.10"
        os.environ["COGMEM_API_PORT"] = "9100"
        os.environ["COGMEM_API_LOG_LEVEL"] = "debug"
        os.environ["COGMEM_API_WORKERS"] = "3"
        os.environ["COGMEM_API_LLM_PROVIDER"] = "openai"
        os.environ["COGMEM_API_LLM_MODEL"] = "gpt-4o-mini"
        os.environ["COGMEM_API_LLM_API_KEY"] = "secret"
        os.environ["COGMEM_API_DB_POOL_MIN_SIZE"] = "4"
        os.environ["COGMEM_API_DB_POOL_MAX_SIZE"] = "12"

        config_module = importlib.reload(config_module)
        runtime_config = config_module._get_raw_config()

        assert runtime_config.database_url == "postgresql://u:p@db:5432/cogmem"
        assert runtime_config.database_schema == "tenant_1"
        assert runtime_config.host == "127.0.0.10"
        assert runtime_config.port == 9100
        assert runtime_config.log_level == "debug"
        assert runtime_config.workers == 3
        assert runtime_config.llm_provider == "openai"
        assert runtime_config.llm_model == "gpt-4o-mini"
        assert runtime_config.llm_api_key == "secret"
        assert runtime_config.db_pool_min_size == 4
        assert runtime_config.db_pool_max_size == 12
    finally:
        _restore_env(backup)
        importlib.reload(config_module)


def run_pg0_parser_behavior() -> None:
    from cogmem_api.pg0 import parse_pg0_url

    assert parse_pg0_url("pg0") == (True, "cogmem", None)
    assert parse_pg0_url("pg0://my-instance") == (True, "my-instance", None)
    assert parse_pg0_url("pg0://my-instance:5544") == (True, "my-instance", 5544)
    assert parse_pg0_url("postgresql://user:pass@localhost:5432/db") == (False, None, None)


def run_memory_engine_pg0_behavior() -> None:
    import cogmem_api.engine.memory_engine as module

    original_embedded = module.EmbeddedPostgres
    original_create_pool = module.asyncpg.create_pool

    class FakeEmbeddedPostgres:
        instances: list["FakeEmbeddedPostgres"] = []

        def __init__(self, **kwargs):
            self.kwargs = kwargs
            self.stopped = False
            self.__class__.instances.append(self)

        async def is_running(self) -> bool:
            return False

        async def ensure_running(self) -> str:
            return "postgresql://embedded:embedded@127.0.0.1:5544/cogmem"

        async def stop(self) -> None:
            self.stopped = True

    class FakePool:
        def __init__(self):
            self.closed = False

        async def close(self) -> None:
            self.closed = True

    fake_pool = FakePool()

    async def fake_create_pool(db_url: str, min_size: int, max_size: int):
        assert db_url == "postgresql://embedded:embedded@127.0.0.1:5544/cogmem"
        assert min_size >= 1
        assert max_size >= min_size
        return fake_pool

    module.EmbeddedPostgres = FakeEmbeddedPostgres
    module.asyncpg.create_pool = fake_create_pool

    try:
        async def scenario() -> None:
            engine = module.MemoryEngine(db_url="pg0://instance-a:5544")
            await engine.initialize()

            assert engine.initialized is True
            assert engine.pool is fake_pool
            assert engine.db_url == "postgresql://embedded:embedded@127.0.0.1:5544/cogmem"
            assert FakeEmbeddedPostgres.instances, "Embedded pg0 helper should be created"
            assert FakeEmbeddedPostgres.instances[0].kwargs["name"] == "instance-a"
            assert FakeEmbeddedPostgres.instances[0].kwargs["port"] == 5544

            await engine.close()
            assert fake_pool.closed is True
            assert FakeEmbeddedPostgres.instances[0].stopped is True
            assert engine.initialized is False

        asyncio.run(scenario())
    finally:
        module.EmbeddedPostgres = original_embedded
        module.asyncpg.create_pool = original_create_pool


def main() -> None:
    repo_root = Path(__file__).resolve().parents[2]
    repo_root_str = str(repo_root)
    if repo_root_str not in sys.path:
        sys.path.insert(0, repo_root_str)

    assert_required_files(repo_root)
    assert_isolation(repo_root)
    assert_packaging_contract(repo_root)
    run_runtime_config_behavior()
    run_pg0_parser_behavior()
    run_memory_engine_pg0_behavior()
    print("Task 502 packaging config check passed.")


if __name__ == "__main__":
    main()
