"""Artifact test for Task 786 — Query APIs (GET /facts, /facts/all, /relationships, /relationships/by-type).

Verifies:
1. Functions exist with correct signatures
2. Functions produce correct SQL (mocked)
3. No syntax errors
"""

from __future__ import annotations
import sys
import asyncio
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))


def test_fact_storage_exports():
    from cogmem_api.engine.retain import fact_storage
    assert hasattr(fact_storage, "get_facts")
    assert hasattr(fact_storage, "get_all_facts")
    assert hasattr(fact_storage, "get_relationships")
    assert hasattr(fact_storage, "get_relationships_by_type")
    assert callable(fact_storage.get_facts)
    assert callable(fact_storage.get_all_facts)
    assert callable(fact_storage.get_relationships)
    assert callable(fact_storage.get_relationships_by_type)
    print("PASS: fact_storage exports all 4 query functions")


def test_http_routes_defined():
    from cogmem_api.api import http as http_module
    import inspect
    src = inspect.getsource(http_module)
    assert "/v1/default/banks/{bank_id}/facts" in src, "GET /facts route not found"
    assert "/v1/default/banks/{bank_id}/facts/all" in src, "GET /facts/all route not found"
    assert "/v1/default/banks/{bank_id}/relationships" in src, "GET /relationships route not found"
    assert "/v1/default/banks/{bank_id}/relationships/by-type/{link_type}" in src, "GET /relationships/by-type route not found"
    print("PASS: All 4 routes are defined in http.py")


def test_query_function_signatures():
    import inspect
    from cogmem_api.engine.retain import fact_storage

    sig = inspect.signature(fact_storage.get_facts)
    params = list(sig.parameters.keys())
    assert "conn" in params, "get_facts missing 'conn'"
    assert "bank_id" in params, "get_facts missing 'bank_id'"
    assert "keyword" in params, "get_facts missing 'keyword'"
    assert "fact_type" in params, "get_facts missing 'fact_type'"
    assert "limit" in params, "get_facts missing 'limit'"
    assert "offset" in params, "get_facts missing 'offset'"
    print(f"PASS: get_facts signature: {sig}")

    sig2 = inspect.signature(fact_storage.get_relationships)
    params2 = list(sig2.parameters.keys())
    assert "conn" in params2 and "bank_id" in params2 and "limit" in params2 and "offset" in params2
    print(f"PASS: get_relationships signature: {sig2}")

    sig3 = inspect.signature(fact_storage.get_relationships_by_type)
    params3 = list(sig3.parameters.keys())
    assert "link_type" in params3, "get_relationships_by_type missing 'link_type'"
    print(f"PASS: get_relationships_by_type signature: {sig3}")


class MockFactRow:
    def __init__(self, data):
        self._data = data
    def __getitem__(self, key):
        return self._data.get(key)


class MockLinkRow:
    def __init__(self, data):
        self._data = data
    def __getitem__(self, key):
        return self._data.get(key)


async def test_get_facts_makes_correct_query():
    class FactConn:
        def __init__(self):
            self.queries = []
        async def fetch(self, query, *args):
            self.queries.append((query, args))
            return [
                MockFactRow({
                    "id": "unit1", "text": "User bought Tiger I", "fact_type": "experience",
                    "raw_snippet": "bought", "context": "", "occurred_start": None,
                    "occurred_end": None, "mentioned_at": None, "event_date": None,
                    "chunk_id": "p1_0", "document_id": "doc1", "metadata": {},
                    "tags": None, "embedding": [],
                }),
            ]

    from cogmem_api.engine.retain import fact_storage
    conn = FactConn()
    results = await fact_storage.get_facts(conn, "bank1", keyword="Tiger", fact_type="experience", limit=10, offset=0)
    assert len(results) == 1
    assert results[0]["text"] == "User bought Tiger I"
    assert results[0]["fact_type"] == "experience"
    print("PASS: get_facts with keyword+type returns correct result")


async def test_get_all_facts_makes_paginated_query():
    class FactConn:
        def __init__(self):
            self.queries = []
        async def fetch(self, query, *args):
            self.queries.append((query, args))
            return [
                MockFactRow({
                    "id": "unit1", "text": "User bought Tiger I", "fact_type": "experience",
                    "raw_snippet": "bought", "context": "", "occurred_start": None,
                    "occurred_end": None, "mentioned_at": None, "event_date": None,
                    "chunk_id": "p1_0", "document_id": "doc1", "metadata": {},
                    "tags": None, "embedding": [],
                }),
            ]

    from cogmem_api.engine.retain import fact_storage
    conn = FactConn()
    results = await fact_storage.get_all_facts(conn, "bank1", limit=2, offset=5)
    assert len(results) == 1
    query, args = conn.queries[-1]
    assert "LIMIT $2" in query and "OFFSET $3" in query
    print("PASS: get_all_facts with limit=2 offset=5 returns results with pagination")


async def test_get_relationships_returns_link_dicts():
    class LinkConn:
        def __init__(self):
            self.queries = []
        async def fetch(self, query, *args):
            self.queries.append((query, args))
            return [
                MockLinkRow({
                    "from_unit_id": "id1", "to_unit_id": "id2", "link_type": "semantic",
                    "transition_type": None, "weight": 0.95,
                    "from_text": "User bought Tiger I", "from_fact_type": "experience",
                    "to_text": "Tiger I is a tank", "to_fact_type": "world",
                }),
            ]

    from cogmem_api.engine.retain import fact_storage
    conn = LinkConn()
    results = await fact_storage.get_relationships(conn, "bank1", limit=10, offset=0)
    r = results[0] if results else {}
    assert len(results) == 1, f"Expected 1 result, got {len(results)}"
    has_required = all(k in r for k in ("from_unit_id", "to_unit_id", "link_type", "from_text", "to_text"))
    assert has_required, f"Missing required keys. Got: {list(r.keys())}"
    print("PASS: get_relationships returns link dicts with from/to_text")


async def test_get_relationships_by_type_filters():
    class LinkConn:
        def __init__(self):
            self.queries = []
        async def fetch(self, query, *args):
            self.queries.append((query, args))
            return [
                MockLinkRow({
                    "from_unit_id": "id1", "to_unit_id": "id2", "link_type": "semantic",
                    "transition_type": None, "weight": 0.95,
                    "from_text": "User bought Tiger I", "from_fact_type": "experience",
                    "to_text": "Tiger I is a tank", "to_fact_type": "world",
                }),
            ]

    from cogmem_api.engine.retain import fact_storage
    conn = LinkConn()
    results = await fact_storage.get_relationships_by_type(conn, "bank1", "semantic", limit=10, offset=0)
    assert len(results) == 1
    assert all(r["link_type"] == "semantic" for r in results)
    query, args = conn.queries[-1]
    assert "link_type = $2" in query
    print("PASS: get_relationships_by_type(semantic) filters correctly")


def main():
    tests = [
        test_fact_storage_exports,
        test_http_routes_defined,
        test_query_function_signatures,
    ]
    passed = 0
    for test in tests:
        try:
            test()
            passed += 1
        except Exception as exc:
            print(f"  ERROR: {test.__name__} -> {type(exc).__name__}: {exc}")

    async_tests = [
        test_get_facts_makes_correct_query,
        test_get_all_facts_makes_paginated_query,
        test_get_relationships_returns_link_dicts,
        test_get_relationships_by_type_filters,
    ]
    for test in async_tests:
        try:
            asyncio.run(test())
            passed += 1
        except Exception as exc:
            print(f"  ERROR: {test.__name__} -> {type(exc).__name__}: {exc}")

    total = len(tests) + len(async_tests)
    print(f"\n{passed}/{total} PASS")
    return passed == total


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)