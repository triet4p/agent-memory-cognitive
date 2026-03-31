"""CogMem configuration surface used by forked engine and runtime modules."""

from __future__ import annotations

import os
from dataclasses import dataclass

try:
    from dotenv import find_dotenv, load_dotenv

    load_dotenv(find_dotenv(usecwd=True), override=True)
except ImportError:
    # python-dotenv is optional at import time and available in runtime images.
    pass

ENV_DATABASE_URL = "COGMEM_API_DATABASE_URL"
ENV_DATABASE_SCHEMA = "COGMEM_API_DATABASE_SCHEMA"
ENV_HOST = "COGMEM_API_HOST"
ENV_PORT = "COGMEM_API_PORT"
ENV_LOG_LEVEL = "COGMEM_API_LOG_LEVEL"
ENV_WORKERS = "COGMEM_API_WORKERS"
ENV_LLM_PROVIDER = "COGMEM_API_LLM_PROVIDER"
ENV_LLM_MODEL = "COGMEM_API_LLM_MODEL"
ENV_LLM_API_KEY = "COGMEM_API_LLM_API_KEY"
ENV_DB_POOL_MIN_SIZE = "COGMEM_API_DB_POOL_MIN_SIZE"
ENV_DB_POOL_MAX_SIZE = "COGMEM_API_DB_POOL_MAX_SIZE"

DEFAULT_EMBEDDING_DIMENSION = 384
EMBEDDING_DIMENSION = DEFAULT_EMBEDDING_DIMENSION

DEFAULT_DATABASE_URL = "pg0"
DEFAULT_DATABASE_SCHEMA = "public"
DEFAULT_HOST = "0.0.0.0"
DEFAULT_PORT = 8888
DEFAULT_LOG_LEVEL = "info"
DEFAULT_WORKERS = 1
DEFAULT_LLM_PROVIDER = "openai"
DEFAULT_LLM_MODEL = "gpt-4o-mini"
DEFAULT_DB_POOL_MIN_SIZE = 2
DEFAULT_DB_POOL_MAX_SIZE = 10

DATABASE_SCHEMA = os.getenv(ENV_DATABASE_SCHEMA, DEFAULT_DATABASE_SCHEMA)
DB_POOL_MIN_SIZE = int(os.getenv(ENV_DB_POOL_MIN_SIZE, str(DEFAULT_DB_POOL_MIN_SIZE)))
DB_POOL_MAX_SIZE = int(os.getenv(ENV_DB_POOL_MAX_SIZE, str(DEFAULT_DB_POOL_MAX_SIZE)))

DEFAULT_GRAPH_RETRIEVER = "link_expansion"
DEFAULT_TEXT_SEARCH_EXTENSION = "native"
DEFAULT_MPFP_TOP_K_NEIGHBORS = 20
DEFAULT_RERANKER_PROVIDER = "rrf"
DEFAULT_BFS_REFRACTORY_STEPS = 1
DEFAULT_BFS_FIRING_QUOTA = 2
DEFAULT_BFS_ACTIVATION_SATURATION = 2.0


@dataclass(frozen=True)
class CogMemRuntimeConfig:
    """Runtime configuration used by service entrypoints and container boot."""

    database_url: str = DEFAULT_DATABASE_URL
    database_schema: str = DEFAULT_DATABASE_SCHEMA
    host: str = DEFAULT_HOST
    port: int = DEFAULT_PORT
    log_level: str = DEFAULT_LOG_LEVEL
    workers: int = DEFAULT_WORKERS
    llm_provider: str = DEFAULT_LLM_PROVIDER
    llm_model: str = DEFAULT_LLM_MODEL
    llm_api_key: str | None = None
    db_pool_min_size: int = DEFAULT_DB_POOL_MIN_SIZE
    db_pool_max_size: int = DEFAULT_DB_POOL_MAX_SIZE


@dataclass(frozen=True)
class CogMemConfig:
    """Runtime config view for modules that previously depended on HINDSIGHT config."""

    graph_retriever: str = DEFAULT_GRAPH_RETRIEVER
    text_search_extension: str = DEFAULT_TEXT_SEARCH_EXTENSION
    mpfp_top_k_neighbors: int = DEFAULT_MPFP_TOP_K_NEIGHBORS
    reranker_provider: str = DEFAULT_RERANKER_PROVIDER
    bfs_refractory_steps: int = DEFAULT_BFS_REFRACTORY_STEPS
    bfs_firing_quota: int = DEFAULT_BFS_FIRING_QUOTA
    bfs_activation_saturation: float = DEFAULT_BFS_ACTIVATION_SATURATION


_cached_config: CogMemConfig | None = None


def _get_raw_config() -> CogMemRuntimeConfig:
    """Load runtime config from COGMEM_API_* environment variables."""
    return CogMemRuntimeConfig(
        database_url=os.getenv(ENV_DATABASE_URL, DEFAULT_DATABASE_URL),
        database_schema=os.getenv(ENV_DATABASE_SCHEMA, DEFAULT_DATABASE_SCHEMA),
        host=os.getenv(ENV_HOST, DEFAULT_HOST),
        port=int(os.getenv(ENV_PORT, str(DEFAULT_PORT))),
        log_level=os.getenv(ENV_LOG_LEVEL, DEFAULT_LOG_LEVEL),
        workers=int(os.getenv(ENV_WORKERS, str(DEFAULT_WORKERS))),
        llm_provider=os.getenv(ENV_LLM_PROVIDER, DEFAULT_LLM_PROVIDER),
        llm_model=os.getenv(ENV_LLM_MODEL, DEFAULT_LLM_MODEL),
        llm_api_key=os.getenv(ENV_LLM_API_KEY),
        db_pool_min_size=int(os.getenv(ENV_DB_POOL_MIN_SIZE, str(DEFAULT_DB_POOL_MIN_SIZE))),
        db_pool_max_size=int(os.getenv(ENV_DB_POOL_MAX_SIZE, str(DEFAULT_DB_POOL_MAX_SIZE))),
    )


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
            bfs_refractory_steps=int(
                os.getenv("COGMEM_API_BFS_REFRACTORY_STEPS", str(DEFAULT_BFS_REFRACTORY_STEPS))
            ),
            bfs_firing_quota=int(os.getenv("COGMEM_API_BFS_FIRING_QUOTA", str(DEFAULT_BFS_FIRING_QUOTA))),
            bfs_activation_saturation=float(
                os.getenv("COGMEM_API_BFS_ACTIVATION_SATURATION", str(DEFAULT_BFS_ACTIVATION_SATURATION))
            ),
        )
    return _cached_config
