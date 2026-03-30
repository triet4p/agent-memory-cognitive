from __future__ import annotations

import ast
import importlib
import re
import sys
from pathlib import Path


def parse_check_constraint_values(pattern: str, source_text: str) -> list[str]:
    match = re.search(pattern, source_text)
    if not match:
        return []
    raw_values = match.group(1)
    return [v.strip().strip("'") for v in raw_values.split(",")]


def assert_files_exist(repo_root: Path) -> tuple[Path, Path]:
    models_path = repo_root / "cogmem_api" / "models.py"
    config_path = repo_root / "cogmem_api" / "config.py"

    assert models_path.exists(), "Missing cogmem_api/models.py"
    assert config_path.exists(), "Missing cogmem_api/config.py"
    return models_path, config_path


def assert_schema_classes(source_text: str) -> None:
    module = ast.parse(source_text)
    class_names = {node.name for node in module.body if isinstance(node, ast.ClassDef)}
    expected = {
        "RequestContext",
        "Base",
        "Document",
        "MemoryUnit",
        "Entity",
        "UnitEntity",
        "EntityCooccurrence",
        "MemoryLink",
        "Bank",
    }
    missing = sorted(expected - class_names)
    assert not missing, f"Missing expected schema classes in cogmem_api/models.py: {missing}"


def assert_baseline_constraints(source_text: str) -> None:
    fact_types = parse_check_constraint_values(r"fact_type\s+IN\s*\(([^)]+)\)", source_text)
    expected_fact_types = {"world", "experience", "opinion"}
    assert expected_fact_types.issubset(set(fact_types)), (
        "Forked schema does not preserve baseline fact_type values. "
        f"Expected at least {sorted(expected_fact_types)}, got {fact_types}"
    )

    link_types = parse_check_constraint_values(r"link_type\s+IN\s*\(([^)]+)\)", source_text)
    expected_link_types = {"temporal", "semantic", "entity"}
    assert expected_link_types.issubset(set(link_types)), (
        "Forked schema does not preserve baseline link_type values. "
        f"Expected at least {sorted(expected_link_types)}, got {link_types}"
    )


def assert_namespace_isolation(models_text: str, config_text: str) -> None:
    assert "hindsight_api" not in models_text, "Found forbidden hindsight_api reference in cogmem_api/models.py"
    assert "hindsight_api" not in config_text, "Found forbidden hindsight_api reference in cogmem_api/config.py"


def assert_embedding_config(config_text: str) -> None:
    assert "EMBEDDING_DIMENSION" in config_text, "EMBEDDING_DIMENSION is required for Vector column declarations"


def assert_runtime_import(repo_root: Path) -> None:
    repo_root_str = str(repo_root)
    if repo_root_str not in sys.path:
        sys.path.insert(0, repo_root_str)

    imported = importlib.import_module("cogmem_api.models")
    assert imported is not None, "Unable to import cogmem_api.models"



def main() -> None:
    repo_root = Path(__file__).resolve().parents[2]
    models_path, config_path = assert_files_exist(repo_root)

    models_text = models_path.read_text(encoding="utf-8")
    config_text = config_path.read_text(encoding="utf-8")

    compile(models_text, str(models_path), "exec")
    compile(config_text, str(config_path), "exec")

    assert_schema_classes(models_text)
    assert_baseline_constraints(models_text)
    assert_namespace_isolation(models_text, config_text)
    assert_embedding_config(config_text)
    assert_runtime_import(repo_root)

    print("Task 101 schema fork check passed.")


if __name__ == "__main__":
    main()
