"""Minimal lazy reflect synthesis for CogMem Sprint 4 Task 4.1."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from .models import ReflectSynthesisResult
from .prompts import build_lazy_synthesis_prompt
from .tools import prepare_lazy_evidence


def _default_markdown_answer(question: str, evidence_lines: list[str]) -> str:
    if not evidence_lines:
        return (
            "## Memory-Grounded Answer\n\n"
            "I do not have enough retrieved memories to answer this question confidently."
        )

    content = "\n".join(f"- {line}" for line in evidence_lines)
    return (
        "## Memory-Grounded Answer\n\n"
        f"Question: {question.strip()}\n\n"
        "### Evidence Summary\n\n"
        f"{content}\n\n"
        "Answer is synthesized only from retrieved CogMem evidence."
    )


def synthesize_lazy_reflect(
    question: str,
    retrieved_items: list[Any],
    llm_generate: Callable[[str], str] | None = None,
    bank_profile: dict[str, Any] | None = None,
    max_evidence: int = 8,
    include_prompt: bool = False,
) -> ReflectSynthesisResult:
    """Synthesize an answer lazily from post-retrieval evidence.

    The function does not trigger proactive consolidation and does not depend on
    observation pipelines. It consumes retrieved memory candidates and optionally
    delegates final answer wording to an external generator.
    """
    evidences = prepare_lazy_evidence(retrieved_items, max_items=max_evidence)
    prompt = build_lazy_synthesis_prompt(question=question, evidences=evidences, bank_profile=bank_profile)

    evidence_lines: list[str] = []
    for evidence in evidences:
        line = f"[{evidence.fact_type}] {evidence.text}"
        if evidence.raw_snippet:
            line += f" (raw: {evidence.raw_snippet})"
        evidence_lines.append(line)

    if llm_generate is not None:
        generated = llm_generate(prompt)
        answer = (generated or "").strip() or _default_markdown_answer(question, evidence_lines)
    else:
        answer = _default_markdown_answer(question, evidence_lines)

    networks: list[str] = []
    for evidence in evidences:
        if evidence.fact_type not in networks:
            networks.append(evidence.fact_type)

    return ReflectSynthesisResult(
        answer=answer,
        used_memory_ids=[e.id for e in evidences],
        networks_covered=networks,
        evidence_count=len(evidences),
        prompt=prompt if include_prompt else None,
    )
