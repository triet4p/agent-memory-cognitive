"""Task 772: raw_snippet = chunk text, not session text.

Verifies:
1. fact_extraction.py uses chunk_text (not content.content) for raw_snippet
2. memory_engine.py uses chunk_id in dedup loop (not seen_doc_ids)
"""

import ast
import sys


def test_fact_extraction_uses_chunk_text():
    path = "cogmem_api/engine/retain/fact_extraction.py"
    with open(path, "r", encoding="utf-8") as f:
        source = f.read()

    tree = ast.parse(source)

    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == "_normalize_llm_facts":
            func_source = ast.unparse(node)
            assert "raw_snippet=chunk_text" in func_source, (
                "_normalize_llm_facts must use raw_snippet=chunk_text, not content.content"
            )
            assert "raw_snippet=content.content" not in func_source, (
                "_normalize_llm_facts must NOT use raw_snippet=content.content (full session)"
            )
            return

    raise AssertionError("_normalize_llm_facts not found in fact_extraction.py")


def test_memory_engine_uses_chunk_id_dedup():
    path = "cogmem_api/engine/memory_engine.py"
    with open(path, "r", encoding="utf-8") as f:
        source = f.read()

    snippet_budget_block = None
    lines = source.split("\n")
    for i, line in enumerate(lines):
        if "snippet_budget is not None" in line:
            snippet_budget_block = "\n".join(lines[i : i + 20])
            break

    assert snippet_budget_block is not None, "snippet_budget block not found"

    assert "seen_chunk_ids" in snippet_budget_block, (
        "Dedup must use seen_chunk_ids (chunk-level dedup)"
    )
    assert "seen_doc_ids" not in snippet_budget_block, (
        "Dedup must not use seen_doc_ids (session-level dedup is too coarse)"
    )
    assert "chunk_id = item.get" in snippet_budget_block, (
        "Dedup must read chunk_id from item, with fallback to document_id"
    )


if __name__ == "__main__":
    test_fact_extraction_uses_chunk_text()
    test_memory_engine_uses_chunk_id_dedup()
    print("2/2 PASS")
    sys.exit(0)