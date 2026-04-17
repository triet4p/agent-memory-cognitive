"""Shared utilities for retain dialogue tests.

Provides:
  - REPO_ROOT         : absolute path to repo root
  - setup_path()      : add REPO_ROOT to sys.path once
  - _BaseFakeLLM      : offline fake LLM returning a canned response dict
  - resolve_llm(fake) : real LLMConfig from env vars, or FakeLLM fallback
  - make_config(mode) : retain config SimpleNamespace reading from env vars
"""

from __future__ import annotations

import os
import sys
from pathlib import Path
from types import SimpleNamespace
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]


def setup_path() -> None:
    """Insert REPO_ROOT into sys.path so cogmem_api and tests packages resolve."""
    root_str = str(REPO_ROOT)
    if root_str not in sys.path:
        sys.path.insert(0, root_str)


class _BaseFakeLLM:
    """Offline fake LLM — returns a pre-canned dict response without network calls."""

    def __init__(self, response: Any) -> None:
        self._response = response

    async def call(self, messages: list[dict[str, str]], **kwargs: Any) -> Any:
        from cogmem_api.engine.response_models import TokenUsage
        return self._response, TokenUsage(input_tokens=100, output_tokens=80, total_tokens=180)


def resolve_llm(fake_response: Any) -> Any:
    """Return real LLMConfig when COGMEM_API_LLM_BASE_URL is set, else FakeLLM.

    Real mode reads:
      COGMEM_API_LLM_BASE_URL         — e.g. NGROK URL ending with /v1
      COGMEM_API_LLM_MODEL            — default: ministral3-3b
      COGMEM_API_LLM_API_KEY          — default: ollama
      COGMEM_API_RETAIN_LLM_TIMEOUT   — default: 600 seconds
    """
    base_url = os.getenv("COGMEM_API_LLM_BASE_URL", "").strip()
    if base_url:
        from cogmem_api.engine.llm_wrapper import LLMConfig
        model = os.getenv("COGMEM_API_LLM_MODEL", "ministral3-3b")
        api_key = os.getenv("COGMEM_API_LLM_API_KEY", "ollama")
        timeout = float(
            os.getenv("COGMEM_API_RETAIN_LLM_TIMEOUT")
            or os.getenv("COGMEM_API_LLM_TIMEOUT")
            or "600"
        )
        print(f"[LLM] real — {base_url}  model={model}")
        return LLMConfig(
            provider="openai",
            model=model,
            api_key=api_key,
            base_url=base_url,
            timeout=timeout,
        )
    print("[LLM] offline — FakeLLM")
    return _BaseFakeLLM(fake_response)


def make_config(mode: str = "concise") -> SimpleNamespace:
    """Build retain pipeline config, preferring env vars over provided defaults.

    Env vars:
      COGMEM_API_RETAIN_EXTRACTION_MODE         — concise | verbose | verbatim | custom
      COGMEM_API_RETAIN_MAX_COMPLETION_TOKENS   — default: 13000
      COGMEM_API_RETAIN_CHUNK_SIZE              — default: 3000
      COGMEM_API_RETAIN_MISSION                 — optional mission string
      COGMEM_API_RETAIN_CUSTOM_INSTRUCTIONS     — optional custom instructions
    """
    return SimpleNamespace(
        retain_extraction_mode=os.getenv("COGMEM_API_RETAIN_EXTRACTION_MODE", mode),
        retain_max_completion_tokens=int(
            os.getenv("COGMEM_API_RETAIN_MAX_COMPLETION_TOKENS") or "13000"
        ),
        retain_chunk_size=int(os.getenv("COGMEM_API_RETAIN_CHUNK_SIZE") or "3000"),
        retain_mission=os.getenv("COGMEM_API_RETAIN_MISSION"),
        retain_custom_instructions=os.getenv("COGMEM_API_RETAIN_CUSTOM_INSTRUCTIONS"),
        retain_extract_causal_links=True,
    )
