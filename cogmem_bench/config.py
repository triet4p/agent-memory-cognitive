"""Resolve the conversation-generation (Minimax) LLM config.

Deliberately a *separate* model from the retain/answer model (Ministral-3B,
configured via COGMEM_API_LLM_*). Cross-model generation avoids the generator
and the reader sharing blind spots — see docs/Ablation-Flow.md step 2.
"""

from __future__ import annotations

import os

from cogmem_api.engine.llm_wrapper import LLMConfig

ENV_GEN_BASE_URL = "COGMEM_BENCH_GEN_LLM_BASE_URL"
ENV_GEN_MODEL = "COGMEM_BENCH_GEN_LLM_MODEL"
ENV_GEN_API_KEY = "COGMEM_BENCH_GEN_LLM_API_KEY"
ENV_GEN_TIMEOUT = "COGMEM_BENCH_GEN_LLM_TIMEOUT"
ENV_GEN_LAST_K_VERBATIM = "COGMEM_BENCH_GEN_LAST_K_VERBATIM"

DEFAULT_GEN_MODEL = "minimax-m2"
DEFAULT_GEN_TIMEOUT = 600.0
DEFAULT_LAST_K_VERBATIM = 2


def _env(name: str) -> str | None:
    value = os.getenv(name)
    return value.strip() if value and value.strip() else None


def resolve_generation_llm() -> LLMConfig:
    """Build the Minimax generation LLMConfig from COGMEM_BENCH_GEN_LLM_* env vars.

    Raises ValueError if no base_url is configured (generation cannot run offline).
    """
    base_url = _env(ENV_GEN_BASE_URL)
    if not base_url:
        raise ValueError(
            f"{ENV_GEN_BASE_URL} is required for conversation generation "
            "(the strong cross-model generator, e.g. Minimax-M2)."
        )
    timeout_raw = _env(ENV_GEN_TIMEOUT)
    try:
        timeout = float(timeout_raw) if timeout_raw else DEFAULT_GEN_TIMEOUT
    except ValueError:
        timeout = DEFAULT_GEN_TIMEOUT

    return LLMConfig(
        provider="openai",
        model=_env(ENV_GEN_MODEL) or DEFAULT_GEN_MODEL,
        api_key=_env(ENV_GEN_API_KEY) or "ollama",
        base_url=base_url,
        timeout=timeout,
    )


def resolve_last_k_verbatim(override: int | None = None) -> int:
    """Number of recent sessions passed verbatim for cross-session consistency.

    Precedence: CLI override > COGMEM_BENCH_GEN_LAST_K_VERBATIM env > default (2).
    """
    if override is not None:
        return max(0, override)
    raw = _env(ENV_GEN_LAST_K_VERBATIM)
    if not raw:
        return DEFAULT_LAST_K_VERBATIM
    try:
        return max(0, int(raw))
    except ValueError:
        return DEFAULT_LAST_K_VERBATIM
