"""Minimal cross-encoder abstraction for CogMem search reranking."""

from __future__ import annotations

import logging
from abc import ABC, abstractmethod

from ..config import get_config

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
    """Create a cross-encoder based on CogMem config.

    T3.1 keeps a lightweight default to avoid introducing extra runtime dependencies.
    """

    config = get_config()
    provider = config.reranker_provider.lower()
    if provider != "rrf":
        logger.warning("Reranker provider '%s' is not implemented in CogMem baseline; using rrf passthrough.", provider)
    return RRFPassthroughCrossEncoder()
