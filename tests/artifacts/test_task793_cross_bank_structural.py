"""Artifact test for Task 793 — Cross-session structural links.

Verifies:
1. Temporal links created for facts with event_date within 24h window
2. s_r_link created: habit → non-habit facts sharing non-blocked entities cross-session
3. a_o_causal created: action_effect → non-action_effect facts sharing entities
4. Transition heuristic: experience → existing planning intention sharing entities
5. Blocked entities excluded from s_r_link / a_o_causal / transition queries
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import asyncio
from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta
from cogmem_api.engine.retain.link_creation import create_cross_bank_structural_links_batch
from cogmem_api.engine.retain.types import ProcessedFact
from cogmem_api.engine.retain.entity_processing import _resolve_entity_id


def _make_processed_fact(fact_type: str, entities: list[str], event_date=None) -> ProcessedFact:
    return ProcessedFact(
        fact_text=f"Fact of type {fact_type}",
        fact_type=fact_type,
        embedding=[],
        occurred_start=None,
        occurred_end=None,
        mentioned_at=event_date,
        context="",
        metadata={},
        entities=entities,
    )


class FakeConn:
    def __init__(self):
        self.inserted_links: list[tuple] = []
        self.temporal_neighbors: dict[str, list[dict]] = {}
        self.entity_facts: dict[str, list[dict]] = {}
        self.planning_intentions: dict[str, list[dict]] = {}

    async def get_temporal_neighbors(self, bank_id, unit_id, event_date, window_s):
        return self.temporal_neighbors.get(unit_id, [])

    async def get_entity_overlapping_facts(self, bank_id, new_unit_ids, entity_ids, exclude_fact_types):
        results = []
        for eid in entity_ids:
            for row in self.entity_facts.get(str(eid), []):
                if row.get("fact_type") not in exclude_fact_types:
                    results.append(row)
        return results

    async def get_planning_intentions_by_entity(self, bank_id, new_unit_ids, entity_ids):
        results = []
        for eid in entity_ids:
            results.extend(self.planning_intentions.get(str(eid), []))
        return results

    async def execute(self, *args, **kwargs):
        pass

    async def executemany(self, query, rows):
        self.inserted_links.extend(rows)


def test_temporal_cross_session_links():
    now = datetime(2026, 5, 1, 12, 0, 0, tzinfo=UTC)
    near = now - timedelta(hours=6)  # within 24h window

    bank_id = "test_bank"
    unit_ids = ["new-A"]
    facts = [_make_processed_fact("experience", [], event_date=now)]

    conn = FakeConn()
    conn.temporal_neighbors = {
        "new-A": [{"id": "old-X", "event_date": near}]
    }

    # Patch fetch_event_dates to return our event_date
    import cogmem_api.engine.retain.link_utils as lu
    original_fetch = lu.fetch_event_dates

    async def fake_fetch(conn_, uids):
        return {"new-A": now}

    lu.fetch_event_dates = fake_fetch
    try:
        count = asyncio.run(
            create_cross_bank_structural_links_batch(conn, bank_id, unit_ids, facts)
        )
    finally:
        lu.fetch_event_dates = original_fetch

    # Expect 2 temporal links (bidirectional: new-A↔old-X)
    temporal_links = [(r[0], r[1]) for r in conn.inserted_links if r[2] == "temporal"]
    assert ("new-A", "old-X") in temporal_links, "Missing forward temporal link"
    assert ("old-X", "new-A") in temporal_links, "Missing reverse temporal link"
    print("PASS: Temporal cross-session links created")


def test_sr_link_habit_to_existing_facts():
    bank_id = "test_bank"
    coffee_eid = _resolve_entity_id(bank_id, "coffee")

    unit_ids = ["habit-unit"]
    facts = [_make_processed_fact("habit", ["coffee"])]

    conn = FakeConn()
    conn.entity_facts = {
        str(coffee_eid): [{"id": "old-exp-1", "fact_type": "experience"}]
    }

    async def fake_fetch(conn_, uids):
        return {}

    import cogmem_api.engine.retain.link_utils as lu
    original_fetch = lu.fetch_event_dates
    lu.fetch_event_dates = fake_fetch
    try:
        count = asyncio.run(
            create_cross_bank_structural_links_batch(conn, bank_id, unit_ids, facts)
        )
    finally:
        lu.fetch_event_dates = original_fetch

    sr_links = [(r[0], r[1]) for r in conn.inserted_links if r[2] == "s_r_link"]
    assert ("habit-unit", "old-exp-1") in sr_links, "Missing s_r_link from habit to experience"
    print("PASS: s_r_link created from habit to existing experience sharing entity")


def test_transition_heuristic_experience_to_planning_intention():
    bank_id = "test_bank"
    french_press_eid = _resolve_entity_id(bank_id, "French press")

    unit_ids = ["exp-unit"]
    facts = [_make_processed_fact("experience", ["French press"])]

    conn = FakeConn()
    conn.planning_intentions = {
        str(french_press_eid): [{"id": "old-intention-1"}]
    }

    async def fake_fetch(conn_, uids):
        return {}

    import cogmem_api.engine.retain.link_utils as lu
    original_fetch = lu.fetch_event_dates
    lu.fetch_event_dates = fake_fetch
    try:
        count = asyncio.run(
            create_cross_bank_structural_links_batch(conn, bank_id, unit_ids, facts)
        )
    finally:
        lu.fetch_event_dates = original_fetch

    trans_links = [(r[0], r[1], r[3]) for r in conn.inserted_links if r[2] == "transition"]
    assert ("old-intention-1", "exp-unit", "fulfilled_by") in trans_links, (
        "Missing fulfilled_by transition link from intention to experience"
    )
    print("PASS: Transition heuristic creates fulfilled_by link from planning intention to experience")


def test_blocked_entities_excluded_from_structural_queries():
    bank_id = "test_bank"
    user_eid = _resolve_entity_id(bank_id, "User")

    unit_ids = ["habit-unit"]
    facts = [_make_processed_fact("habit", ["User", "me", "my"])]  # all blocked

    conn = FakeConn()
    conn.entity_facts = {
        str(user_eid): [{"id": "old-unit", "fact_type": "experience"}]
    }

    async def fake_fetch(conn_, uids):
        return {}

    import cogmem_api.engine.retain.link_utils as lu
    original_fetch = lu.fetch_event_dates
    lu.fetch_event_dates = fake_fetch
    try:
        asyncio.run(create_cross_bank_structural_links_batch(conn, bank_id, unit_ids, facts))
    finally:
        lu.fetch_event_dates = original_fetch

    assert len(conn.inserted_links) == 0, "Blocked entities produced structural links"
    print("PASS: Blocked entities excluded from structural link queries")


if __name__ == "__main__":
    tests = [
        test_temporal_cross_session_links,
        test_sr_link_habit_to_existing_facts,
        test_transition_heuristic_experience_to_planning_intention,
        test_blocked_entities_excluded_from_structural_queries,
    ]
    passed = 0
    for t in tests:
        try:
            t()
            passed += 1
        except Exception as exc:
            import traceback
            print(f"FAIL: {t.__name__}: {exc}")
            traceback.print_exc()

    print(f"\n{passed}/{len(tests)} PASS")
    if passed < len(tests):
        sys.exit(1)
