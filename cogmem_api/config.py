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
ENV_LLM_BASE_URL = "COGMEM_API_LLM_BASE_URL"
ENV_LLM_TIMEOUT = "COGMEM_API_LLM_TIMEOUT"
ENV_RETAIN_LLM_TIMEOUT = "COGMEM_API_RETAIN_LLM_TIMEOUT"
ENV_REFLECT_LLM_TIMEOUT = "COGMEM_API_REFLECT_LLM_TIMEOUT"
ENV_RETAIN_MAX_COMPLETION_TOKENS = "COGMEM_API_RETAIN_MAX_COMPLETION_TOKENS"
ENV_RETAIN_CHUNK_SIZE = "COGMEM_API_RETAIN_CHUNK_SIZE"
ENV_RETAIN_EXTRACT_CAUSAL_LINKS = "COGMEM_API_RETAIN_EXTRACT_CAUSAL_LINKS"
ENV_RETAIN_EXTRACTION_MODE = "COGMEM_API_RETAIN_EXTRACTION_MODE"
ENV_RETAIN_MISSION = "COGMEM_API_RETAIN_MISSION"
ENV_RETAIN_CUSTOM_INSTRUCTIONS = "COGMEM_API_RETAIN_CUSTOM_INSTRUCTIONS"
ENV_RECALL_MAX_CONCURRENT = "COGMEM_API_RECALL_MAX_CONCURRENT"
ENV_DB_POOL_MIN_SIZE = "COGMEM_API_DB_POOL_MIN_SIZE"
ENV_DB_POOL_MAX_SIZE = "COGMEM_API_DB_POOL_MAX_SIZE"
ENV_GRAPH_RETRIEVER = "COGMEM_API_GRAPH_RETRIEVER"
ENV_TEXT_SEARCH_EXTENSION = "COGMEM_API_TEXT_SEARCH_EXTENSION"
ENV_MPFP_TOP_K_NEIGHBORS = "COGMEM_API_MPFP_TOP_K_NEIGHBORS"
ENV_BFS_REFRACTORY_STEPS = "COGMEM_API_BFS_REFRACTORY_STEPS"
ENV_BFS_FIRING_QUOTA = "COGMEM_API_BFS_FIRING_QUOTA"
ENV_BFS_ACTIVATION_SATURATION = "COGMEM_API_BFS_ACTIVATION_SATURATION"

ENV_EMBEDDINGS_PROVIDER = "COGMEM_API_EMBEDDINGS_PROVIDER"
ENV_EMBEDDINGS_LOCAL_MODEL = "COGMEM_API_EMBEDDINGS_LOCAL_MODEL"
ENV_EMBEDDINGS_OPENAI_MODEL = "COGMEM_API_EMBEDDINGS_OPENAI_MODEL"
ENV_EMBEDDINGS_OPENAI_BASE_URL = "COGMEM_API_EMBEDDINGS_OPENAI_BASE_URL"
ENV_EMBEDDINGS_OPENAI_API_KEY = "COGMEM_API_EMBEDDINGS_OPENAI_API_KEY"

ENV_RERANKER_PROVIDER = "COGMEM_API_RERANKER_PROVIDER"
ENV_RERANKER_LOCAL_MODEL = "COGMEM_API_RERANKER_LOCAL_MODEL"
ENV_RERANKER_TEI_URL = "COGMEM_API_RERANKER_TEI_URL"
ENV_RERANKER_TEI_BATCH_SIZE = "COGMEM_API_RERANKER_TEI_BATCH_SIZE"
ENV_RERANKER_MAX_CANDIDATES = "COGMEM_API_RERANKER_MAX_CANDIDATES"

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
DEFAULT_LLM_BASE_URL = None
DEFAULT_LLM_TIMEOUT = 120.0
DEFAULT_RETAIN_LLM_TIMEOUT = 120.0
DEFAULT_REFLECT_LLM_TIMEOUT = 120.0
DEFAULT_RETAIN_MAX_COMPLETION_TOKENS = 64000
DEFAULT_RETAIN_CHUNK_SIZE = 3000
DEFAULT_RETAIN_EXTRACT_CAUSAL_LINKS = True
DEFAULT_RETAIN_EXTRACTION_MODE = "concise"
DEFAULT_RETAIN_MISSION = None
DEFAULT_RETAIN_CUSTOM_INSTRUCTIONS = None
DEFAULT_RECALL_MAX_CONCURRENT = 32
DEFAULT_DB_POOL_MIN_SIZE = 2
DEFAULT_DB_POOL_MAX_SIZE = 10

DATABASE_SCHEMA = os.getenv(ENV_DATABASE_SCHEMA, DEFAULT_DATABASE_SCHEMA)
DB_POOL_MIN_SIZE = int(os.getenv(ENV_DB_POOL_MIN_SIZE, str(DEFAULT_DB_POOL_MIN_SIZE)))
DB_POOL_MAX_SIZE = int(os.getenv(ENV_DB_POOL_MAX_SIZE, str(DEFAULT_DB_POOL_MAX_SIZE)))

DEFAULT_GRAPH_RETRIEVER = "link_expansion"
DEFAULT_TEXT_SEARCH_EXTENSION = "native"
DEFAULT_MPFP_TOP_K_NEIGHBORS = 20
DEFAULT_RERANKER_PROVIDER = "rrf"
DEFAULT_RERANKER_LOCAL_MODEL = "cross-encoder/ms-marco-MiniLM-L-6-v2"
DEFAULT_RERANKER_TEI_BATCH_SIZE = 128
DEFAULT_RERANKER_MAX_CANDIDATES = 300
DEFAULT_BFS_REFRACTORY_STEPS = 1
DEFAULT_BFS_FIRING_QUOTA = 2
DEFAULT_BFS_ACTIVATION_SATURATION = 2.0
DEFAULT_EMBEDDINGS_PROVIDER = "local"
DEFAULT_EMBEDDINGS_LOCAL_MODEL = "BAAI/bge-small-en-v1.5"
DEFAULT_EMBEDDINGS_OPENAI_MODEL = "text-embedding-3-small"

ALLOWED_RETAIN_EXTRACTION_MODES = {"concise", "custom", "verbatim", "verbose"}


def _read_optional_str(env_name: str, default: str | None = None) -> str | None:
    value = os.getenv(env_name)
    if value is None:
        return default
    normalized = value.strip()
    if not normalized:
        return default
    return normalized


def _read_int(env_name: str, default: int, minimum: int | None = None) -> int:
    raw = os.getenv(env_name)
    if raw is None:
        candidate = default
    else:
        try:
            candidate = int(raw)
        except ValueError:
            candidate = default
    if minimum is not None:
        return max(minimum, candidate)
    return candidate


def _read_float(env_name: str, default: float, minimum: float | None = None) -> float:
    raw = os.getenv(env_name)
    if raw is None:
        candidate = default
    else:
        try:
            candidate = float(raw)
        except ValueError:
            candidate = default
    if minimum is not None:
        return max(minimum, candidate)
    return candidate


def _read_bool(env_name: str, default: bool) -> bool:
    raw = os.getenv(env_name)
    if raw is None:
        return default
    normalized = raw.strip().lower()
    if normalized in {"1", "true", "yes", "y", "on"}:
        return True
    if normalized in {"0", "false", "no", "n", "off"}:
        return False
    return default


def _read_retain_extraction_mode() -> str:
    mode = _read_optional_str(ENV_RETAIN_EXTRACTION_MODE, DEFAULT_RETAIN_EXTRACTION_MODE)
    assert mode is not None
    normalized = mode.lower()
    if normalized in ALLOWED_RETAIN_EXTRACTION_MODES:
        return normalized
    return DEFAULT_RETAIN_EXTRACTION_MODE


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
    llm_base_url: str | None = DEFAULT_LLM_BASE_URL
    llm_timeout: float = DEFAULT_LLM_TIMEOUT
    retain_llm_timeout: float = DEFAULT_RETAIN_LLM_TIMEOUT
    reflect_llm_timeout: float = DEFAULT_REFLECT_LLM_TIMEOUT
    retain_max_completion_tokens: int = DEFAULT_RETAIN_MAX_COMPLETION_TOKENS
    retain_chunk_size: int = DEFAULT_RETAIN_CHUNK_SIZE
    retain_extract_causal_links: bool = DEFAULT_RETAIN_EXTRACT_CAUSAL_LINKS
    retain_extraction_mode: str = DEFAULT_RETAIN_EXTRACTION_MODE
    retain_mission: str | None = DEFAULT_RETAIN_MISSION
    retain_custom_instructions: str | None = DEFAULT_RETAIN_CUSTOM_INSTRUCTIONS
    recall_max_concurrent: int = DEFAULT_RECALL_MAX_CONCURRENT
    db_pool_min_size: int = DEFAULT_DB_POOL_MIN_SIZE
    db_pool_max_size: int = DEFAULT_DB_POOL_MAX_SIZE


@dataclass(frozen=True)
class CogMemConfig:
    """Runtime config view for modules that previously depended on HINDSIGHT config."""

    graph_retriever: str = DEFAULT_GRAPH_RETRIEVER
    text_search_extension: str = DEFAULT_TEXT_SEARCH_EXTENSION
    mpfp_top_k_neighbors: int = DEFAULT_MPFP_TOP_K_NEIGHBORS
    recall_max_concurrent: int = DEFAULT_RECALL_MAX_CONCURRENT
    reranker_provider: str = DEFAULT_RERANKER_PROVIDER
    reranker_local_model: str = DEFAULT_RERANKER_LOCAL_MODEL
    reranker_tei_url: str | None = None
    reranker_tei_batch_size: int = DEFAULT_RERANKER_TEI_BATCH_SIZE
    reranker_max_candidates: int = DEFAULT_RERANKER_MAX_CANDIDATES
    embeddings_provider: str = DEFAULT_EMBEDDINGS_PROVIDER
    embeddings_local_model: str = DEFAULT_EMBEDDINGS_LOCAL_MODEL
    embeddings_openai_model: str = DEFAULT_EMBEDDINGS_OPENAI_MODEL
    embeddings_openai_base_url: str | None = None
    embeddings_openai_api_key: str | None = None
    llm_base_url: str | None = DEFAULT_LLM_BASE_URL
    llm_timeout: float = DEFAULT_LLM_TIMEOUT
    retain_llm_timeout: float = DEFAULT_RETAIN_LLM_TIMEOUT
    reflect_llm_timeout: float = DEFAULT_REFLECT_LLM_TIMEOUT
    retain_max_completion_tokens: int = DEFAULT_RETAIN_MAX_COMPLETION_TOKENS
    retain_chunk_size: int = DEFAULT_RETAIN_CHUNK_SIZE
    retain_extract_causal_links: bool = DEFAULT_RETAIN_EXTRACT_CAUSAL_LINKS
    retain_extraction_mode: str = DEFAULT_RETAIN_EXTRACTION_MODE
    retain_mission: str | None = DEFAULT_RETAIN_MISSION
    retain_custom_instructions: str | None = DEFAULT_RETAIN_CUSTOM_INSTRUCTIONS
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
        port=_read_int(ENV_PORT, DEFAULT_PORT, minimum=1),
        log_level=os.getenv(ENV_LOG_LEVEL, DEFAULT_LOG_LEVEL),
        workers=_read_int(ENV_WORKERS, DEFAULT_WORKERS, minimum=1),
        llm_provider=os.getenv(ENV_LLM_PROVIDER, DEFAULT_LLM_PROVIDER),
        llm_model=os.getenv(ENV_LLM_MODEL, DEFAULT_LLM_MODEL),
        llm_api_key=_read_optional_str(ENV_LLM_API_KEY),
        llm_base_url=_read_optional_str(ENV_LLM_BASE_URL, DEFAULT_LLM_BASE_URL),
        llm_timeout=_read_float(ENV_LLM_TIMEOUT, DEFAULT_LLM_TIMEOUT, minimum=0.1),
        retain_llm_timeout=_read_float(ENV_RETAIN_LLM_TIMEOUT, DEFAULT_RETAIN_LLM_TIMEOUT, minimum=0.1),
        reflect_llm_timeout=_read_float(ENV_REFLECT_LLM_TIMEOUT, DEFAULT_REFLECT_LLM_TIMEOUT, minimum=0.1),
        retain_max_completion_tokens=_read_int(
            ENV_RETAIN_MAX_COMPLETION_TOKENS,
            DEFAULT_RETAIN_MAX_COMPLETION_TOKENS,
            minimum=1,
        ),
        retain_chunk_size=_read_int(ENV_RETAIN_CHUNK_SIZE, DEFAULT_RETAIN_CHUNK_SIZE, minimum=1),
        retain_extract_causal_links=_read_bool(ENV_RETAIN_EXTRACT_CAUSAL_LINKS, DEFAULT_RETAIN_EXTRACT_CAUSAL_LINKS),
        retain_extraction_mode=_read_retain_extraction_mode(),
        retain_mission=_read_optional_str(ENV_RETAIN_MISSION, DEFAULT_RETAIN_MISSION),
        retain_custom_instructions=_read_optional_str(
            ENV_RETAIN_CUSTOM_INSTRUCTIONS,
            DEFAULT_RETAIN_CUSTOM_INSTRUCTIONS,
        ),
        recall_max_concurrent=_read_int(ENV_RECALL_MAX_CONCURRENT, DEFAULT_RECALL_MAX_CONCURRENT, minimum=1),
        db_pool_min_size=_read_int(ENV_DB_POOL_MIN_SIZE, DEFAULT_DB_POOL_MIN_SIZE, minimum=1),
        db_pool_max_size=_read_int(ENV_DB_POOL_MAX_SIZE, DEFAULT_DB_POOL_MAX_SIZE, minimum=1),
    )


def get_config() -> CogMemConfig:
    """Return cached config values used by the CogMem engine modules."""
    global _cached_config
    if _cached_config is None:
        runtime = _get_raw_config()
        _cached_config = CogMemConfig(
            graph_retriever=os.getenv(ENV_GRAPH_RETRIEVER, DEFAULT_GRAPH_RETRIEVER),
            text_search_extension=os.getenv(ENV_TEXT_SEARCH_EXTENSION, DEFAULT_TEXT_SEARCH_EXTENSION),
            mpfp_top_k_neighbors=_read_int(ENV_MPFP_TOP_K_NEIGHBORS, DEFAULT_MPFP_TOP_K_NEIGHBORS, minimum=1),
            recall_max_concurrent=runtime.recall_max_concurrent,
            reranker_provider=os.getenv(ENV_RERANKER_PROVIDER, DEFAULT_RERANKER_PROVIDER),
            reranker_local_model=os.getenv(ENV_RERANKER_LOCAL_MODEL, DEFAULT_RERANKER_LOCAL_MODEL),
            reranker_tei_url=_read_optional_str(ENV_RERANKER_TEI_URL),
            reranker_tei_batch_size=_read_int(
                ENV_RERANKER_TEI_BATCH_SIZE,
                DEFAULT_RERANKER_TEI_BATCH_SIZE,
                minimum=1,
            ),
            reranker_max_candidates=_read_int(
                ENV_RERANKER_MAX_CANDIDATES,
                DEFAULT_RERANKER_MAX_CANDIDATES,
                minimum=1,
            ),
            embeddings_provider=os.getenv(ENV_EMBEDDINGS_PROVIDER, DEFAULT_EMBEDDINGS_PROVIDER),
            embeddings_local_model=os.getenv(ENV_EMBEDDINGS_LOCAL_MODEL, DEFAULT_EMBEDDINGS_LOCAL_MODEL),
            embeddings_openai_model=os.getenv(ENV_EMBEDDINGS_OPENAI_MODEL, DEFAULT_EMBEDDINGS_OPENAI_MODEL),
            embeddings_openai_base_url=_read_optional_str(ENV_EMBEDDINGS_OPENAI_BASE_URL),
            embeddings_openai_api_key=_read_optional_str(ENV_EMBEDDINGS_OPENAI_API_KEY),
            llm_base_url=runtime.llm_base_url,
            llm_timeout=runtime.llm_timeout,
            retain_llm_timeout=runtime.retain_llm_timeout,
            reflect_llm_timeout=runtime.reflect_llm_timeout,
            retain_max_completion_tokens=runtime.retain_max_completion_tokens,
            retain_chunk_size=runtime.retain_chunk_size,
            retain_extract_causal_links=runtime.retain_extract_causal_links,
            retain_extraction_mode=runtime.retain_extraction_mode,
            retain_mission=runtime.retain_mission,
            retain_custom_instructions=runtime.retain_custom_instructions,
            bfs_refractory_steps=_read_int(ENV_BFS_REFRACTORY_STEPS, DEFAULT_BFS_REFRACTORY_STEPS, minimum=1),
            bfs_firing_quota=_read_int(ENV_BFS_FIRING_QUOTA, DEFAULT_BFS_FIRING_QUOTA, minimum=1),
            bfs_activation_saturation=_read_float(
                ENV_BFS_ACTIVATION_SATURATION,
                DEFAULT_BFS_ACTIVATION_SATURATION,
                minimum=0.1,
            ),
        )
    return _cached_config
