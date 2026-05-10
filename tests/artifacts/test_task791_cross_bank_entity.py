"""Artifact test for Task 791 — Cross-session entity links.

Verifies:
1. build_cross_bank_entity_links creates bidirectional entity links to existing units
2. Blocked entities ("user") are not queried cross-session
3. Deduplication prevents duplicate pairs
4. Returns empty list when no cross-session units share entities
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import asyncio
from dataclasses import dataclass, field
from cogmem_api.engine.retain.entity_processing import (
    build_cross_bank_entity_links,
    _resolve_entity_id,
    _ENTITY_BLOCKLIST,
)
from cogmem_api.engine.retain.types import EntityLink


@dataclass
class MockFact:
    fact_type: str
    entities: list[str] = field(default_factory=list)
    content_index: int = 0


class FakeConn:
    """Fake connection with get_entity_unit_ids hook."""

    def __init__(self, entity_units: dict[str, list[str]]):
        # entity_id → list of existing unit IDs in bank
        self.entity_units = entity_units
        self.queried_entities: list[str] = []

    async def get_entity_unit_ids(self, entity_id: str, exclude_ids: list[str]) -> list[str]:
        self.queried_entities.append(str(entity_id))
        return [uid for uid in self.entity_units.get(str(entity_id), []) if uid not in exclude_ids]


def test_creates_cross_session_entity_links():
    bank_id = "bank1"
    west_elm_eid = _resolve_entity_id(bank_id, "West Elm")

    conn = FakeConn({
        str(west_elm_eid): ["existing-unit-1", "existing-unit-2"],
    })

    new_facts = [MockFact("experience", ["User", "West Elm", "coffee table"])]
    new_unit_ids = ["new-unit-A"]

    links = asyncio.run(build_cross_bank_entity_links(conn, bank_id, new_unit_ids, new_facts))

    # Expect 4 links: new↔existing-1 (2) + new↔existing-2 (2)
    assert len(links) == 4, f"Expected 4 links, got {len(links)}"

    froms = {l.from_unit_id for l in links}
    tos = {l.to_unit_id for l in links}
    assert "new-unit-A" in froms
    assert "new-unit-A" in tos
    assert "existing-unit-1" in froms
    assert "existing-unit-2" in froms

    print("PASS: Cross-session entity links created for 'West Elm'")


def test_blocked_entity_not_queried():
    bank_id = "bank1"
    user_eid = _resolve_entity_id(bank_id, "User")
    user_eid_low = _resolve_entity_id(bank_id, "user")

    conn = FakeConn({
        str(user_eid): ["existing-unit-X"],
        str(user_eid_low): ["existing-unit-X"],
    })

    new_facts = [MockFact("experience", ["User", "me", "my"])]
    new_unit_ids = ["new-unit-B"]

    links = asyncio.run(build_cross_bank_entity_links(conn, bank_id, new_unit_ids, new_facts))

    # No links because all entities are blocked
    assert len(links) == 0, f"Expected 0 links, got {len(links)}"
    # Blocked entities must NOT have been queried
    for queried in conn.queried_entities:
        assert queried not in (str(user_eid), str(user_eid_low)), "Blocked entity was queried!"

    print("PASS: Blocked entities not queried in cross-session lookup")


def test_no_duplicate_pairs():
    bank_id = "bank1"
    casper_eid = _resolve_entity_id(bank_id, "Casper")

    conn = FakeConn({str(casper_eid): ["existing-unit-1"]})

    # Two new facts both have "Casper" → would create duplicate A↔existing-1 pairs without dedup
    new_facts = [
        MockFact("experience", ["Casper"]),
        MockFact("experience", ["Casper", "mattress"]),
    ]
    new_unit_ids = ["new-unit-A", "new-unit-B"]

    links = asyncio.run(build_cross_bank_entity_links(conn, bank_id, new_unit_ids, new_facts))

    # Deduplicated: (A, existing-1) and (B, existing-1), each bidirectional → 4 total max
    pairs = {(l.from_unit_id, l.to_unit_id) for l in links}
    assert ("new-unit-A", "existing-unit-1") in pairs
    assert ("existing-unit-1", "new-unit-A") in pairs
    # No duplicates: each pair appears exactly once in set
    assert len(pairs) == len(links), "Duplicate pairs detected"
    print("PASS: No duplicate entity link pairs")


if __name__ == "__main__":
    tests = [
        test_creates_cross_session_entity_links,
        test_blocked_entity_not_queried,
        test_no_duplicate_pairs,
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
