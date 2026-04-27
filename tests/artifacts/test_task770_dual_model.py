"""Task 770: Dual model (Ministral-3B retain + Gemma-4 generation).

Verifies:
1. MemoryEngine._build_generate_llm_config method exists in memory_engine.py
2. http.py /generate endpoint calls _build_generate_llm_config (not _build_retain_llm_config)
3. config.py has COGMEM_API_GENERATE_LLM_MODEL constant
"""

import ast
import sys


def test_build_generate_llm_config_method_exists():
    path = "cogmem_api/engine/memory_engine.py"
    with open(path, "r", encoding="utf-8") as f:
        source = f.read()

    tree = ast.parse(source)

    found = False
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == "_build_generate_llm_config":
            found = True
            break

    assert found, "_build_generate_llm_config method not found in memory_engine.py"


def test_generate_endpoint_uses_generate_llm_config():
    path = "cogmem_api/api/http.py"
    with open(path, "r", encoding="utf-8") as f:
        source = f.read()

    tree = ast.parse(source)

    for node in ast.walk(tree):
        if isinstance(node, ast.AsyncFunctionDef) and node.name == "generate_answer":
            source_lines = ast.unparse(node)
            assert "_build_generate_llm_config" in source_lines, (
                "/generate endpoint must call _build_generate_llm_config"
            )
            assert "_build_retain_llm_config" not in source_lines, (
                "/generate endpoint must NOT call _build_retain_llm_config"
            )
            return

    raise AssertionError("generate_answer function not found in http.py")


def test_config_has_generate_llm_model_constant():
    path = "cogmem_api/config.py"
    with open(path, "r", encoding="utf-8") as f:
        source = f.read()

    assert 'ENV_GENERATE_LLM_MODEL = "COGMEM_API_GENERATE_LLM_MODEL"' in source, (
        "ENV_GENERATE_LLM_MODEL constant not found in config.py"
    )


if __name__ == "__main__":
    test_build_generate_llm_config_method_exists()
    test_generate_endpoint_uses_generate_llm_config()
    test_config_has_generate_llm_model_constant()
    print("3/3 PASS")
    sys.exit(0)