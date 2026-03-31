"""Prompt builders for CogMem lazy reflect synthesis."""

from __future__ import annotations

from typing import Any

from .models import ReflectEvidence

SYSTEM_PROMPT = (
    "You are CogMem reflect synthesis. "
    "Answer strictly from retrieved evidence. "
    "Prefer raw_snippet details when available and avoid adding unsupported claims."
)


def _truncate(text: str, limit: int) -> str:
    text = text.strip()
    if len(text) <= limit:
        return text
    return text[: max(0, limit - 3)].rstrip() + "..."


def build_lazy_synthesis_prompt(
    question: str,
    evidences: list[ReflectEvidence],
    bank_profile: dict[str, Any] | None = None,
    max_snippet_chars: int = 280,
) -> str:
    """Build a synthesis prompt from retrieved evidence only (lazy, post-retrieval)."""
    profile = bank_profile or {}
    bank_name = str(profile.get("name") or "CogMem")
    mission = str(profile.get("mission") or "")

    lines: list[str] = [
        f"Memory Bank: {bank_name}",
        f"Question: {question.strip()}",
    ]
    if mission:
        lines.append(f"Mission: {mission}")

    lines.extend(["", "Retrieved Evidence:"])
    if not evidences:
        lines.append("- (no evidence)")

    for idx, evidence in enumerate(evidences, start=1):
        lines.append(
            f"{idx}. [{evidence.fact_type}] id={evidence.id} source={evidence.source} score={evidence.score:.4f}"
        )
        lines.append(f"   fact: {_truncate(evidence.text, max_snippet_chars)}")
        if evidence.raw_snippet:
            lines.append(f"   raw_snippet: {_truncate(evidence.raw_snippet, max_snippet_chars)}")

    lines.extend(
        [
            "",
            "Instructions:",
            "- Write a concise markdown answer grounded in evidence above.",
            "- If evidence is insufficient, explicitly say what is missing.",
            "- Do not invent names, dates, or events.",
        ]
    )

    return "\n".join(lines)
