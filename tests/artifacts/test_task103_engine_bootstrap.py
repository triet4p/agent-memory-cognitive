from __future__ import annotations

import asyncio
import importlib
import re
import sys
from pathlib import Path


def assert_engine_files_exist(repo_root: Path) -> tuple[Path, Path, Path]:
    db_utils_path = repo_root / "cogmem_api" / "engine" / "db_utils.py"
    memory_engine_path = repo_root / "cogmem_api" / "engine" / "memory_engine.py"
    init_path = repo_root / "cogmem_api" / "engine" / "__init__.py"

    assert db_utils_path.exists(), "Missing cogmem_api/engine/db_utils.py"
    assert memory_engine_path.exists(), "Missing cogmem_api/engine/memory_engine.py"
    assert init_path.exists(), "Missing cogmem_api/engine/__init__.py"
    return db_utils_path, memory_engine_path, init_path


def assert_namespace_isolation(*texts: str) -> None:
    forbidden = re.compile(r"\bhindsight_api\b")
    for text in texts:
        assert not forbidden.search(text), "Found forbidden hindsight_api reference in CogMem engine files"


def assert_runtime_import_and_bootstrap(repo_root: Path) -> None:
    repo_root_str = str(repo_root)
    if repo_root_str not in sys.path:
        sys.path.insert(0, repo_root_str)

    module = importlib.import_module("cogmem_api.engine.memory_engine")

    assert module.get_current_schema() == "public", "Default schema should be public"
    assert module.fq_table("memory_units") == "public.memory_units", "fq_table should use default schema"

    with module.set_schema_context("tenant_a"):
        assert module.get_current_schema() == "tenant_a", "Schema context override failed"
        assert module.fq_table("memory_units") == "tenant_a.memory_units", "fq_table should use overridden schema"

    assert module.get_current_schema() == "public", "Schema context should reset after context manager"

    module.validate_sql_schema("SELECT * FROM public.memory_units")

    try:
        module.validate_sql_schema("SELECT * FROM memory_units")
    except module.UnqualifiedTableError:
        pass
    else:
        raise AssertionError("validate_sql_schema must fail on unqualified protected table")

    async def bootstrap_without_db() -> None:
        engine = module.MemoryEngine(db_url=None)
        await engine.initialize()
        assert engine.initialized is True, "Engine should mark initialized without db_url"
        assert engine.pool is None, "Pool should remain None when db_url is absent"
        await engine.close()
        assert engine.initialized is False, "Engine should reset initialized flag after close"

    asyncio.run(bootstrap_without_db())



def main() -> None:
    repo_root = Path(__file__).resolve().parents[2]
    db_utils_path, memory_engine_path, init_path = assert_engine_files_exist(repo_root)

    db_utils_text = db_utils_path.read_text(encoding="utf-8")
    memory_engine_text = memory_engine_path.read_text(encoding="utf-8")
    init_text = init_path.read_text(encoding="utf-8")

    compile(db_utils_text, str(db_utils_path), "exec")
    compile(memory_engine_text, str(memory_engine_path), "exec")
    compile(init_text, str(init_path), "exec")

    assert_namespace_isolation(db_utils_text, memory_engine_text, init_text)
    assert_runtime_import_and_bootstrap(repo_root)

    print("Task 103 engine bootstrap check passed.")


if __name__ == "__main__":
    main()
