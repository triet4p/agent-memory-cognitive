"""Centralized prompt library for CogMem.

Modules:
- cogmem_api.prompts.retain.pass1: Pass 1 extraction prompt
- cogmem_api.prompts.retain.pass2: Pass 2 persona-focused prompt
- cogmem_api.prompts.retain.shared: Shared utilities for retain prompts
- cogmem_api.prompts.eval.generate: Generation prompt builder
- cogmem_api.prompts.eval.judge: Judge prompt builder

Public API:
- build_pass1_prompt(config) -> (prompt, mode)
- build_pass2_prompt() -> prompt_str
- PASS2_ALLOWED_FACT_TYPES
- build_generation_prompt(query, evidence) -> str
- build_judge_system_prompt(category) -> str
"""

from __future__ import annotations

from cogmem_api.prompts.retain import build_pass1_prompt, build_pass2_prompt, PASS2_ALLOWED_FACT_TYPES
from cogmem_api.prompts.eval import build_generation_prompt, build_judge_system_prompt

__all__ = [
    "build_pass1_prompt",
    "build_pass2_prompt",
    "PASS2_ALLOWED_FACT_TYPES",
    "build_generation_prompt",
    "build_judge_system_prompt",
]