"""Task 758 artifact tests: Retrieval quality schema in memory_engine._safe_ddl.

Alembic migration files were removed in S24.7 (project uses _safe_ddl pattern,
not Alembic). These tests verify the equivalent schema is applied via
memory_engine.py initialize() _safe_ddl blocks.
"""

from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

ENGINE_PATH = os.path.join(
    os.path.dirname(__file__), "..", "..", "cogmem_api", "engine", "memory_engine.py"
)


def _read_engine() -> str:
    with open(ENGINE_PATH, encoding="utf-8") as f:
        return f.read()


def test_migration_has_all_required_indexes() -> None:
    """memory_engine.py _safe_ddl creates all required indexes for retrieval quality."""
    source = _read_engine()

    required = [
        "idx_memory_units_search_vector",
        "idx_memory_units_tags",
        "idx_memory_links_entity_covering",
        "idx_memory_links_to_type_weight",
    ]
    for idx_name in required:
        assert idx_name in source, f"Missing index in memory_engine _safe_ddl: {idx_name}"

    fact_types = ["world", "experience", "opinion", "habit", "intention", "action_effect"]
    for ft in fact_types:
        idx_name = f"idx_mu_emb_{ft}"
        assert idx_name in source, f"Missing partial HNSW index in memory_engine: {idx_name}"

    print("PASS: test_migration_has_all_required_indexes")


def test_migration_search_vector_includes_raw_snippet() -> None:
    """search_vector generated column in _safe_ddl includes both text and raw_snippet."""
    source = _read_engine()
    assert "search_vector" in source, "search_vector column missing from memory_engine"
    assert "raw_snippet" in source, "raw_snippet not included in search_vector expression"
    assert "to_tsvector('english'," in source, "to_tsvector expression not found"
    print("PASS: test_migration_search_vector_includes_raw_snippet")


def test_chunk_id_safe_ddl_present() -> None:
    """chunk_id column is created via _safe_ddl in memory_engine (S24.7)."""
    source = _read_engine()
    assert "chunk_id" in source, "chunk_id not found in memory_engine"
    assert "ADD COLUMN IF NOT EXISTS chunk_id text" in source, \
        "chunk_id _safe_ddl ALTER TABLE statement not found"
    assert "idx_memory_units_chunk_id" in source, \
        "chunk_id partial index not found in memory_engine"
    print("PASS: test_chunk_id_safe_ddl_present")


def _main() -> None:
    tests = [
        test_migration_has_all_required_indexes,
        test_migration_search_vector_includes_raw_snippet,
        test_chunk_id_safe_ddl_present,
    ]
    passed = 0
    failed = 0
    for test in tests:
        try:
            test()
            passed += 1
        except Exception as exc:
            print(f"FAIL: {test.__name__}: {exc}")
            failed += 1
    print(f"\nResults: {passed}/3 passed")
    if failed:
        print(f"FAILED: {failed} test(s)")
        sys.exit(1)
    print("ALL TESTS PASSED")


if __name__ == "__main__":
    _main()
