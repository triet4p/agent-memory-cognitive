from __future__ import annotations

import importlib
import re
import sys
from pathlib import Path


def assert_files_exist(repo_root: Path) -> Path:
    models_path = repo_root / "cogmem_api" / "models.py"
    assert models_path.exists(), "Missing cogmem_api/models.py"
    return models_path


def assert_memory_unit_extensions(models_text: str) -> None:
    assert "raw_snippet" in models_text, "raw_snippet column is missing from MemoryUnit"
    assert "network_type" in models_text, "network_type column is missing from MemoryUnit"

    expected_fact_types = ["habit", "intention", "action_effect"]
    for fact_type in expected_fact_types:
        assert f"'{fact_type}'" in models_text, f"Missing extended fact_type value: {fact_type}"

    expected_network_types = ["habit", "intention", "action_effect"]
    for network_type in expected_network_types:
        assert f"'{network_type}'" in models_text, f"Missing extended network_type value: {network_type}"

    assert "'observation'" not in models_text, "Observation network must be removed from CogMem schema"
    assert "idx_memory_units_observation_date" not in models_text, "Observation-specific index must be removed"


def assert_memory_link_transition_typing(models_text: str) -> None:
    assert "transition_type" in models_text, "transition_type column is missing from MemoryLink"

    expected_link_types = ["temporal", "semantic", "entity", "causal", "s_r_link", "a_o_causal", "transition"]
    for link_type in expected_link_types:
        assert f"'{link_type}'" in models_text, f"Missing extended link_type value: {link_type}"

    removed_link_types = ["causes", "caused_by", "enables", "prevents"]
    for link_type in removed_link_types:
        assert f"'{link_type}'" not in models_text, f"Legacy link_type must be removed from CogMem schema: {link_type}"

    expected_transition_types = [
        "fulfilled_by",
        "abandoned",
        "triggered",
        "enabled_by",
        "revised_to",
        "contradicted_by",
    ]
    for transition_type in expected_transition_types:
        assert f"'{transition_type}'" in models_text, f"Missing transition type value: {transition_type}"

    assert "memory_links_transition_type_usage_check" in models_text, "Missing transition usage check constraint"


def assert_migration_content(migration_text: str) -> None:
    required_upgrade_patterns = [
        r"add_column\(\s*\"memory_units\"\s*,\s*sa\.Column\(\s*\"raw_snippet\"",
        r"add_column\(\s*\"memory_units\"\s*,\s*sa\.Column\(\s*\"network_type\"",
        r"add_column\(\s*\"memory_links\"\s*,\s*sa\.Column\(\s*\"transition_type\"",
        r"memory_units_network_type_check",
        r"memory_links_transition_type_values_check",
        r"memory_links_transition_type_usage_check",
        r"fact_type IN \('world', 'experience', 'opinion', 'habit', 'intention', 'action_effect'\)",
        r"network_type IN \('world', 'experience', 'opinion', 'habit', 'intention', 'action_effect'\)",
        r"link_type IN \('temporal', 'semantic', 'entity', 'causal', 's_r_link', 'a_o_causal', 'transition'\)",
    ]
    for pattern in required_upgrade_patterns:
        assert re.search(pattern, migration_text), f"Missing required migration pattern: {pattern}"

    assert "hindsight_api" not in migration_text, "Migration file must not reference hindsight_api"



def assert_runtime_import(repo_root: Path) -> None:
    repo_root_str = str(repo_root)
    if repo_root_str not in sys.path:
        sys.path.insert(0, repo_root_str)

    imported = importlib.import_module("cogmem_api.models")
    assert imported is not None, "Unable to import cogmem_api.models"


def main() -> None:
    repo_root = Path(__file__).resolve().parents[2]
    models_path = assert_files_exist(repo_root)

    models_text = models_path.read_text(encoding="utf-8")

    compile(models_text, str(models_path), "exec")

    assert_memory_unit_extensions(models_text)
    assert_memory_link_transition_typing(models_text)
    assert_runtime_import(repo_root)

    print("Task 102 schema extensions check passed.")


if __name__ == "__main__":
    main()
