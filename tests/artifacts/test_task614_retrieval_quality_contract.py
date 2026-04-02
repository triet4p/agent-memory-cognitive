from __future__ import annotations

import asyncio
import os
import sys
from datetime import UTC, datetime
from pathlib import Path


def assert_required_files(repo_root: Path) -> None:
    required = [
        repo_root / "cogmem_api" / "engine" / "cross_encoder.py",
        repo_root / "cogmem_api" / "engine" / "embeddings.py",
        repo_root / "cogmem_api" / "engine" / "memory_engine.py",
        repo_root / "cogmem_api" / "engine" / "search" / "reranking.py",
        repo_root / "logs" / "task_614_summary.md",
        repo_root / "tests" / "artifacts" / "test_task614_retrieval_quality_contract.py",
    ]
    missing = [str(path.relative_to(repo_root)) for path in required if not path.exists()]
    assert not missing, f"Missing B4 files/artifacts: {missing}"


def assert_isolation(repo_root: Path) -> None:
    scope = [
        repo_root / "cogmem_api" / "engine" / "cross_encoder.py",
        repo_root / "cogmem_api" / "engine" / "embeddings.py",
        repo_root / "cogmem_api" / "engine" / "memory_engine.py",
        repo_root / "cogmem_api" / "engine" / "search" / "reranking.py",
        repo_root / "tests" / "artifacts" / "test_task614_retrieval_quality_contract.py",
    ]

    forbidden = "hindsight" + "_api"
    violations: list[str] = []
    for file_path in scope:
        text = file_path.read_text(encoding="utf-8")
        if forbidden in text:
            violations.append(str(file_path.relative_to(repo_root)))

    assert not violations, f"Isolation violation detected: {violations}"


def run_cross_encoder_factory_contract() -> None:
    import cogmem_api.config as config_mod
    import cogmem_api.engine.cross_encoder as ce_mod

    original_local = ce_mod.LocalSTCrossEncoder
    original_tei = ce_mod.RemoteTEICrossEncoder

    class FakeLocal:
        def __init__(self, model_name: str, max_concurrent: int = 4):
            self.model_name = model_name
            self.max_concurrent = max_concurrent

        @property
        def provider_name(self) -> str:
            return "local"

        async def initialize(self) -> None:
            return None

        async def predict(self, pairs):
            return [0.0] * len(pairs)

    class FakeTEI:
        def __init__(self, base_url: str, timeout: float = 30.0, batch_size: int = 128, max_concurrent: int = 8):
            self.base_url = base_url
            self.timeout = timeout
            self.batch_size = batch_size
            self.max_concurrent = max_concurrent

        @property
        def provider_name(self) -> str:
            return "tei"

        async def initialize(self) -> None:
            return None

        async def predict(self, pairs):
            return [0.0] * len(pairs)

    ce_mod.LocalSTCrossEncoder = FakeLocal
    ce_mod.RemoteTEICrossEncoder = FakeTEI

    env_names = [
        "COGMEM_API_RERANKER_PROVIDER",
        "COGMEM_API_RERANKER_LOCAL_MODEL",
        "COGMEM_API_RERANKER_TEI_URL",
        "COGMEM_API_RERANKER_TEI_BATCH_SIZE",
    ]
    old_env = {name: os.environ.get(name) for name in env_names}

    try:
        os.environ["COGMEM_API_RERANKER_PROVIDER"] = "local"
        os.environ["COGMEM_API_RERANKER_LOCAL_MODEL"] = "cross-encoder/test-local"
        config_mod._cached_config = None
        local_model = ce_mod.create_cross_encoder_from_env()
        assert isinstance(local_model, FakeLocal)
        assert local_model.model_name == "cross-encoder/test-local"

        os.environ["COGMEM_API_RERANKER_PROVIDER"] = "tei"
        os.environ["COGMEM_API_RERANKER_TEI_URL"] = "http://localhost:8080"
        os.environ["COGMEM_API_RERANKER_TEI_BATCH_SIZE"] = "64"
        config_mod._cached_config = None
        tei_model = ce_mod.create_cross_encoder_from_env()
        assert isinstance(tei_model, FakeTEI)
        assert tei_model.base_url == "http://localhost:8080"
        assert tei_model.batch_size == 64

        os.environ["COGMEM_API_RERANKER_PROVIDER"] = "cohere"
        config_mod._cached_config = None
        fallback = ce_mod.create_cross_encoder_from_env()
        assert isinstance(fallback, ce_mod.RRFPassthroughCrossEncoder)
    finally:
        ce_mod.LocalSTCrossEncoder = original_local
        ce_mod.RemoteTEICrossEncoder = original_tei
        for name, value in old_env.items():
            if value is None:
                os.environ.pop(name, None)
            else:
                os.environ[name] = value
        config_mod._cached_config = None


async def run_memory_engine_embedding_contract() -> None:
    import cogmem_api.engine.memory_engine as me_mod

    original_factory = me_mod.create_embeddings_from_env

    class FakeEmbeddings:
        def __init__(self):
            self.initialized = False

        @property
        def provider_name(self) -> str:
            return "fake"

        async def initialize(self) -> None:
            self.initialized = True

        def encode(self, texts: list[str]) -> list[list[float]]:
            return [[0.1, 0.2, 0.3] for _ in texts]

    fake = FakeEmbeddings()

    def good_factory():
        return fake

    def bad_factory():
        raise RuntimeError("factory failure")

    me_mod.create_embeddings_from_env = good_factory
    engine = me_mod.MemoryEngine(db_url="")
    await engine.initialize()
    assert engine._embeddings_model is fake
    assert fake.initialized is True

    me_mod.create_embeddings_from_env = bad_factory
    fallback_engine = me_mod.MemoryEngine(db_url="")
    await fallback_engine.initialize()
    assert fallback_engine._embeddings_model is not None
    assert fallback_engine._embeddings_model.provider_name == "deterministic"

    me_mod.create_embeddings_from_env = original_factory


async def run_reranking_reorder_contract() -> None:
    from cogmem_api.engine.search.reranking import CrossEncoderReranker, apply_combined_scoring
    from cogmem_api.engine.search.types import MergedCandidate, RetrievalResult

    class FakeCrossEncoder:
        @property
        def provider_name(self) -> str:
            return "fake"

        async def initialize(self) -> None:
            return None

        async def predict(self, pairs):
            # Candidate #2 should win by reranker score.
            return [0.1, 3.0, 1.2]

    candidates = [
        MergedCandidate(retrieval=RetrievalResult(id="a", text="alpha", fact_type="world"), rrf_score=0.9),
        MergedCandidate(retrieval=RetrievalResult(id="b", text="beta", fact_type="world"), rrf_score=0.8),
        MergedCandidate(retrieval=RetrievalResult(id="c", text="gamma", fact_type="world"), rrf_score=0.7),
    ]

    reranker = CrossEncoderReranker(cross_encoder=FakeCrossEncoder())
    await reranker.ensure_initialized()
    scored = await reranker.rerank("test query", candidates)
    assert [item.id for item in scored] == ["b", "c", "a"]

    apply_combined_scoring(scored_results=scored, now=datetime.now(UTC))
    scored.sort(key=lambda item: item.combined_score, reverse=True)
    assert scored[0].id == "b"


def main() -> None:
    repo_root = Path(__file__).resolve().parents[2]
    repo_root_str = str(repo_root)
    if repo_root_str not in sys.path:
        sys.path.insert(0, repo_root_str)

    assert_required_files(repo_root)
    assert_isolation(repo_root)
    run_cross_encoder_factory_contract()
    asyncio.run(run_memory_engine_embedding_contract())
    asyncio.run(run_reranking_reorder_contract())
    print("Task 614 retrieval quality contract check passed.")


if __name__ == "__main__":
    main()
