"""Task 745: S20.3 — Document and gate s_r_link simplification.

Gap: s_r_link uses entity-overlap proxy instead of behavioral reinforcement logic.
This is a documented simplification valid for NL dialogue context.

Verifies:
- s_r_link edges are created between habit node and non-habit nodes sharing at least one entity
- s_r_link does NOT connect across different entities
- Rationale: entity-overlap is a reasonable proxy for S-R behavioral reinforcement at NL dialogue level
"""

from __future__ import annotations

import asyncio
import sys
import uuid
from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta
from pathlib import Path
from types import SimpleNamespace


@dataclass
class _NoopTransaction:
    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        return False


class FakeConnection:
    def __init__(self):
        self.memory_units: list[dict] = []
        self.memory_links: list[tuple] = []
        self.unit_entities: list[tuple[str, str]] = []
        self._banks: set[str] = set()

    def transaction(self):
        return _NoopTransaction()

    async def ensure_bank_exists(self, bank_id: str) -> None:
        self._banks.add(bank_id)

    async def insert_memory_units(self, bank_id: str, facts, document_id=None) -> list[str]:
        ids: list[str] = []
        for fact in facts:
            unit_id = str(uuid.uuid4())
            event_date = fact.occurred_start or fact.mentioned_at or datetime.now(UTC)
            self.memory_units.append(
                {
                    "id": unit_id,
                    "bank_id": bank_id,
                    "fact_type": fact.fact_type,
                    "text": fact.fact_text,
                    "event_date": event_date,
                }
            )
            ids.append(unit_id)
        return ids

    async def get_unit_event_dates(self, unit_ids: list[str]) -> dict[str, datetime]:
        lookup = {row["id"]: row["event_date"] for row in self.memory_units}
        return {unit_id: lookup[unit_id] for unit_id in unit_ids if unit_id in lookup}

    async def insert_memory_links(self, links: list[tuple]) -> None:
        self.memory_links.extend(links)

    async def insert_unit_entities(self, pairs: list[tuple[str, str]]) -> None:
        self.unit_entities.extend(pairs)


class FakePool:
    def __init__(self, connection: FakeConnection):
        self.connection = connection

    async def acquire(self):
        return self.connection

    async def release(self, conn):
        return None


class FakeEmbeddingsModel:
    def encode(self, texts: list[str]) -> list[list[float]]:
        vectors: list[list[float]] = []
        for text in texts:
            seed = float((sum(ord(ch) for ch in text) % 50) + 1)
            vectors.append([seed / 50.0, 0.4, 0.2, 0.1])
        return vectors


REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))


async def run_sr_link_contract_test():
    from cogmem_api.engine.retain.orchestrator import retain_batch

    start = datetime(2026, 3, 31, 10, 0, tzinfo=UTC)

    contents = [
        {
            "content": "Alice always checks her email before standup.",
            "event_date": start,
            "entities": [{"text": "Alice", "type": "PERSON"}],
        },
        {
            "content": "Alice prepared standup notes for the team.",
            "event_date": start + timedelta(minutes=5),
            "entities": [{"text": "Alice", "type": "PERSON"}],
        },
        {
            "content": "Bob prepared sprint tickets.",
            "event_date": start + timedelta(minutes=10),
            "entities": [{"text": "Bob", "type": "PERSON"}],
        },
    ]

    conn = FakeConnection()
    pool = FakePool(conn)

    unit_groups, _usage = await retain_batch(
        pool=pool,
        embeddings_model=FakeEmbeddingsModel(),
        llm_config=None,
        entity_resolver=None,
        format_date_fn=lambda dt: dt.strftime("%Y-%m-%d"),
        bank_id="demo_bank_t745",
        contents_dicts=contents,
        config=SimpleNamespace(),
    )

    fact_type_by_id = {row["id"]: row["fact_type"] for row in conn.memory_units}
    habit_units = [unit_id for unit_id, fact_type in fact_type_by_id.items() if fact_type == "habit"]
    assert len(habit_units) == 1, f"Expected exactly one habit node, got {len(habit_units)}"

    sr_links = [link for link in conn.memory_links if link[2] == "s_r_link"]
    assert sr_links, "Expected at least one s_r_link"

    habit_id = habit_units[0]
    outbound_sr = [link for link in sr_links if link[0] == habit_id]
    assert outbound_sr, "Habit node must originate at least one s_r_link"

    linked_target_ids = {link[1] for link in outbound_sr}
    target_fact_types = {fact_type_by_id[target_id] for target_id in linked_target_ids}
    assert "habit" not in target_fact_types, "s_r_link targets must be non-habit nodes"

    bob_unit_ids = [row["id"] for row in conn.memory_units if "Bob" in row["text"]]
    assert bob_unit_ids, "Expected Bob unit in test fixture"
    assert not linked_target_ids.intersection(set(bob_unit_ids)), "s_r_link should not connect across different entities"

    return {
        "habit_id": habit_id,
        "sr_links_count": len(sr_links),
        "linked_targets": list(linked_target_ids),
        "cross_entity_links": linked_target_ids.intersection(set(bob_unit_ids)),
    }


def test_sr_link_contract_in_code():
    link_creation_path = REPO_ROOT / "cogmem_api" / "engine" / "retain" / "link_creation.py"
    text = link_creation_path.read_text(encoding="utf-8")

    assert "s_r_link" in text, "s_r_link must be present in link_creation.py"
    assert "habit" in text, "habit handling must be present"
    assert "overlap" in text, "Entity overlap logic must be present"


async def main() -> None:
    result = await run_sr_link_contract_test()
    test_sr_link_contract_in_code()

    print("Task 745 s_r_link contract gate passed.")
    print(f"  Habit node: {result['habit_id'][:8]}...")
    print(f"  s_r_link count: {result['sr_links_count']}")
    print(f"  Cross-entity links (should be empty): {result['cross_entity_links']}")
    print("  Rationale: entity-overlap is valid proxy for S-R linking at NL dialogue level")


if __name__ == "__main__":
    asyncio.run(main())
