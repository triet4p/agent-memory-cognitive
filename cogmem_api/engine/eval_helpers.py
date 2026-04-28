"""Evaluation helper utilities for generation prompts and judge prompts.

Separated from LLM business logic to keep eval pipeline clean.
Used by cogmem_api HTTP endpoints (/generate, /judge).

Note: Prompt building logic has been moved to cogmem_api.prompts.
eval_helpers now re-exports from there for backward compatibility.
"""

from __future__ import annotations

from cogmem_api.prompts.eval.judge import build_judge_system_prompt as _bj, parse_judge_response as _pjr
from cogmem_api.prompts.eval.generate import build_generation_prompt as _bgp


def build_generation_prompt(query: str, evidence: list[dict]) -> str:
    return _bgp(query, evidence)


def build_judge_system_prompt(category: str | None) -> str:
    return _bj(category)


def parse_judge_response(raw: str) -> dict:
    return _pjr(raw)