"""CogMem configuration surface used by forked engine modules."""

from __future__ import annotations

import os
from dataclasses import dataclass

DEFAULT_EMBEDDING_DIMENSION = 384
EMBEDDING_DIMENSION = DEFAULT_EMBEDDING_DIMENSION

DEFAULT_DATABASE_SCHEMA = "public"
DATABASE_SCHEMA = os.getenv("COGMEM_API_DATABASE_SCHEMA", DEFAULT_DATABASE_SCHEMA)

DEFAULT_DB_POOL_MIN_SIZE = 2
DB_POOL_MIN_SIZE = int(os.getenv("COGMEM_API_DB_POOL_MIN_SIZE", str(DEFAULT_DB_POOL_MIN_SIZE)))

DEFAULT_DB_POOL_MAX_SIZE = 10
DB_POOL_MAX_SIZE = int(os.getenv("COGMEM_API_DB_POOL_MAX_SIZE", str(DEFAULT_DB_POOL_MAX_SIZE)))

DEFAULT_GRAPH_RETRIEVER = "link_expansion"
DEFAULT_TEXT_SEARCH_EXTENSION = "native"
DEFAULT_MPFP_TOP_K_NEIGHBORS = 20
DEFAULT_RERANKER_PROVIDER = "rrf"


@dataclass(frozen=True)
class CogMemConfig:
    """Runtime config view for modules that previously depended on HINDSIGHT config."""

    graph_retriever: str = DEFAULT_GRAPH_RETRIEVER
    text_search_extension: str = DEFAULT_TEXT_SEARCH_EXTENSION
    mpfp_top_k_neighbors: int = DEFAULT_MPFP_TOP_K_NEIGHBORS
    reranker_provider: str = DEFAULT_RERANKER_PROVIDER


_cached_config: CogMemConfig | None = None


def get_config() -> CogMemConfig:
    """Return cached config values used by the CogMem engine modules."""
    global _cached_config
    if _cached_config is None:
        _cached_config = CogMemConfig(
            graph_retriever=os.getenv("COGMEM_API_GRAPH_RETRIEVER", DEFAULT_GRAPH_RETRIEVER),
            text_search_extension=os.getenv("COGMEM_API_TEXT_SEARCH_EXTENSION", DEFAULT_TEXT_SEARCH_EXTENSION),
            mpfp_top_k_neighbors=int(
                os.getenv("COGMEM_API_MPFP_TOP_K_NEIGHBORS", str(DEFAULT_MPFP_TOP_K_NEIGHBORS))
            ),
            reranker_provider=os.getenv("COGMEM_API_RERANKER_PROVIDER", DEFAULT_RERANKER_PROVIDER),
        )
    return _cached_config
