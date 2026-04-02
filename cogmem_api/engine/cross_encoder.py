"""Cross-encoder abstraction for CogMem search reranking."""

from __future__ import annotations

import asyncio
import importlib
import logging
import warnings
from abc import ABC, abstractmethod
from concurrent.futures import ThreadPoolExecutor

import httpx

from cogmem_api.config import get_config

logger = logging.getLogger(__name__)


class CrossEncoderModel(ABC):
    """Abstract cross-encoder contract used by search reranking."""

    @property
    @abstractmethod
    def provider_name(self) -> str:
        pass

    @abstractmethod
    async def initialize(self) -> None:
        pass

    @abstractmethod
    async def predict(self, pairs: list[tuple[str, str]]) -> list[float]:
        pass


class LocalSTCrossEncoder(CrossEncoderModel):
    """Local SentenceTransformers cross-encoder provider."""

    _executor: ThreadPoolExecutor | None = None

    def __init__(self, model_name: str, max_concurrent: int = 4):
        self.model_name = model_name
        self.max_concurrent = max(1, max_concurrent)
        self._model = None

    @property
    def provider_name(self) -> str:
        return "local"

    async def initialize(self) -> None:
        if self._model is not None:
            return

        try:
            module = importlib.import_module("sentence_transformers")
            CrossEncoder = getattr(module, "CrossEncoder")
        except ImportError as exc:  # pragma: no cover - depends on optional runtime deps
            raise ImportError(
                "sentence-transformers is required for local reranking. Install with: uv add sentence-transformers"
            ) from exc

        # Reduce noisy model-load warnings while keeping runtime behavior unchanged.
        with warnings.catch_warnings():
            warnings.filterwarnings("ignore", category=UserWarning)
            warnings.filterwarnings("ignore", message=".*was not found in model state dict.*")
            warnings.filterwarnings("ignore", message=".*UNEXPECTED.*")
            self._model = CrossEncoder(self.model_name)

        if LocalSTCrossEncoder._executor is None:
            LocalSTCrossEncoder._executor = ThreadPoolExecutor(
                max_workers=self.max_concurrent,
                thread_name_prefix="cogmem-reranker",
            )

        logger.info("Reranker: initialized local provider with model %s", self.model_name)

    def _predict_sync(self, pairs: list[tuple[str, str]]) -> list[float]:
        if self._model is None:
            raise RuntimeError("Local reranker is not initialized")
        scores = self._model.predict(pairs, show_progress_bar=False)
        if hasattr(scores, "tolist"):
            return [float(score) for score in scores.tolist()]
        return [float(score) for score in scores]

    async def predict(self, pairs: list[tuple[str, str]]) -> list[float]:
        if not pairs:
            return []
        if self._model is None:
            raise RuntimeError("Local reranker is not initialized")

        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(LocalSTCrossEncoder._executor, self._predict_sync, pairs)


class RemoteTEICrossEncoder(CrossEncoderModel):
    """Remote Text Embeddings Inference reranker provider."""

    _global_semaphore: asyncio.Semaphore | None = None

    def __init__(self, base_url: str, timeout: float = 30.0, batch_size: int = 128, max_concurrent: int = 8):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.batch_size = max(1, batch_size)
        self.max_concurrent = max(1, max_concurrent)
        self._client: httpx.AsyncClient | None = None

        if RemoteTEICrossEncoder._global_semaphore is None:
            RemoteTEICrossEncoder._global_semaphore = asyncio.Semaphore(self.max_concurrent)

    @property
    def provider_name(self) -> str:
        return "tei"

    async def initialize(self) -> None:
        if self._client is not None:
            return
        self._client = httpx.AsyncClient(timeout=self.timeout)
        # Probe endpoint once to fail fast if URL is invalid.
        response = await self._client.get(f"{self.base_url}/info")
        response.raise_for_status()
        logger.info("Reranker: initialized TEI provider at %s", self.base_url)

    async def _rerank_batch(self, query: str, texts: list[str]) -> list[tuple[int, float]]:
        if self._client is None:
            raise RuntimeError("TEI reranker is not initialized")

        semaphore = RemoteTEICrossEncoder._global_semaphore
        if semaphore is None:
            semaphore = asyncio.Semaphore(self.max_concurrent)
            RemoteTEICrossEncoder._global_semaphore = semaphore

        async with semaphore:
            response = await self._client.post(
                f"{self.base_url}/rerank",
                json={"query": query, "texts": texts, "return_text": False},
            )
            response.raise_for_status()
            payload = response.json()

        return [(int(item["index"]), float(item["score"])) for item in payload]

    async def predict(self, pairs: list[tuple[str, str]]) -> list[float]:
        if not pairs:
            return []
        if self._client is None:
            raise RuntimeError("TEI reranker is not initialized")

        query_groups: dict[str, list[tuple[int, str]]] = {}
        for idx, (query, text) in enumerate(pairs):
            query_groups.setdefault(query, []).append((idx, text))

        tasks_info: list[tuple[str, list[int], list[str]]] = []
        for query, indexed_texts in query_groups.items():
            indices = [item[0] for item in indexed_texts]
            texts = [item[1] for item in indexed_texts]
            for offset in range(0, len(texts), self.batch_size):
                tasks_info.append(
                    (
                        query,
                        indices[offset : offset + self.batch_size],
                        texts[offset : offset + self.batch_size],
                    )
                )

        all_scores = [0.0] * len(pairs)
        task_results = await asyncio.gather(
            *[self._rerank_batch(query=query, texts=texts) for query, _, texts in tasks_info]
        )

        for (_, batch_indices, _), scored_batch in zip(tasks_info, task_results):
            for local_index, score in scored_batch:
                all_scores[batch_indices[local_index]] = float(score)

        return all_scores


class RRFPassthroughCrossEncoder(CrossEncoderModel):
    """No-op reranker that preserves retrieval ordering."""

    @property
    def provider_name(self) -> str:
        return "rrf"

    async def initialize(self) -> None:
        return None

    async def predict(self, pairs: list[tuple[str, str]]) -> list[float]:
        return [0.5] * len(pairs)


def create_cross_encoder_from_env() -> CrossEncoderModel:
    """Create a cross-encoder based on CogMem config."""

    config = get_config()
    provider = config.reranker_provider.lower()

    if provider == "local":
        return LocalSTCrossEncoder(model_name=config.reranker_local_model)

    if provider == "tei":
        url = config.reranker_tei_url
        if not url:
            raise ValueError("COGMEM_API_RERANKER_TEI_URL is required when COGMEM_API_RERANKER_PROVIDER=tei")
        return RemoteTEICrossEncoder(base_url=url, batch_size=config.reranker_tei_batch_size)

    if provider == "rrf":
        return RRFPassthroughCrossEncoder()

    logger.warning(
        "Reranker provider '%s' is not implemented in CogMem; falling back to rrf passthrough.",
        provider,
    )
    return RRFPassthroughCrossEncoder()
