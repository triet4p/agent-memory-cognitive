from __future__ import annotations

import asyncio
import sys
from contextlib import asynccontextmanager
from datetime import datetime
from pathlib import Path


def assert_required_files(repo_root: Path) -> None:
    required = [
        repo_root / "cogmem_api" / "engine" / "search" / "__init__.py",
        repo_root / "cogmem_api" / "engine" / "search" / "retrieval.py",
        repo_root / "cogmem_api" / "engine" / "search" / "fusion.py",
        repo_root / "cogmem_api" / "engine" / "search" / "graph_retrieval.py",
        repo_root / "cogmem_api" / "engine" / "search" / "mpfp_retrieval.py",
        repo_root / "cogmem_api" / "engine" / "search" / "link_expansion_retrieval.py",
        repo_root / "cogmem_api" / "engine" / "search" / "reranking.py",
        repo_root / "cogmem_api" / "engine" / "search" / "temporal_extraction.py",
        repo_root / "cogmem_api" / "engine" / "search" / "types.py",
        repo_root / "cogmem_api" / "engine" / "query_analyzer.py",
    ]
    missing = [str(path.relative_to(repo_root)) for path in required if not path.exists()]
    assert not missing, f"Missing T3.1 files: {missing}"


def assert_isolation(repo_root: Path) -> None:
    scope = [
        repo_root / "cogmem_api" / "engine" / "search",
        repo_root / "cogmem_api" / "engine" / "query_analyzer.py",
        repo_root / "cogmem_api" / "engine" / "cross_encoder.py",
    ]
    violating: list[str] = []

    for item in scope:
        if item.is_dir():
            files = item.rglob("*.py")
        else:
            files = [item]
        for py_file in files:
            text = py_file.read_text(encoding="utf-8")
            if "hindsight_api" in text:
                violating.append(str(py_file.relative_to(repo_root)))

    assert not violating, f"Found forbidden hindsight imports: {violating}"


def run_rrf_smoke() -> None:
    from cogmem_api.engine.search.fusion import reciprocal_rank_fusion
    from cogmem_api.engine.search.types import RetrievalResult

    semantic = [
        RetrievalResult(id="u1", text="alpha", fact_type="world", similarity=0.91),
        RetrievalResult(id="u2", text="beta", fact_type="world", similarity=0.82),
    ]
    bm25 = [
        RetrievalResult(id="u2", text="beta", fact_type="world", bm25_score=12.0),
        RetrievalResult(id="u3", text="gamma", fact_type="world", bm25_score=11.5),
    ]
    graph = [
        RetrievalResult(id="u2", text="beta", fact_type="world", activation=0.73),
        RetrievalResult(id="u4", text="delta", fact_type="world", activation=0.68),
    ]

    merged = reciprocal_rank_fusion([semantic, bm25, graph])
    assert merged, "RRF merge should return candidates"
    assert merged[0].id == "u2", "Document appearing in multiple channels should rank highest"


async def run_parallel_orchestration_smoke() -> None:
    from cogmem_api.engine.search.graph_retrieval import GraphRetriever
    from cogmem_api.engine.search.retrieval import retrieve_all_fact_types_parallel
    from cogmem_api.engine.search.types import MPFPTimings, RetrievalResult

    class DummyPool:
        async def acquire(self):
            return object()

        async def release(self, conn):
            return None

    class DummyRetriever(GraphRetriever):
        @property
        def name(self) -> str:
            return "dummy"

        async def retrieve(self, **kwargs):
            return [RetrievalResult(id="g1", text="graph", fact_type="world", activation=0.5)], MPFPTimings(
                fact_type="world", result_count=1
            )

    @asynccontextmanager
    async def fake_acquire_with_retry(pool, max_retries=3):
        yield object()

    async def fake_semantic_bm25(conn, query_emb_str, query_text, bank_id, fact_types, limit, **kwargs):
        return {
            "world": (
                [RetrievalResult(id="s1", text="semantic", fact_type="world", similarity=0.88)],
                [RetrievalResult(id="b1", text="bm25", fact_type="world", bm25_score=9.8)],
            )
        }

    async def fake_temporal(conn, query_emb_str, bank_id, fact_types, start_date, end_date, budget, **kwargs):
        return {
            "world": [
                RetrievalResult(
                    id="t1",
                    text="temporal",
                    fact_type="world",
                    temporal_score=0.72,
                    temporal_proximity=0.72,
                )
            ]
        }

    # Monkeypatch module-level dependencies for isolated orchestration smoke.
    import cogmem_api.engine.search.retrieval as retrieval_mod

    original_acquire = retrieval_mod.acquire_with_retry
    original_sem_bm25 = retrieval_mod.retrieve_semantic_bm25_combined
    original_temporal = retrieval_mod.retrieve_temporal_combined

    try:
        retrieval_mod.acquire_with_retry = fake_acquire_with_retry
        retrieval_mod.retrieve_semantic_bm25_combined = fake_semantic_bm25
        retrieval_mod.retrieve_temporal_combined = fake_temporal

        result = await retrieve_all_fact_types_parallel(
            pool=DummyPool(),
            query_text="what happened last week",
            query_embedding_str="[0.1,0.2,0.3,0.4]",
            bank_id="bank_demo_t301",
            fact_types=["world"],
            thinking_budget=5,
            question_date=datetime(2026, 3, 31),
            query_analyzer=None,
            graph_retriever=DummyRetriever(),
        )

        world = result.results_by_fact_type["world"]
        assert len(world.semantic) == 1
        assert len(world.bm25) == 1
        assert len(world.graph) == 1
        assert world.temporal is not None and len(world.temporal) == 1
    finally:
        retrieval_mod.acquire_with_retry = original_acquire
        retrieval_mod.retrieve_semantic_bm25_combined = original_sem_bm25
        retrieval_mod.retrieve_temporal_combined = original_temporal


def run_temporal_extraction_smoke() -> None:
    from cogmem_api.engine.search.temporal_extraction import extract_temporal_constraint

    constraint = extract_temporal_constraint("What did we discuss last week?")
    assert constraint is not None, "Temporal query should produce a date range"
    start, end = constraint
    assert start <= end


def main() -> None:
    repo_root = Path(__file__).resolve().parents[2]
    repo_root_str = str(repo_root)
    if repo_root_str not in sys.path:
        sys.path.insert(0, repo_root_str)

    assert_required_files(repo_root)
    assert_isolation(repo_root)
    run_rrf_smoke()
    run_temporal_extraction_smoke()
    asyncio.run(run_parallel_orchestration_smoke())
    print("Task 301 search fork check passed.")


if __name__ == "__main__":
    main()
