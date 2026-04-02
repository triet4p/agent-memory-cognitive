"""Embeddings abstraction for CogMem retain/recall pipelines."""

from __future__ import annotations

import hashlib
import importlib
import logging
import math
from abc import ABC, abstractmethod

from cogmem_api.config import EMBEDDING_DIMENSION, get_config

logger = logging.getLogger(__name__)


class Embeddings(ABC):
    """Abstract embeddings contract."""

    @property
    @abstractmethod
    def provider_name(self) -> str:
        pass

    @property
    @abstractmethod
    def dimension(self) -> int:
        pass

    @abstractmethod
    async def initialize(self) -> None:
        pass

    @abstractmethod
    def encode(self, texts: list[str]) -> list[list[float]]:
        pass


class DeterministicEmbeddings(Embeddings):
    """Dependency-free fallback embeddings.

    This keeps retain/recall runnable even when optional model providers are unavailable.
    """

    def __init__(self, dimension: int = EMBEDDING_DIMENSION):
        self._dimension = max(1, int(dimension))

    @property
    def provider_name(self) -> str:
        return "deterministic"

    @property
    def dimension(self) -> int:
        return self._dimension

    async def initialize(self) -> None:
        return None

    def _embed_one(self, text: str) -> list[float]:
        vector = [0.0] * self._dimension
        if not text:
            return vector

        for token in text.split():
            digest = hashlib.sha256(token.encode("utf-8")).digest()
            slot = int.from_bytes(digest[:4], "big") % self._dimension
            raw = int.from_bytes(digest[4:8], "big") / 0xFFFFFFFF
            vector[slot] += raw

        norm = math.sqrt(sum(value * value for value in vector))
        if norm <= 0:
            return vector
        return [value / norm for value in vector]

    def encode(self, texts: list[str]) -> list[list[float]]:
        return [self._embed_one(text) for text in texts]


class LocalSTEmbeddings(Embeddings):
    """SentenceTransformers local embeddings provider."""

    def __init__(self, model_name: str):
        self.model_name = model_name
        self._model = None
        self._dimension: int | None = None

    @property
    def provider_name(self) -> str:
        return "local"

    @property
    def dimension(self) -> int:
        if self._dimension is None:
            raise RuntimeError("Embeddings not initialized. Call initialize() first.")
        return self._dimension

    async def initialize(self) -> None:
        if self._model is not None:
            return

        try:
            module = importlib.import_module("sentence_transformers")
            SentenceTransformer = getattr(module, "SentenceTransformer")
        except ImportError as exc:  # pragma: no cover - optional dependency
            raise ImportError(
                "sentence-transformers is required for local embeddings. Install with: uv add sentence-transformers"
            ) from exc

        self._model = SentenceTransformer(self.model_name)
        self._dimension = int(self._model.get_sentence_embedding_dimension())
        logger.info("Embeddings: initialized local provider with model %s (dim=%s)", self.model_name, self._dimension)

    def encode(self, texts: list[str]) -> list[list[float]]:
        if self._model is None:
            raise RuntimeError("Embeddings not initialized. Call initialize() first.")
        vectors = self._model.encode(texts, convert_to_numpy=True, show_progress_bar=False)
        return [vector.tolist() for vector in vectors]


class OpenAIEmbeddings(Embeddings):
    """OpenAI-compatible embeddings provider."""

    MODEL_DIMENSIONS = {
        "text-embedding-3-small": 1536,
        "text-embedding-3-large": 3072,
        "text-embedding-ada-002": 1536,
    }

    def __init__(self, api_key: str, model: str, base_url: str | None = None):
        self.api_key = api_key
        self.model = model
        self.base_url = base_url
        self._client = None
        self._dimension: int | None = None

    @property
    def provider_name(self) -> str:
        return "openai"

    @property
    def dimension(self) -> int:
        if self._dimension is None:
            raise RuntimeError("Embeddings not initialized. Call initialize() first.")
        return self._dimension

    async def initialize(self) -> None:
        if self._client is not None:
            return

        try:
            module = importlib.import_module("openai")
            OpenAI = getattr(module, "OpenAI")
        except ImportError as exc:  # pragma: no cover - optional dependency
            raise ImportError("openai is required for openai embeddings. Install with: uv add openai") from exc

        kwargs: dict[str, str] = {"api_key": self.api_key}
        if self.base_url:
            kwargs["base_url"] = self.base_url
        self._client = OpenAI(**kwargs)

        if self.model in self.MODEL_DIMENSIONS:
            self._dimension = self.MODEL_DIMENSIONS[self.model]
        else:
            response = self._client.embeddings.create(model=self.model, input=["dimension probe"])
            self._dimension = len(response.data[0].embedding)

        logger.info("Embeddings: initialized openai provider with model %s (dim=%s)", self.model, self._dimension)

    def encode(self, texts: list[str]) -> list[list[float]]:
        if self._client is None:
            raise RuntimeError("Embeddings not initialized. Call initialize() first.")
        if not texts:
            return []

        response = self._client.embeddings.create(model=self.model, input=texts)
        ordered = sorted(response.data, key=lambda item: item.index)
        return [item.embedding for item in ordered]


def create_embeddings_from_env() -> Embeddings:
    """Create configured embeddings provider with deterministic fallback."""

    config = get_config()
    provider = config.embeddings_provider.lower()

    if provider == "local":
        return LocalSTEmbeddings(model_name=config.embeddings_local_model)

    if provider == "openai":
        api_key = config.embeddings_openai_api_key
        if not api_key:
            raise ValueError("COGMEM_API_EMBEDDINGS_OPENAI_API_KEY is required when COGMEM_API_EMBEDDINGS_PROVIDER=openai")
        return OpenAIEmbeddings(
            api_key=api_key,
            model=config.embeddings_openai_model,
            base_url=config.embeddings_openai_base_url,
        )

    if provider == "deterministic":
        return DeterministicEmbeddings()

    raise ValueError(
        f"Unknown embeddings provider: {provider}. Supported providers: local, openai, deterministic"
    )
