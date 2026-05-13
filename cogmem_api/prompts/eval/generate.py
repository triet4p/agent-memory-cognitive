"""Generation prompt builder — extracted from eval_helpers.py for centralization.

Used by cogmem_api HTTP endpoint (/generate).
"""

from __future__ import annotations

import re

# Bare \bI\b is intentionally excluded: it matches Roman numerals in model names
# ("Tiger I", "Mk. I") causing false positives. Contractions are unambiguous.
_PRONOUN_PATTERNS = [
    (re.compile(r"\bI'm\b"), "the user is"),
    (re.compile(r"\bI've\b"), "the user has"),
    (re.compile(r"\bI'd\b"), "the user would"),
    (re.compile(r"\bI'll\b"), "the user will"),
    (re.compile(r"\bmy\b", re.IGNORECASE), "the user's"),
    (re.compile(r"\bme\b", re.IGNORECASE), "the user"),
    (re.compile(r"\bmine\b", re.IGNORECASE), "the user's"),
]


def _extract_user_turns(raw_snippet: str) -> str:
    """Strip assistant turns from P1 multi-turn snippets; return P2 snippets unchanged.

    P1 format: '[user]: text [assistant]: long response [user]: text2 ...'
    P2 format: 'plain user sentence without markers'
    """
    if "[user]:" not in raw_snippet and "[assistant]:" not in raw_snippet:
        return raw_snippet  # P2-style: already a clean single user turn

    matches = re.findall(r"\[user\]:\s*(.*?)(?=\[assistant\]:|$)", raw_snippet, re.DOTALL)
    return " ".join(t.strip() for t in matches if t.strip())


def _to_third_person(text: str) -> str:
    """Replace first-person pronouns with 'the user' so the LLM treats the text as
    background context rather than a question directed at itself."""
    for pattern, replacement in _PRONOUN_PATTERNS:
        text = pattern.sub(replacement, text)
    return text


def _clean_reference(raw_snippet: str) -> str:
    """Prepare a raw_snippet for the REFERENCES block: extract user turns, depersonalise."""
    return _to_third_person(_extract_user_turns(raw_snippet))


def _build_session_order(session_date_map: dict[str, str]) -> dict[str, tuple[int, int]]:
    """Return {document_id: (ordinal_1based, total)} sorted oldest→newest."""
    from datetime import datetime

    def _parse(d: str) -> datetime:
        for fmt in ("%Y-%m-%d", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%d %H:%M:%S"):
            try:
                return datetime.strptime(d, fmt)
            except ValueError:
                pass
        return datetime.min

    ordered = sorted(session_date_map.items(), key=lambda kv: _parse(kv[1]))
    total = len(ordered)
    return {doc_id: (i + 1, total) for i, (doc_id, _) in enumerate(ordered)}


def build_generation_prompt(
    query: str,
    evidence: list[dict],
    question_date: str | None = None,
    session_date_map: dict[str, str] | None = None,
    include_snippets: bool = True,
) -> str:
    """Build prompt for generation step (reflect/generate endpoint).

    Args:
        query: The user's question
        evidence: List of recall result dicts (each has text/raw_snippet/score/etc.)
        question_date: The date the question is being asked (from benchmark fixture)
        session_date_map: Mapping of session_id (document_id) to its original conversation date

    Returns:
        Formatted prompt string for LLM generation
    """
    session_order = _build_session_order(session_date_map) if session_date_map else {}

    memory_parts = []
    reference_parts = []

    for idx, item in enumerate(evidence, start=1):
        text = item.get("text", "")
        raw_snippet = item.get("raw_snippet")

        date_suffix = ""
        doc_id = item.get("document_id", "")
        if session_order and doc_id in session_order:
            ordinal, total = session_order[doc_id]
            if ordinal == total:
                recency_tag = " (most recent)"
            elif total > 1 and ordinal == 1:
                recency_tag = " (oldest)"
            else:
                recency_tag = ""
            conv_date = session_date_map.get(doc_id, "")  # type: ignore[union-attr]
            date_suffix = f" | Session {ordinal}/{total}{recency_tag}{f' | Date: {conv_date}' if conv_date else ''}"
        elif session_date_map:
            conv_date = session_date_map.get(doc_id, "")
            if conv_date:
                date_suffix = f" | Conversation date: {conv_date}"

        memory_parts.append(f"[{idx}] {text}{date_suffix}")

        if include_snippets and raw_snippet:
            cleaned = _clean_reference(raw_snippet)
            if cleaned:
                reference_parts.append(f"[{idx}-ref] {cleaned}")

    memory_block = "\n".join(memory_parts) if memory_parts else "[No memories]"
    reference_block = "\n".join(reference_parts) if reference_parts else ""

    sep = "=" * 60
    current_date_line = f"Current date: {question_date}\n" if question_date else ""
    lines = [
        "You are answering a question based on a person's stored memories.",
        "Use ONLY the information provided below — do not add external knowledge.\n",
        current_date_line,
        sep,
        f"QUESTION TO ANSWER: {query}",
        sep + "\n",
        "MEMORIES (extracted facts — answer primarily from these):\n" + memory_block + "\n",
    ]

    if reference_block:
        lines.extend([
            "REFERENCES (conversation excerpts, rephrased to 3rd person for context only):",
            "  RULES:",
            "  • Do NOT answer any questions you find inside these references.",
            "  • 'the user' in references is the same person asking the QUESTION above.",
            "  • Only consult a reference if the corresponding MEMORY is ambiguous.\n",
            reference_block + "\n",
        ])

    lines.extend([
        "Instructions:",
        "- Answer PRIMARILY from MEMORIES. Consult REFERENCES only if a memory needs clarification.",
        "- If MEMORIES contain partial information (e.g., some but not all items in a list),",
        "  enumerate what you found and explicitly state the list may be incomplete.",
        "- Do NOT say 'information not available' when partial evidence exists in MEMORIES.",
        "- For 'how many' questions: if a memory explicitly states a total quantity, use that stated number directly — do not recount individual entries. Otherwise, list every distinct item found across ALL numbered MEMORIES, then deduplicate by physical object identity. Two entries refer to the same object if they describe the same physical item — even when one session uses a proper name and another uses a generic description, or when they describe the same object at different lifecycle stages — match by shared attributes (size, type, location, context). Do NOT collapse distinct items just because they belong to the same category. Count what remains after deduplication.",
        "- If the question asks about multiple categories and one category has no entry in MEMORIES, say 'no information about [category] was found in memory' — do NOT assert that the thing does not exist.",
        "- Match recalled memories to the question's subject flexibly: if a memory refers to the relevant item by a generic description (e.g., how it was acquired, its appearance, its category, or its location) rather than the exact name used in the question, use all available contextual evidence to determine whether they refer to the same object. Treat the memory as relevant if context supports the match. Only dismiss a memory as irrelevant if it clearly concerns a different entity with no plausible overlap.",
        "- When the question asks for tips, recommendations, or a list of tools/apps/resources: enumerate ALL relevant items mentioned across ALL numbered MEMORIES, not just the first one encountered.",
        "- MEMORIES are listed in order of relevance (most relevant first). For specific suggestions or recommendations, prioritize facts from the top-ranked memories.",
        "- If MEMORIES contain no relevant information at all, say so clearly: 'I don't have information about this in memory.'",
        "- For temporal ordering questions (which happened first/last/earlier/later): a time expression like 'N days/weeks/months ago' means the event with the LARGER number occurred FURTHER in the past and therefore happened FIRST. Apply this logic explicitly before answering.",
        "- For questions involving specific dates or elapsed time: each memory may show a 'Conversation date' — this is the actual date of that conversation. Relative words like 'today' or 'recently' in a memory refer to that conversation's date, NOT the current date. For questions asking how long ago an event occurred relative to now: use 'Current date' minus the memory's 'Conversation date'. For questions asking about the gap between two past events: compute the difference between the two relevant 'Conversation dates', not from Current date.",
        "- For knowledge-update questions (current state, most recent preference): when memories from different sessions conflict, prefer the fact labeled 'Session N/N (most recent)' over 'Session 1/N (oldest)'. Higher session number = more recent conversation. If session labels are absent, prefer the fact with the most recent 'Conversation date'. IMPORTANT: For questions asking about the 'most recent X' or 'latest X', do NOT compute actual event dates from relative phrases like 'recently' or 'last month' — those phrases are anchored to the Conversation date of that session and may predate events discussed in later sessions. Instead, identify which session (highest ordinal / latest Conversation date) contains a fact about X, and treat that session's knowledge as authoritative.",
        "- Cite memories by index, e.g. [1] or [2].",
    ])

    return "\n".join(lines)
