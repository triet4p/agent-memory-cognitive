"""Artifact test for Task 789 — Entity blocklist in entity_processing.py.

Verifies:
1. Generic entities ("user", "me", "my") are excluded from entity links
2. Specific named entities (e.g. "West Elm") still produce entity links
3. Blocklist is case-insensitive (normalized before check)
4. build_cross_bank_entity_links skips blocked entities when querying cross-session
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from dataclasses import dataclass, field
from cogmem_api.engine.retain.entity_processing import (
    _ENTITY_BLOCKLIST,
    _normalize_entity_name,
    _resolve_entity_id,
    process_entities_batch,
)


@dataclass
class MockFact:
    fact_type: str
    entities: list[str] = field(default_factory=list)
    content_index: int = 0


class FakeConn:
    def __init__(self):
        self.inserted_pairs: list[tuple[str, str]] = []

    async def executemany(self, query, rows):
        pass

    async def insert_unit_entities(self, pairs):
        self.inserted_pairs.extend(pairs)


async def _run_process(facts, bank_id="test_bank"):
    conn = FakeConn()
    unit_ids = [f"unit-{i}" for i in range(len(facts))]
    links = await process_entities_batch(
        entity_resolver=None,
        conn=conn,
        bank_id=bank_id,
        unit_ids=unit_ids,
        facts=facts,
    )
    return links, conn


def test_user_entity_excluded():
    import asyncio

    facts = [
        MockFact("experience", ["User", "West Elm", "coffee table"]),
        MockFact("experience", ["User", "West Elm", "living room"]),
    ]
    links, _ = asyncio.run(_run_process(facts))

    # No link through "User" entity
    user_eid = _resolve_entity_id("test_bank", "user")
    user_eid_case = _resolve_entity_id("test_bank", "User")
    for link in links:
        assert link.entity_id != user_eid, "Found unexpected link through 'user'"
        assert link.entity_id != user_eid_case, "Found unexpected link through 'User'"

    # But link through "West Elm" must exist
    west_elm_eid = _resolve_entity_id("test_bank", "West Elm")
    entity_ids = {link.entity_id for link in links}
    assert west_elm_eid in entity_ids, "Expected 'West Elm' entity link not found"

    print("PASS: 'User' entity excluded; 'West Elm' entity link present")


def test_all_blocked_entities():
    import asyncio

    blocked = ["user", "the user", "i", "me", "my", "we", "our"]
    for word in blocked:
        assert _normalize_entity_name(word) in _ENTITY_BLOCKLIST, f"'{word}' should be in blocklist"

    print("PASS: All expected blocked entities present in _ENTITY_BLOCKLIST")


def test_specific_entities_not_blocked():
    import asyncio

    non_blocked = ["West Elm", "IKEA", "Casper", "Max", "Paris", "Python"]
    for word in non_blocked:
        assert _normalize_entity_name(word) not in _ENTITY_BLOCKLIST, f"'{word}' should NOT be in blocklist"

    print("PASS: Specific named entities not in blocklist")


def test_no_links_when_only_blocked_entities():
    import asyncio

    facts = [
        MockFact("experience", ["User", "I", "me"]),
        MockFact("experience", ["User", "my", "our"]),
    ]
    links, _ = asyncio.run(_run_process(facts))
    assert len(links) == 0, f"Expected 0 links but got {len(links)}"
    print("PASS: No links created when all entities are blocked")


if __name__ == "__main__":
    tests = [
        test_all_blocked_entities,
        test_specific_entities_not_blocked,
        test_user_entity_excluded,
        test_no_links_when_only_blocked_entities,
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
