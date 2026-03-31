"""Reflect module for CogMem lazy synthesis."""

from .agent import synthesize_lazy_reflect
from .models import ReflectEvidence, ReflectSynthesisResult
from .prompts import SYSTEM_PROMPT, build_lazy_synthesis_prompt
from .tools import group_evidence_by_network, prepare_lazy_evidence, to_reflect_evidence

__all__ = [
    "SYSTEM_PROMPT",
    "ReflectEvidence",
    "ReflectSynthesisResult",
    "build_lazy_synthesis_prompt",
    "group_evidence_by_network",
    "prepare_lazy_evidence",
    "synthesize_lazy_reflect",
    "to_reflect_evidence",
]
