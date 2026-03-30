from __future__ import annotations

import asyncio
import sys
import uuid
from dataclasses import dataclass
from datetime import UTC, datetime
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
                    "metadata": fact.metadata,
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
            seed = float((sum(ord(ch) for ch in text) % 97) + 1)
            vectors.append([seed / 97.0, 0.3, 0.2, 0.1])
        return vectors


def assert_required_files(repo_root: Path) -> None:
    required = [
        repo_root / "logs" / "task_203_summary.md",
        repo_root / "cogmem_api" / "engine" / "retain" / "fact_extraction.py",
        repo_root / "cogmem_api" / "engine" / "retain" / "link_creation.py",
        repo_root / "cogmem_api" / "engine" / "retain" / "orchestrator.py",
    ]
    missing = [str(path.relative_to(repo_root)) for path in required if not path.exists()]
    assert not missing, f"Missing T2.3 files: {missing}"


def assert_isolation(repo_root: Path) -> None:
    retain_root = repo_root / "cogmem_api" / "engine" / "retain"
    violating = []
    for py_file in retain_root.rglob("*.py"):
        text = py_file.read_text(encoding="utf-8")
        if "hindsight_api" in text:
            violating.append(str(py_file.relative_to(repo_root)))
    assert not violating, f"Found forbidden hindsight_api imports: {violating}"


async def run_behavior_test(repo_root: Path) -> None:
    repo_root_str = str(repo_root)
    if repo_root_str not in sys.path:
        sys.path.insert(0, repo_root_str)

    from cogmem_api.engine.retain.orchestrator import retain_batch

    start = datetime(2026, 3, 31, 11, 0, tzinfo=UTC)

    # Fact order is important because transition_relations target_fact_index references this list.
    seeded_facts = [
        {
            "text": "Alice plans to learn Rust in Q3",
            "fact_type": "intention",
            "entities": ["Alice"],
            "intention_status": "planning",
            "transition_relations": [
                {"target_fact_index": 1, "transition_type": "fulfilled_by"},
                {"target_fact_index": 5, "transition_type": "enabled_by"},
            ],
        },
        {
            "text": "Alice completed the Rust tutorial",
            "fact_type": "experience",
            "entities": ["Alice"],
        },
        {
            "text": "Alice dropped the Kotlin migration plan",
            "fact_type": "intention",
            "entities": ["Alice"],
            "intention_status": "abandoned",
            "transition_relations": [
                {"transition_type": "abandoned"}
            ],
        },
        {
            "text": "Review with Minh inspired cache work",
            "fact_type": "experience",
            "entities": ["Alice", "Minh"],
            "transition_relations": [
                {"target_fact_index": 4, "transition_type": "triggered"}
            ],
        },
        {
            "text": "Alice plans to add cache layer",
            "fact_type": "intention",
            "entities": ["Alice"],
            "intention_status": "planning",
        },
        {
            "text": "Alice plans to write a Rust paper",
            "fact_type": "intention",
            "entities": ["Alice"],
            "intention_status": "planning",
        },
    ]

    contents = [
        {
            "content": "intention lifecycle scenario",
            "event_date": start,
            "facts": seeded_facts,
        }
    ]

    conn = FakeConnection()
    pool = FakePool(conn)

    unit_groups, _usage = await retain_batch(
        pool=pool,
        embeddings_model=FakeEmbeddingsModel(),
        llm_config=None,
        entity_resolver=None,
        format_date_fn=lambda dt: dt.strftime("%Y-%m-%d"),
        bank_id="demo_bank_t203",
        contents_dicts=contents,
        config=SimpleNamespace(),
    )

    assert len(unit_groups) == 1 and len(unit_groups[0]) == len(seeded_facts)

    created_ids = unit_groups[0]

    transition_links = [link for link in conn.memory_links if link[2] == "transition"]
    assert transition_links, "Expected transition links for intention lifecycle"

    def find_transition(src_idx: int, dst_idx: int, transition_type: str) -> bool:
        src = created_ids[src_idx]
        dst = created_ids[dst_idx]
        return any(
            link[0] == src and link[1] == dst and link[2] == "transition" and link[3] == transition_type
            for link in transition_links
        )

    assert find_transition(0, 1, "fulfilled_by"), "planning->fulfilled transition must be created"
    assert find_transition(3, 4, "triggered"), "experience->intention triggered transition must be created"
    assert find_transition(0, 5, "enabled_by"), "intention->intention enabled_by transition must be created"

    abandoned_links = [link for link in transition_links if link[3] == "abandoned"]
    assert not abandoned_links, "abandoned should be a status update, not a transition edge"

    fact_type_by_id = {row["id"]: row["fact_type"] for row in conn.memory_units}
    experience_count = sum(1 for ft in fact_type_by_id.values() if ft == "experience")
    assert experience_count == 2, "Abandoned intention must not create a new experience node"

    abandoned_nodes = [row for row in conn.memory_units if row["metadata"].get("intention_status") == "abandoned"]
    assert len(abandoned_nodes) == 1, "Abandoned intention status must be preserved in metadata"


def main() -> None:
    repo_root = Path(__file__).resolve().parents[2]
    assert_required_files(repo_root)
    assert_isolation(repo_root)
    asyncio.run(run_behavior_test(repo_root))
    print("Task 203 intention lifecycle check passed.")


if __name__ == "__main__":
    main()
