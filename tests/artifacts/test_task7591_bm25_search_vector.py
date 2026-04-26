"""Task 759.1 artifact tests: BM25 native path uses search_vector column.

Verification that retrieval.py BM25 native branch uses stored search_vector
column instead of inline to_tsvector workaround.
"""

from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))


def test_bm25_native_path_uses_search_vector_column() -> None:
    """BM25 native path uses search_vector column, not inline to_tsvector."""
    from cogmem_api.engine.search import retrieval

    source = open(retrieval.__file__, encoding="utf-8").read()

    assert "search_vector" in source, "search_vector reference missing from retrieval.py"
    assert "ts_rank_cd(search_vector," in source, \
        "BM25 score expr does not use search_vector column"
    assert "search_vector @@ to_tsquery" in source, \
        "BM25 where clause does not use search_vector column"

    print("PASS: test_bm25_native_path_uses_search_vector_column")


def _main() -> None:
    tests = [test_bm25_native_path_uses_search_vector_column]
    passed = 0
    failed = 0
    for test in tests:
        try:
            test()
            passed += 1
        except Exception as exc:
            print(f"FAIL: {test.__name__}: {exc}")
            failed += 1
    print(f"\nResults: {passed}/1 passed")
    if failed:
        print(f"FAILED: {failed} test(s)")
        sys.exit(1)
    print("ALL TESTS PASSED")


if __name__ == "__main__":
    _main()
