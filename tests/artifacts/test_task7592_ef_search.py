"""Task 759.2 artifact tests: HNSW ef_search set to 200 in pool init.

Verification that memory_engine.py sets hnsw.ef_search=200 per-connection
for accurate HNSW recall.
"""

from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))


def test_ef_search_set_in_pool_init() -> None:
    """Pool init callback sets hnsw.ef_search=200 for all connections."""
    from cogmem_api.engine import memory_engine

    source = open(memory_engine.__file__, encoding="utf-8").read()

    assert "SET hnsw.ef_search = 200" in source, \
        "hnsw.ef_search = 200 not found in memory_engine.py"
    assert "_init_pool_connection" in source, \
        "Pool init callback not found in memory_engine.py"
    assert "init=_init_pool_connection" in source, \
        "init=_init_pool_connection not passed to asyncpg.create_pool"

    print("PASS: test_ef_search_set_in_pool_init")


def _main() -> None:
    tests = [test_ef_search_set_in_pool_init]
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
