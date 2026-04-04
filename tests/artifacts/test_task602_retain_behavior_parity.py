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
    def __init__(self) -> None:
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
                    "raw_snippet": fact.raw_snippet,
                    "metadata": fact.metadata,
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
            base = float((sum(ord(ch) for ch in text) % 83) + 1)
            vectors.append([base / 83.0, 0.41, 0.21, 0.11])
        return vectors


class FakeLLMConfig:
    async def call(self, messages, **kwargs):
        from cogmem_api.engine.response_models import TokenUsage

        _system_prompt = str(messages[0]["content"])
        usage = TokenUsage(input_tokens=42, output_tokens=28, total_tokens=70)

        return {
            "facts": [
                {
                    "what": "Latency exceeded 100ms during deployment",
                    "when": "2026-04-04",
                    "where": "N/A",
                    "who": "Alice",
                    "why": "Production latency issue",
                    "fact_kind": "event",
                    "fact_type": "world",
                    "entities": [{"text": "Alice"}],
                },
                {
                    "what": "Alice planned to switch quantization settings",
                    "when": "2026-04-04",
                    "where": "N/A",
                    "who": "Alice",
                    "why": "Mitigate high latency",
                    "fact_kind": "conversation",
                    "fact_type": "intention",
                    "entities": [{"text": "Alice"}],
                    "intention_status": "PLANNING",
                    "transition_relations": [
                        {"target_index": 2, "transition_type": "fulfilled_by", "strength": 0.88},
                        {"target_index": 2, "transition_type": "triggered", "strength": 0.77},
                    ],
                },
                {
                    "what": "Alice switched to int8 quantization in production",
                    "when": "2026-04-04",
                    "where": "N/A",
                    "who": "Alice",
                    "why": "Execution of planned mitigation",
                    "fact_kind": "event",
                    "fact_type": "experience",
                    "entities": [{"text": "Alice"}],
                    "causal_relations": [
                        {"target_index": 0, "relation_type": "caused_by", "strength": 0.82}
                    ],
                    "transition_relations": [
                        {"target_index": 1, "transition_type": "triggered", "strength": 0.66}
                    ],
                },
                {
                    "what": "When latency is high, Alice switches to int8 so latency drops",
                    "when": "2026-04-04",
                    "where": "N/A",
                    "who": "Alice",
                    "why": "A-O causal pattern",
                    "fact_kind": "event",
                    "fact_type": "action_effect",
                    "entities": [{"text": "Alice"}],
                    "precondition": "Latency > 100ms",
                    "action": "Switch to int8 quantization",
                    "outcome": "Latency dropped to 45ms",
                    "confidence": "1.5",
                    "devalue_sensitive": "yes",
                    "action_effect_relations": [
                        {"target_index": 2, "relation_type": "a_o_causal", "strength": 0.93}
                    ],
                },
            ]
        }, usage


def assert_required_files(repo_root: Path) -> None:
    required = [
        repo_root / "cogmem_api" / "engine" / "retain" / "types.py",
        repo_root / "cogmem_api" / "engine" / "retain" / "link_creation.py",
        repo_root / "cogmem_api" / "engine" / "retain" / "fact_storage.py",
        repo_root / "logs" / "task_602_summary.md",
        repo_root / "tests" / "artifacts" / "test_task602_retain_behavior_parity.py",
    ]
    missing = [str(path.relative_to(repo_root)) for path in required if not path.exists()]
    assert not missing, f"Missing T6.2 files: {missing}"


def assert_isolation(repo_root: Path) -> None:
    targets = [
        repo_root / "cogmem_api" / "engine" / "retain" / "types.py",
        repo_root / "cogmem_api" / "engine" / "retain" / "link_creation.py",
        repo_root / "cogmem_api" / "engine" / "retain" / "fact_storage.py",
    ]

    violations: list[str] = []
    for path in targets:
        text = path.read_text(encoding="utf-8")
        if "hindsight_api" in text:
            violations.append(str(path.relative_to(repo_root)))

    assert not violations, f"Isolation violation detected: {violations}"


async def run_behavior_test(repo_root: Path) -> None:
    repo_root_str = str(repo_root)
    if repo_root_str not in sys.path:
        sys.path.insert(0, repo_root_str)

    from cogmem_api.engine.retain.orchestrator import retain_batch

    conn = FakeConnection()
    pool = FakePool(conn)

    now = datetime(2026, 4, 4, 9, 30, tzinfo=UTC)
    source_content = "Latency issue and quantization lifecycle discussion between user and assistant."

    unit_groups, usage = await retain_batch(
        pool=pool,
        embeddings_model=FakeEmbeddingsModel(),
        llm_config=FakeLLMConfig(),
        entity_resolver=None,
        format_date_fn=lambda dt: dt.strftime("%Y-%m-%d"),
        bank_id="demo_bank_t602",
        contents_dicts=[
            {
                "content": source_content,
                "event_date": now,
                "context": "retain",
                "metadata": {"source": "llm-e2e"},
            }
        ],
        config=SimpleNamespace(
            retain_extraction_mode="concise",
            retain_max_completion_tokens=64000,
            retain_chunk_size=3000,
            retain_mission="Retain durable technical memory",
            retain_custom_instructions=None,
            retain_extract_causal_links=True,
        ),
    )

    assert usage.total_tokens > 0
    assert len(unit_groups) == 1
    created_ids = unit_groups[0]
    assert len(created_ids) == 4

    row_by_id = {row["id"]: row for row in conn.memory_units}
    fact_type_by_id = {row_id: row["fact_type"] for row_id, row in row_by_id.items()}

    # raw_snippet parity
    for row in conn.memory_units:
        assert row["raw_snippet"] == source_content

    # metadata parity
    intention_row = next(row for row in conn.memory_units if row["fact_type"] == "intention")
    assert intention_row["metadata"].get("intention_status") == "planning"
    assert "edge_intent" in intention_row["metadata"]

    action_effect_row = next(row for row in conn.memory_units if row["fact_type"] == "action_effect")
    assert action_effect_row["metadata"].get("precondition") == "Latency > 100ms"
    assert action_effect_row["metadata"].get("action") == "Switch to int8 quantization"
    assert action_effect_row["metadata"].get("outcome") == "Latency dropped to 45ms"
    assert action_effect_row["metadata"].get("confidence") == 1.0
    assert action_effect_row["metadata"].get("devalue_sensitive") is True
    assert "edge_intent" in action_effect_row["metadata"]

    # edge parity
    causal_links = [link for link in conn.memory_links if link[2] == "causal"]
    assert len(causal_links) == 1

    transition_links = [link for link in conn.memory_links if link[2] == "transition"]
    transition_types = [link[3] for link in transition_links]
    assert "fulfilled_by" in transition_types
    assert "triggered" in transition_types

    # invalid transition (intention -> experience with triggered) must be filtered out
    intention_id = next(unit_id for unit_id in created_ids if fact_type_by_id[unit_id] == "intention")
    experience_id = next(unit_id for unit_id in created_ids if fact_type_by_id[unit_id] == "experience")
    assert not any(
        link[0] == intention_id and link[1] == experience_id and link[2] == "transition" and link[3] == "triggered"
        for link in transition_links
    )

    action_effect_id = next(unit_id for unit_id in created_ids if fact_type_by_id[unit_id] == "action_effect")
    ao_links = [link for link in conn.memory_links if link[2] == "a_o_causal"]
    assert any(link[0] == action_effect_id and link[1] == experience_id for link in ao_links)


def main() -> None:
    repo_root = Path(__file__).resolve().parents[2]
    assert_required_files(repo_root)
    assert_isolation(repo_root)
    asyncio.run(run_behavior_test(repo_root))
    print("Task 602 retain behavior parity check passed.")


if __name__ == "__main__":
    main()
