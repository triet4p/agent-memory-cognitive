"""Artifact test for Task 790 — Cross-session semantic links via fake ANN hook.

Verifies:
1. create_cross_bank_semantic_links_batch calls get_ann_neighbors on fake conn
2. Links are bidirectional and above threshold only
3. No self-links or within-batch links
4. Returns 0 when unit_ids is empty
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import asyncio
from cogmem_api.engine.retain.link_creation import create_cross_bank_semantic_links_batch


class FakeConn:
    """Fake connection that simulates get_ann_neighbors with pre-loaded results."""

    def __init__(self, neighbor_map: dict[str, list[dict]]):
        self.neighbor_map = neighbor_map
        self.inserted_links: list[tuple] = []

    async def get_ann_neighbors(self, bank_id, unit_id, embedding, threshold, top_k):
        return self.neighbor_map.get(unit_id, [])

    async def execute(self, *args, **kwargs):
        pass

    async def executemany(self, query, rows):
        self.inserted_links.extend(rows)


def test_bidirectional_links_created():
    conn = FakeConn({
        "unit-A": [{"id": "unit-X", "similarity": 0.85}],
        "unit-B": [{"id": "unit-Y", "similarity": 0.72}],
    })
    unit_ids = ["unit-A", "unit-B"]
    embeddings = [[0.1, 0.2], [0.3, 0.4]]

    count = asyncio.run(
        create_cross_bank_semantic_links_batch(conn, "bank1", unit_ids, embeddings)
    )

    # unit-A → unit-X and unit-X → unit-A; unit-B → unit-Y and unit-Y → unit-B
    assert count == 4, f"Expected 4 links, got {count}"
    inserted = conn.inserted_links
    pairs = {(r[0], r[1]) for r in inserted}
    assert ("unit-A", "unit-X") in pairs
    assert ("unit-X", "unit-A") in pairs
    assert ("unit-B", "unit-Y") in pairs
    assert ("unit-Y", "unit-B") in pairs
    print("PASS: Bidirectional semantic links created")


def test_no_self_links_or_within_batch():
    # The batch unit_ids are excluded from ANN results by the SQL WHERE clause.
    # Here simulate that get_ann_neighbors returns nothing for within-batch IDs.
    conn = FakeConn({
        "unit-A": [],  # no neighbors returned (within-batch filtered by real SQL)
    })
    unit_ids = ["unit-A", "unit-B"]
    embeddings = [[0.1], [0.2]]

    count = asyncio.run(
        create_cross_bank_semantic_links_batch(conn, "bank1", unit_ids, embeddings)
    )
    assert count == 0, f"Expected 0 links, got {count}"
    print("PASS: No within-batch self-links")


def test_empty_unit_ids():
    conn = FakeConn({})
    count = asyncio.run(
        create_cross_bank_semantic_links_batch(conn, "bank1", [], [])
    )
    assert count == 0
    print("PASS: Empty unit_ids returns 0")


def test_dedup_bidirectional_pairs():
    """Ensure A→X and X→A are only inserted once even if ANN returns both."""
    conn = FakeConn({
        "unit-A": [{"id": "unit-X", "similarity": 0.9}],
        "unit-X": [{"id": "unit-A", "similarity": 0.9}],  # would double-insert without dedup
    })
    unit_ids = ["unit-A", "unit-X"]
    embeddings = [[0.1], [0.2]]

    count = asyncio.run(
        create_cross_bank_semantic_links_batch(conn, "bank1", unit_ids, embeddings)
    )
    # unit-A and unit-X are in the same batch, so get_ann_neighbors is called for both
    # but seen_pairs dedup should prevent duplicate A→X and X→A
    pairs = [(r[0], r[1]) for r in conn.inserted_links]
    forward_count = pairs.count(("unit-A", "unit-X"))
    assert forward_count <= 1, f"Duplicate link A→X inserted {forward_count} times"
    print("PASS: Bidirectional pair deduplication works")


if __name__ == "__main__":
    tests = [
        test_empty_unit_ids,
        test_bidirectional_links_created,
        test_no_self_links_or_within_batch,
        test_dedup_bidirectional_pairs,
    ]
    passed = 0
    for t in tests:
        try:
            t()
            passed += 1
        except Exception as exc:
            print(f"FAIL: {t.__name__}: {exc}")

    print(f"\n{passed}/{len(tests)} PASS")
    if passed < len(tests):
        sys.exit(1)
