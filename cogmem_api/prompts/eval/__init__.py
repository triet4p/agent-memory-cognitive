"""Prompt library for CogMem eval pipeline (generation + judge)."""

from __future__ import annotations

from cogmem_api.prompts.eval.generate import build_generation_prompt
from cogmem_api.prompts.eval.judge import build_judge_system_prompt

__all__ = ["build_generation_prompt", "build_judge_system_prompt"]