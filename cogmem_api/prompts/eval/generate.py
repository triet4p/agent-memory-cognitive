"""Generation prompt builder — extracted from eval_helpers.py for centralization.

Used by cogmem_api HTTP endpoint (/generate).
"""

from __future__ import annotations


def build_generation_prompt(query: str, evidence: list[dict]) -> str:
    """Build prompt for generation step (reflect/generate endpoint).

    Args:
        query: The user's question
        evidence: List of recall result dicts (each has text/raw_snippet/score/etc.)

    Returns:
        Formatted prompt string for LLM generation
    """
    evidence_parts = []
    for idx, item in enumerate(evidence, start=1):
        snippet = item.get("raw_snippet") or item.get("text", "")
        evidence_parts.append(f"[{idx}] {snippet}")

    evidence_block = "\n".join(evidence_parts) if evidence_parts else "[No evidence]"

    return (
        "Answer the question using ONLY the recall evidence below.\n"
        "- Cite evidence by index, e.g. [1] or [2].\n"
        "- If the evidence does not contain the answer, say explicitly that the information is not available.\n"
        "- Do not fabricate facts not present in the evidence.\n"
        "- Match the language of the question.\n\n"
        f"Question: {query}\n\n"
        f"Recall Evidence:\n{evidence_block}\n"
    )