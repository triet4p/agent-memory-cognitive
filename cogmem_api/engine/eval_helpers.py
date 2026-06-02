"""Evaluation helper utilities for generation prompts and judge prompts.

Separated from LLM business logic to keep eval pipeline clean.
Used by cogmem_api HTTP endpoints (/generate, /judge).

Note: Prompt building logic has been moved to cogmem_api.prompts.
eval_helpers now re-exports from there for backward compatibility.
"""

from __future__ import annotations

import os

from cogmem_api.prompts.eval.judge import build_judge_system_prompt as _bj, parse_judge_response as _pjr
from cogmem_api.prompts.eval.generate import (
    build_generation_prompt as _bgp_legacy,
    build_generation_prompt_v2 as _bgp_v2,
    build_generation_prompt_v3_temporal as _bgp_v3_temporal,
    build_generation_prompt_v3_temporal_list as _bgp_v3_temporal_list,
    build_generation_prompt_v4_evidence_guard as _bgp_v4_evidence_guard,
)


def build_generation_prompt(
    query: str,
    evidence: list[dict],
    question_date: str | None = None,
    session_date_map: dict[str, str] | None = None,
    include_snippets: bool = True,
) -> str:
    """Dispatch prompt builder based on COGMEM_API_GENERATE_PROMPT_VARIANT env.

    - Default (unset or 'legacy'): legacy prompt (S29-S34 runs reproduce byte-identically).
    - 'v2': S35 prompt v2 — tighter dedup criterion + inline raw_snippet under each
            MEMORY (when include_snippets=True). See cogmem_api/prompts/eval/generate.py
            module docstring for details.
    - 'v3_temporal'/'v3': v2 plus one compact temporal-anchor rule (S35-T8B).
    - 'v3_temporal_list'/'v3-list': v3_temporal plus one compact list
            completeness guard (S35-T8E).
    - 'v4_evidence_guard'/'v4': T8E plus query-relevant snippets, strict causal
            negative-control guard, and explicit-duration handling (S35-T8G).
    """
    variant = os.environ.get("COGMEM_API_GENERATE_PROMPT_VARIANT", "legacy").strip().lower()
    if variant in {"v4", "v4_evidence_guard", "v4-evidence-guard", "evidence_guard", "evidence-guard"}:
        builder = _bgp_v4_evidence_guard
    elif variant in {"v3_temporal_list", "v3-temporal-list", "v3_list", "v3-list"}:
        builder = _bgp_v3_temporal_list
    elif variant in {"v3", "v3_temporal", "v3-temporal"}:
        builder = _bgp_v3_temporal
    elif variant == "v2":
        builder = _bgp_v2
    else:
        builder = _bgp_legacy
    return builder(query, evidence, question_date=question_date, session_date_map=session_date_map, include_snippets=include_snippets)


def build_judge_system_prompt(category: str | None) -> str:
    return _bj(category)


def parse_judge_response(raw: str) -> dict:
    return _pjr(raw)
