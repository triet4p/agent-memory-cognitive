"""Task 758 artifact tests: Alembic migration for retrieval quality schema.

Verification that migration file exists with correct revision chain.
"""

from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))


def test_migration_exists_with_correct_chain() -> None:
    """Migration 20260426_0002 exists and has correct revision chain."""
    migration_path = os.path.join(
        os.path.dirname(__file__), "..", "..",
        "cogmem_api", "alembic", "versions", "20260426_0002_retrieval_quality.py"
    )
    assert os.path.exists(migration_path), f"Migration file not found: {migration_path}"

    source = open(migration_path, encoding="utf-8").read()
    assert 'revision = "20260426_0002"' in source, "Wrong revision in migration"
    assert 'down_revision = "20260330_0001"' in source, "Wrong down_revision in migration"
    print("PASS: test_migration_exists_with_correct_chain")


def test_migration_has_all_required_indexes() -> None:
    """Migration creates all required indexes for retrieval quality."""
    migration_path = os.path.join(
        os.path.dirname(__file__), "..", "..",
        "cogmem_api", "alembic", "versions", "20260426_0002_retrieval_quality.py"
    )
    source = open(migration_path, encoding="utf-8").read()

    required = [
        "idx_memory_units_search_vector",
        "idx_memory_units_tags",
        "idx_memory_links_entity_covering",
        "idx_memory_links_to_type_weight",
    ]
    for idx_name in required:
        assert idx_name in source, f"Missing index: {idx_name}"
        assert f'drop_index("{idx_name}"' in source, f"Missing drop for {idx_name} in downgrade()"

    fact_types = ["world", "experience", "opinion", "habit", "intention", "action_effect"]
    for ft in fact_types:
        idx_name_in_source = "idx_mu_emb_{ft}"
        assert idx_name_in_source in source, \
            f"Missing partial HNSW index template for idx_mu_emb_{ft}"
        create_pattern = "CREATE INDEX idx_mu_emb_{ft}"
        assert create_pattern in source, \
            f"Missing CREATE INDEX for idx_mu_emb_{ft}"
        drop_pattern = 'drop_index(f"idx_mu_emb_{ft}"'
        assert drop_pattern in source, \
            f"Missing drop_index for idx_mu_emb_{ft} in downgrade()"

    print("PASS: test_migration_has_all_required_indexes")


def test_migration_search_vector_includes_raw_snippet() -> None:
    """search_vector generated column includes both text and raw_snippet."""
    migration_path = os.path.join(
        os.path.dirname(__file__), "..", "..",
        "cogmem_api", "alembic", "versions", "20260426_0002_retrieval_quality.py"
    )
    source = open(migration_path, encoding="utf-8").read()
    assert "search_vector" in source, "search_vector column missing from migration"
    assert "raw_snippet" in source, "raw_snippet not included in search_vector expression"
    assert "to_tsvector('english'," in source, "to_tsvector expression not found"
    print("PASS: test_migration_search_vector_includes_raw_snippet")


def _main() -> None:
    tests = [
        test_migration_exists_with_correct_chain,
        test_migration_has_all_required_indexes,
        test_migration_search_vector_includes_raw_snippet,
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
