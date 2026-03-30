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
            seed = float((sum(ord(ch) for ch in text) % 89) + 1)
            vectors.append([seed / 89.0, 0.45, 0.22, 0.11])
        return vectors


def assert_required_files(repo_root: Path) -> None:
    required = [
        repo_root / "logs" / "task_204_summary.md",
        repo_root / "cogmem_api" / "engine" / "retain" / "fact_extraction.py",
        repo_root / "cogmem_api" / "engine" / "retain" / "link_creation.py",
        repo_root / "cogmem_api" / "engine" / "retain" / "orchestrator.py",
    ]
    missing = [str(path.relative_to(repo_root)) for path in required if not path.exists()]
    assert not missing, f"Missing T2.4 files: {missing}"


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

    now = datetime(2026, 3, 31, 13, 0, tzinfo=UTC)

    # Fact index order matters for action_effect_relations target_fact_index.
    contents = [
        {
            "content": "action effect scenario",
            "event_date": now,
            "facts": [
                {
                    "text": "Alice noticed embedding latency above 100ms",
                    "fact_type": "world",
                    "entities": ["Alice"],
                },
                {
                    "text": "When embedding latency is above 100ms, Alice switched to int8 quantization, so latency dropped from 180ms to 45ms",
                    "entities": ["Alice"],
                    "action_effect_relations": [{"target_fact_index": 0, "relation_type": "a_o_causal", "strength": 0.92}],
                    "confidence": 0.92,
                    "devalue_sensitive": True,
                },
            ],
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
        bank_id="demo_bank_t204",
        contents_dicts=contents,
        config=SimpleNamespace(),
    )

    assert len(unit_groups) == 1 and len(unit_groups[0]) == 2

    created_ids = unit_groups[0]
    fact_type_by_id = {row["id"]: row["fact_type"] for row in conn.memory_units}

    action_effect_ids = [unit_id for unit_id, fact_type in fact_type_by_id.items() if fact_type == "action_effect"]
    assert len(action_effect_ids) == 1, f"Expected one action_effect node, got {len(action_effect_ids)}"

    action_effect_id = action_effect_ids[0]
    metadata = next(row["metadata"] for row in conn.memory_units if row["id"] == action_effect_id)

    for key in ("precondition", "action", "outcome"):
        assert key in metadata, f"Missing parsed {key} in action_effect metadata"
        assert isinstance(metadata[key], str) and metadata[key].strip(), f"Invalid {key} value"

    confidence = metadata.get("confidence")
    assert isinstance(confidence, (int, float)), "confidence must be numeric"
    assert 0.0 <= float(confidence) <= 1.0, "confidence must be in [0,1]"

    devalue_sensitive = metadata.get("devalue_sensitive")
    assert isinstance(devalue_sensitive, bool), "devalue_sensitive must be bool"

    ao_links = [link for link in conn.memory_links if link[2] == "a_o_causal"]
    assert ao_links, "Expected at least one a_o_causal link"

    world_id = created_ids[0]
    assert any(link[0] == action_effect_id and link[1] == world_id for link in ao_links), (
        "Expected a_o_causal edge from action_effect node to target world node"
    )


def main() -> None:
    repo_root = Path(__file__).resolve().parents[2]
    assert_required_files(repo_root)
    assert_isolation(repo_root)
    asyncio.run(run_behavior_test(repo_root))
    print("Task 204 action-effect check passed.")


if __name__ == "__main__":
    main()
