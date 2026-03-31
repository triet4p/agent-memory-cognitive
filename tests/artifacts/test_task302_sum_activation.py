from __future__ import annotations

import asyncio
import math
import sys
from pathlib import Path


def make_unit_row(node_id: str, text: str, fact_type: str = "world", similarity: float | None = None) -> dict:
    row = {
        "id": node_id,
        "text": text,
        "context": None,
        "event_date": None,
        "occurred_start": None,
        "occurred_end": None,
        "mentioned_at": None,
        "fact_type": fact_type,
        "document_id": None,
        "chunk_id": None,
        "tags": None,
    }
    if similarity is not None:
        row["similarity"] = similarity
    return row


def make_link_row(from_id: str, to_id: str, weight: float, link_type: str = "semantic") -> dict:
    row = make_unit_row(to_id, f"node-{to_id}")
    row["weight"] = weight
    row["link_type"] = link_type
    row["from_unit_id"] = from_id
    return row


class FakeConn:
    def __init__(self):
        self.entry_rows = [
            make_unit_row("A", "entry-a", similarity=0.6),
            make_unit_row("B", "entry-b", similarity=0.6),
        ]
        self.edges = {
            "A": [make_link_row("A", "X", 0.8)],
            "B": [make_link_row("B", "X", 0.9)],
            "X": [
                make_link_row("X", "A", 0.9),
                make_link_row("X", "B", 0.9),
            ],
        }
        self.neighbor_queries = 0

    async def fetch(self, query: str, *params):
        if "ORDER BY embedding <=>" in query:
            return self.entry_rows

        if "FROM public.memory_links" in query or "FROM memory_links" in query:
            self.neighbor_queries += 1
            source_ids = params[0]
            rows = []
            for source in source_ids:
                rows.extend(self.edges.get(source, []))
            return rows

        return []


async def run_sum_and_saturation_check() -> None:
    from cogmem_api.engine.search.graph_retrieval import BFSGraphRetriever

    conn = FakeConn()
    retriever = BFSGraphRetriever(
        activation_decay=1.0,
        min_activation=0.01,
        batch_size=10,
        refractory_steps=1,
        firing_quota=2,
        activation_saturation=2.0,
    )

    results = await retriever._retrieve_with_conn(
        conn=conn,
        query_embedding_str="[0.1,0.2,0.3,0.4]",
        bank_id="bank_t302",
        fact_type="world",
        budget=10,
    )

    by_id = {r.id: r for r in results}
    assert "X" in by_id, "Expected merged multi-path node X in results"

    # SUM propagation should combine A->X and B->X contributions: 0.6*0.8 + 0.6*0.9 = 1.02
    assert (by_id["X"].activation or 0.0) > 0.9, "Activation should increase from multi-path SUM, not single-path MAX"
    # Saturation A_max should keep values bounded even in cycles
    assert (by_id["X"].activation or 0.0) <= 2.0 + 1e-9, "Activation exceeded configured saturation A_max"


async def run_refractory_guard_check() -> None:
    from cogmem_api.engine.search.graph_retrieval import BFSGraphRetriever

    conn = FakeConn()
    retriever = BFSGraphRetriever(
        activation_decay=1.0,
        min_activation=0.01,
        batch_size=10,
        refractory_steps=2,
        firing_quota=5,
        activation_saturation=10.0,
    )

    results = await retriever._retrieve_with_conn(
        conn=conn,
        query_embedding_str="[0.1,0.2,0.3,0.4]",
        bank_id="bank_t302",
        fact_type="world",
        budget=10,
    )

    by_id = {r.id: r for r in results}
    assert "A" in by_id and "B" in by_id and "X" in by_id

    # Refractory=2 blocks immediate re-firing in this 3-step cycle, so seed nodes stay at entry activation.
    assert math.isclose(by_id["A"].activation or 0.0, 0.6, rel_tol=1e-6)
    assert math.isclose(by_id["B"].activation or 0.0, 0.6, rel_tol=1e-6)


async def run_firing_quota_guard_check() -> None:
    from cogmem_api.engine.search.graph_retrieval import BFSGraphRetriever

    conn = FakeConn()
    retriever = BFSGraphRetriever(
        activation_decay=1.0,
        min_activation=0.01,
        batch_size=10,
        refractory_steps=0,
        firing_quota=1,
        activation_saturation=10.0,
    )

    await retriever._retrieve_with_conn(
        conn=conn,
        query_embedding_str="[0.1,0.2,0.3,0.4]",
        bank_id="bank_t302",
        fact_type="world",
        budget=10,
    )

    # With quota=1 each node can fire only once, so traversal should stop quickly.
    assert conn.neighbor_queries <= 2, "Firing quota should cap repeated cycle traversal"


def main() -> None:
    repo_root = Path(__file__).resolve().parents[2]
    repo_root_str = str(repo_root)
    if repo_root_str not in sys.path:
        sys.path.insert(0, repo_root_str)

    asyncio.run(run_sum_and_saturation_check())
    asyncio.run(run_refractory_guard_check())
    asyncio.run(run_firing_quota_guard_check())
    print("Task 302 SUM activation check passed.")


if __name__ == "__main__":
    main()
