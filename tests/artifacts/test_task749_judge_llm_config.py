"""Task 749: S22.1 — Judge LLM config gate.

Verifies:
- resolve_eval_llm_config() raises ValueError when COGMEM_EVAL_LLM_MODEL is unset
- resolve_eval_llm_config() raises ValueError when COGMEM_EVAL_LLM_BASE_URL is unset
- ValueError message mentions both env vars and >= 7B requirement
- Returns EvalLLMConfig when both vars are set (mocked)
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.eval_cogmem import resolve_eval_llm_config, EvalLLMConfig


def _clear_eval_env():
    for key in ["COGMEM_EVAL_LLM_MODEL", "COGMEM_EVAL_LLM_BASE_URL", "COGMEM_EVAL_LLM_PROVIDER", "COGMEM_EVAL_LLM_API_KEY", "COGMEM_EVAL_LLM_TIMEOUT", "COGMEM_EVAL_MAX_COMPLETION_TOKENS"]:
        os.environ.pop(key, None)


def _run_with_env(test_fn, **env_vars):
    saved = {k: os.environ.get(k) for k in env_vars}
    _clear_eval_env()
    for k, v in env_vars.items():
        if v is not None:
            os.environ[k] = v
    try:
        test_fn()
    finally:
        _clear_eval_env()
        for k, v in saved.items():
            if v is not None:
                os.environ[k] = v


def test_raises_when_model_unset():
    def _inner():
        try:
            resolve_eval_llm_config()
            assert False, "Expected ValueError"
        except ValueError as e:
            msg = str(e)
            assert "COGMEM_EVAL_LLM_MODEL" in msg
            assert "COGMEM_EVAL_LLM_BASE_URL" in msg
            assert "7B" in msg or ">= 7B" in msg
    _run_with_env(_inner, COGMEM_EVAL_LLM_BASE_URL="http://localhost:8889/v1")


def test_raises_when_base_url_unset():
    def _inner():
        try:
            resolve_eval_llm_config()
            assert False, "Expected ValueError"
        except ValueError as e:
            msg = str(e)
            assert "COGMEM_EVAL_LLM_MODEL" in msg
            assert "COGMEM_EVAL_LLM_BASE_URL" in msg
    _run_with_env(_inner, COGMEM_EVAL_LLM_MODEL="Qwen3-8B")


def test_raises_when_both_unset():
    def _inner():
        try:
            resolve_eval_llm_config()
            assert False, "Expected ValueError"
        except ValueError as e:
            msg = str(e)
            assert "COGMEM_EVAL_LLM_MODEL" in msg
            assert "COGMEM_EVAL_LLM_BASE_URL" in msg
    _run_with_env(_inner)


def test_returns_config_when_both_set():
    saved = {}
    for k in ["COGMEM_EVAL_LLM_MODEL", "COGMEM_EVAL_LLM_BASE_URL", "COGMEM_EVAL_LLM_API_KEY"]:
        saved[k] = os.environ.get(k)
    _clear_eval_env()
    os.environ["COGMEM_EVAL_LLM_MODEL"] = "Qwen3-8B"
    os.environ["COGMEM_EVAL_LLM_BASE_URL"] = "http://localhost:8889/v1"
    os.environ["COGMEM_EVAL_LLM_API_KEY"] = "test-key"
    try:
        config = resolve_eval_llm_config()
        assert isinstance(config, EvalLLMConfig)
        assert config.model == "Qwen3-8B"
        assert config.base_url == "http://localhost:8889/v1"
        assert config.provider == "openai"
        assert config.api_key == "test-key"
    finally:
        _clear_eval_env()
        for k, v in saved.items():
            if v is not None:
                os.environ[k] = v


if __name__ == "__main__":
    print("Task 749 judge LLM config gate tests")
    test_raises_when_model_unset()
    print("  test_raises_when_model_unset PASSED")
    test_raises_when_base_url_unset()
    print("  test_raises_when_base_url_unset PASSED")
    test_raises_when_both_unset()
    print("  test_raises_when_both_unset PASSED")
    test_returns_config_when_both_set()
    print("  test_returns_config_when_both_set PASSED")
    print("Task 749 judge LLM config gate passed.")