from __future__ import annotations

import asyncio
import sys
import uuid
from dataclasses import dataclass
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
                    "document_id": fact.document_id if fact.document_id else document_id,
                    "fact_type": fact.fact_type,
                    "network_type": fact.fact_type,
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
            base = float((sum(ord(ch) for ch in text) % 100) + 1)
            vectors.append([base / 100.0, 0.5, 0.25, 0.125])
        return vectors


def assert_required_files(repo_root: Path) -> None:
    required = [
        repo_root / "cogmem_api" / "engine" / "retain" / "__init__.py",
        repo_root / "cogmem_api" / "engine" / "retain" / "orchestrator.py",
        repo_root / "cogmem_api" / "engine" / "retain" / "fact_extraction.py",
        repo_root / "cogmem_api" / "engine" / "retain" / "fact_storage.py",
        repo_root / "cogmem_api" / "engine" / "retain" / "entity_processing.py",
        repo_root / "cogmem_api" / "engine" / "retain" / "embedding_processing.py",
        repo_root / "cogmem_api" / "engine" / "retain" / "link_creation.py",
        repo_root / "logs" / "task_201_summary.md",
    ]
    missing = [str(path.relative_to(repo_root)) for path in required if not path.exists()]
    assert not missing, f"Missing T2.1 files: {missing}"


def assert_isolation(repo_root: Path) -> None:
    retain_root = repo_root / "cogmem_api" / "engine" / "retain"
    bad = []
    for py_file in retain_root.rglob("*.py"):
        content = py_file.read_text(encoding="utf-8")
        if "hindsight_api" in content:
            bad.append(str(py_file.relative_to(repo_root)))
    assert not bad, f"Found forbidden hindsight imports in retain package: {bad}"


async def run_behavior_test(repo_root: Path) -> None:
    repo_root_str = str(repo_root)
    if repo_root_str not in sys.path:
        sys.path.insert(0, repo_root_str)

    from cogmem_api.engine.retain.orchestrator import retain_batch

    now = datetime(2026, 3, 31, 9, 0, tzinfo=UTC)
    contents = [
        {
            "content": "Alice works on LLM infrastructure.",
            "event_date": now,
            "facts": [{"text": "Alice works on LLM infrastructure", "fact_type": "world", "entities": ["Alice"]}],
        },
        {
            "content": "Alice asked the assistant to summarize a design note.",
            "event_date": now + timedelta(minutes=5),
            "facts": [
                {
                    "text": "User asked assistant to summarize design note",
                    "fact_type": "experience",
                    "entities": ["Alice", "assistant"],
                }
            ],
        },
        {
            "content": "Alice believes Python is best for quick ML prototypes.",
            "event_date": now + timedelta(minutes=10),
            "facts": [{"text": "Alice believes Python is best for quick ML prototypes", "fact_type": "opinion"}],
        },
        {
            "content": "Alice always reviews emails before standup.",
            "event_date": now + timedelta(minutes=15),
            "facts": [{"text": "Alice reviews emails before standup", "fact_type": "habit", "entities": ["Alice"]}],
        },
        {
            "content": "Alice plans to learn Rust in Q3.",
            "event_date": now + timedelta(minutes=20),
            "facts": [{"text": "Alice plans to learn Rust in Q3", "fact_type": "intention", "entities": ["Alice"]}],
        },
        {
            "content": "When latency rises, Alice switches to quantization and latency drops.",
            "event_date": now + timedelta(minutes=25),
            "facts": [
                {
                    "text": "Switching to quantization lowered latency",
                    "fact_type": "action_effect",
                    "causal_relations": [{"target_fact_index": 0, "relation_type": "caused_by", "strength": 0.8}],
                }
            ],
        },
    ]

    conn = FakeConnection()
    pool = FakePool(conn)

    result_unit_ids, usage = await retain_batch(
        pool=pool,
        embeddings_model=FakeEmbeddingsModel(),
        llm_config=None,
        entity_resolver=None,
        format_date_fn=lambda dt: dt.strftime("%Y-%m-%d"),
        bank_id="demo_bank_t201",
        contents_dicts=contents,
        config=SimpleNamespace(),
    )

    assert len(result_unit_ids) == 6, "Expected unit mapping for every content item"
    assert all(len(item) == 1 for item in result_unit_ids), "Each sample content should produce exactly one fact"

    fact_types = {row["fact_type"] for row in conn.memory_units}
    expected = {"world", "experience", "opinion", "habit", "intention", "action_effect"}
    assert fact_types == expected, f"Unexpected fact types: {fact_types}"
    assert "observation" not in fact_types, "Observation network must not be created in CogMem retain baseline"

    link_types = {link[2] for link in conn.memory_links}
    assert "temporal" in link_types, "Temporal links should be created"
    assert "entity" in link_types, "Entity links should be created"
    assert "causal" in link_types, "Causal links should be created"

    assert usage.input_tokens == 0 and usage.output_tokens == 0 and usage.total_tokens == 0


def main() -> None:
    repo_root = Path(__file__).resolve().parents[2]
    assert_required_files(repo_root)
    assert_isolation(repo_root)
    asyncio.run(run_behavior_test(repo_root))
    print("Task 201 retain baseline check passed.")


if __name__ == "__main__":
    main()
