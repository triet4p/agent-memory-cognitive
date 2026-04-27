"""Task 775: Fix chunk_id pipeline — per-content document_id.

Verifies:
1. orchestrator.py chunk_id assignment uses per-content document_id
   (not top-level document_id as a gate condition)
2. chunk_id format is {bank_id}_{document_id}_{chunk_index}
"""

import ast
import sys


def test_chunk_id_from_per_content_document_id():
    path = "cogmem_api/engine/retain/orchestrator.py"
    with open(path, "r", encoding="utf-8") as f:
        source = f.read()

    tree = ast.parse(source)

    for node in ast.walk(tree):
        if isinstance(node, ast.AsyncFunctionDef) and node.name == "_db_write_work":
            func_source = ast.unparse(node)

            assert (
                "contents_dicts[extracted_fact.content_index].get('document_id')" in func_source
            ), (
                "chunk_id must be generated using per-content document_id "
                "(contents_dicts[extracted_fact.content_index].get('document_id'))"
            )

            assert "f'{bank_id}_{fact_doc_id}_{extracted_fact.chunk_index}'" in func_source, (
                "chunk_id must follow format {bank_id}_{document_id}_{chunk_index}"
            )

            assert (
                "fact_doc_id" in func_source and "or document_id" in func_source
            ), (
                "fact_doc_id must fallback to top-level document_id when per-content doc_id is absent"
            )

            assert not (
                "if chunks and document_id:" in func_source
            ), (
                "chunk_id assignment must NOT be gated behind 'if chunks and document_id:' — "
                "that was the bug. It must use per-content document_id."
            )
            return

    raise AssertionError("_db_write_work not found in orchestrator.py")


if __name__ == "__main__":
    test_chunk_id_from_per_content_document_id()
    print("1/1 PASS")
    sys.exit(0)
