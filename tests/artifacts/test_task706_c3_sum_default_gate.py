from __future__ import annotations

import asyncio
import os
import sys
from pathlib import Path


def assert_required_outputs(repo_root: Path) -> None:
    required = [
        repo_root / "logs" / "task_706_summary.md",
        repo_root / "tests" / "artifacts" / "test_task706_c3_sum_default_gate.py",
    ]
    missing = [str(path.relative_to(repo_root)) for path in required if not path.exists()]
    assert not missing, f"Missing task706 outputs: {missing}"


def _restore_env(backup: dict[str, str | None]) -> None:
    for key, value in backup.items():
        if value is None:
            os.environ.pop(key, None)
        else:
            os.environ[key] = value


def _reset_config_cache(config_module) -> None:
    config_module._cached_config = None


def assert_default_policy_in_config() -> None:
    import cogmem_api.config as config_module

    env_keys = [
        "COGMEM_API_GRAPH_RETRIEVER",
        "COGMEM_API_BFS_REFRACTORY_STEPS",
        "COGMEM_API_BFS_FIRING_QUOTA",
        "COGMEM_API_BFS_ACTIVATION_SATURATION",
    ]
    backup = {key: os.environ.get(key) for key in env_keys}

    try:
        assert config_module.DEFAULT_GRAPH_RETRIEVER == "bfs"

        os.environ["COGMEM_API_GRAPH_RETRIEVER"] = ""
        _reset_config_cache(config_module)
        cfg = config_module.get_config()
        assert cfg.graph_retriever == "bfs"

        os.environ["COGMEM_API_GRAPH_RETRIEVER"] = "invalid-retriever"
        _reset_config_cache(config_module)
        cfg = config_module.get_config()
        assert cfg.graph_retriever == "bfs", "Invalid retriever value must fall back to BFS"

        os.environ["COGMEM_API_GRAPH_RETRIEVER"] = "mpfp"
        _reset_config_cache(config_module)
        cfg = config_module.get_config()
        assert cfg.graph_retriever == "mpfp"
    finally:
        _restore_env(backup)
        _reset_config_cache(config_module)


class FakeConn:
    def __init__(self) -> None:
        self.entry_rows = [
            self._unit_row("A", "entry-a", similarity=0.6),
            self._unit_row("B", "entry-b", similarity=0.6),
        ]
        self.edges = {
            "A": [self._link_row("A", "X", 0.8)],
            "B": [self._link_row("B", "X", 0.9)],
            "X": [
                self._link_row("X", "A", 0.9),
                self._link_row("X", "B", 0.9),
            ],
        }
        self.neighbor_queries = 0

    @staticmethod
    def _unit_row(node_id: str, text: str, similarity: float | None = None) -> dict:
        row = {
            "id": node_id,
            "text": text,
            "context": None,
            "event_date": None,
            "occurred_start": None,
            "occurred_end": None,
            "mentioned_at": None,
            "fact_type": "world",
            "document_id": None,
            "chunk_id": None,
            "tags": None,
        }
        if similarity is not None:
            row["similarity"] = similarity
        return row

    @classmethod
    def _link_row(cls, from_id: str, to_id: str, weight: float) -> dict:
        row = cls._unit_row(to_id, f"node-{to_id}")
        row["weight"] = weight
        row["link_type"] = "semantic"
        row["from_unit_id"] = from_id
        return row

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


async def assert_default_bfs_runtime_behavior() -> None:
    import cogmem_api.config as config_module
    import cogmem_api.engine.search.retrieval as retrieval_module
    from cogmem_api.engine.search.graph_retrieval import BFSGraphRetriever

    env_keys = [
        "COGMEM_API_GRAPH_RETRIEVER",
        "COGMEM_API_BFS_REFRACTORY_STEPS",
        "COGMEM_API_BFS_FIRING_QUOTA",
        "COGMEM_API_BFS_ACTIVATION_SATURATION",
    ]
    backup = {key: os.environ.get(key) for key in env_keys}

    try:
        os.environ["COGMEM_API_GRAPH_RETRIEVER"] = "bfs"
        os.environ["COGMEM_API_BFS_REFRACTORY_STEPS"] = "2"
        os.environ["COGMEM_API_BFS_FIRING_QUOTA"] = "1"
        os.environ["COGMEM_API_BFS_ACTIVATION_SATURATION"] = "2.0"

        _reset_config_cache(config_module)
        retrieval_module._default_graph_retriever = None

        retriever = retrieval_module.get_default_graph_retriever()
        assert isinstance(retriever, BFSGraphRetriever)
        assert retriever.refractory_steps == 2
        assert retriever.firing_quota == 1
        assert abs(retriever.activation_saturation - 2.0) < 1e-9

        conn = FakeConn()
        results = await retriever._retrieve_with_conn(
            conn=conn,
            query_embedding_str="[0.1,0.2,0.3,0.4]",
            bank_id="bank_t706",
            fact_type="world",
            budget=10,
        )
        by_id = {r.id: r for r in results}

        assert "X" in by_id, "Expected merged node from multi-hop evidence"
        # With default activation_decay=0.8, combined multi-path activation should still
        # exceed any single-path contribution (max single path here is 0.432).
        assert (by_id["X"].activation or 0.0) > 0.7, "SUM path must accumulate activation from both parents"
        assert (by_id["X"].activation or 0.0) <= 2.0 + 1e-9, "Activation must respect saturation guard"
        assert conn.neighbor_queries <= 2, "Firing quota/refractory should prevent repeated loop expansion"
    finally:
        _restore_env(backup)
        _reset_config_cache(config_module)
        retrieval_module._default_graph_retriever = None

def main() -> None:
    repo_root = Path(__file__).resolve().parents[2]
    repo_root_str = str(repo_root)
    if repo_root_str not in sys.path:
        sys.path.insert(0, repo_root_str)

    assert_required_outputs(repo_root)
    assert_default_policy_in_config()
    asyncio.run(assert_default_bfs_runtime_behavior())

    print("Task 706 C3 sum-default gate checks passed.")


if __name__ == "__main__":
    main()
