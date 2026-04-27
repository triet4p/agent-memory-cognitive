"""Task 768: Snippet budget deduplication by document_id.

Verifies:
1. seen_doc_ids set exists in snippet_budget loop of memory_engine.py
2. text field is NEVER set to None (only raw_snippet)
"""

import ast
import sys


def test_seen_doc_ids_set_exists():
    path = "cogmem_api/engine/memory_engine.py"
    with open(path, "r", encoding="utf-8") as f:
        source = f.read()

    tree = ast.parse(source)

    found = False
    for node in ast.walk(tree):
        if isinstance(node, ast.Name) and node.id == "seen_doc_ids":
            found = True
            break

    assert found, f"seen_doc_ids not found in {path}"


def test_text_never_set_to_none():
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

    assert 'item["text"] = None' not in snippet_budget_block, (
        'text field must never be set to None — it is the extracted fact '
        "and is required for generation model context"
    )


if __name__ == "__main__":
    test_seen_doc_ids_set_exists()
    test_text_never_set_to_none()
    print("2/2 PASS")
    sys.exit(0)