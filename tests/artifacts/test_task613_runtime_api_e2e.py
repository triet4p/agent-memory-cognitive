from __future__ import annotations

import sys
import uuid
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path


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

    async def fetchval(self, sql: str, *args):
        if "SELECT 1" in sql.upper():
            return 1
        return None

    async def ensure_bank_exists(self, bank_id: str) -> None:
        self._banks.add(bank_id)

    async def insert_memory_units(self, bank_id: str, facts, document_id=None) -> list[str]:
        created_ids: list[str] = []
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
                    "event_date": event_date,
                    "document_id": fact.document_id if fact.document_id else document_id,
                }
            )
            created_ids.append(unit_id)
        return created_ids

    async def get_unit_event_dates(self, unit_ids: list[str]) -> dict[str, datetime]:
        event_dates = {item["id"]: item["event_date"] for item in self.memory_units}
        return {unit_id: event_dates[unit_id] for unit_id in unit_ids if unit_id in event_dates}

    async def insert_memory_links(self, links: list[tuple]) -> None:
        self.memory_links.extend(links)

    async def insert_unit_entities(self, pairs: list[tuple[str, str]]) -> None:
        self.unit_entities.extend(pairs)

    async def recall_memory_units(self, bank_id: str, query: str, fact_types: list[str], limit: int) -> list[dict]:
        query_terms = {token for token in query.lower().split() if token}

        def overlap_score(text: str) -> int:
            terms = {token for token in text.lower().split() if token}
            return len(query_terms.intersection(terms))

        scoped = [
            row
            for row in self.memory_units
            if row["bank_id"] == bank_id and row["fact_type"] in fact_types
        ]
        ranked = sorted(scoped, key=lambda row: overlap_score(row["text"]), reverse=True)
        return ranked[:limit]


class FakePool:
    def __init__(self, connection: FakeConnection):
        self.connection = connection

    async def acquire(self):
        return self.connection

    async def release(self, _conn):
        return None

    async def close(self):
        return None


def assert_required_files(repo_root: Path) -> None:
    required = [
        repo_root / "cogmem_api" / "api" / "http.py",
        repo_root / "cogmem_api" / "engine" / "memory_engine.py",
        repo_root / "logs" / "task_613_summary.md",
        repo_root / "tests" / "artifacts" / "test_task613_runtime_api_e2e.py",
    ]
    missing = [str(path.relative_to(repo_root)) for path in required if not path.exists()]
    assert not missing, f"Missing B3 artifacts/files: {missing}"


def assert_isolation(repo_root: Path) -> None:
    targets = [
        repo_root / "cogmem_api" / "api" / "http.py",
        repo_root / "cogmem_api" / "engine" / "memory_engine.py",
        repo_root / "tests" / "artifacts" / "test_task613_runtime_api_e2e.py",
    ]
    violations: list[str] = []
    forbidden_import = "hindsight" + "_api"
    for target in targets:
        content = target.read_text(encoding="utf-8")
        if forbidden_import in content:
            violations.append(str(target.relative_to(repo_root)))
    assert not violations, f"Isolation violation detected: {violations}"


def run_runtime_roundtrip(repo_root: Path) -> None:
    repo_root_str = str(repo_root)
    if repo_root_str not in sys.path:
        sys.path.insert(0, repo_root_str)

    from fastapi.testclient import TestClient

    from cogmem_api.api import create_app
    from cogmem_api.engine.memory_engine import MemoryEngine

    fake_conn = FakeConnection()
    fake_pool = FakePool(fake_conn)

    memory = MemoryEngine(db_url="postgresql://fixture")
    memory._pool = fake_pool
    memory._initialized = True

    app = create_app(memory=memory, http_api_enabled=True, initialize_memory=False)

    with TestClient(app) as client:
        retain_response = client.post(
            "/v1/default/banks/demo-b3/memories",
            json={
                "items": [
                    {"content": "Alice planned a Rust migration to reduce latency."},
                    {"content": "Alice switched to int8 quantization and latency dropped."},
                ]
            },
        )
        assert retain_response.status_code == 200, retain_response.text
        retain_payload = retain_response.json()
        assert retain_payload["success"] is True
        assert retain_payload["items_count"] == 2
        assert len(retain_payload["unit_ids"]) == 2

        recall_response = client.post(
            "/v1/default/banks/demo-b3/memories/recall",
            json={
                "query": "What happened with Rust latency?",
                "types": ["world", "experience", "opinion", "habit", "intention", "action_effect"],
                "budget": "mid",
                "max_tokens": 256,
                "trace": True,
            },
        )
        assert recall_response.status_code == 200, recall_response.text
        recall_payload = recall_response.json()
        assert "results" in recall_payload
        assert len(recall_payload["results"]) >= 1

        top_text = recall_payload["results"][0]["text"].lower()
        assert "latency" in top_text or "rust" in top_text

        health_response = client.get("/health")
        assert health_response.status_code == 200, health_response.text

    assert len(fake_conn.memory_units) >= 2, "Retain route must persist facts through memory engine"


def main() -> None:
    repo_root = Path(__file__).resolve().parents[2]
    assert_required_files(repo_root)
    assert_isolation(repo_root)
    run_runtime_roundtrip(repo_root)
    print("Task 613 runtime API e2e check passed.")


if __name__ == "__main__":
    main()
