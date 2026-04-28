"""Cross-pass deduplication for 2-pass fact extraction.

Dedup rules:
- For 4 personal types (experience/habit/intention/opinion): if same key in both passes,
  keep Pass 2 (more reliable for user content), drop Pass 1.
- For world/action_effect: Pass 2 cannot extract these (filtered at extraction) —
  only Pass 1 contributes.
- Key = (fact_type, normalized_text) where normalized_text is lowercased,
  whitespace-collapsed, first 120 chars.
"""

from __future__ import annotations

import re
from typing import Any


def _normalize_key_text(text: str) -> str:
    """Normalize text for dedup key: lower, collapse whitespace, first 120 chars."""
    normalized = re.sub(r"\s+", " ", text.strip().lower())
    return normalized[:120]


def _make_dedup_key(fact_type: str, fact_text: str) -> tuple[str, str]:
    return (fact_type, _normalize_key_text(fact_text))


def dedup_facts(
    facts_p1: list[Any],
    facts_p2: list[Any],
    fuzzy_match: bool = False,
) -> list[Any]:
    """Dedup Pass 1 and Pass 2 facts, preferring Pass 2 for personal types.

    Args:
        facts_p1: List of ExtractedFact from Pass 1 (all 6 types).
        facts_p2: List of ExtractedFact from Pass 2 (only 4 personal types).
        fuzzy_match: If True, use rapidfuzz token_set_ratio >= 90 on text field.
                     If False (default), only use exact key match.

    Returns:
        Deduplicated list of ExtractedFact objects.
    """
    PERSONAL_TYPES: frozenset[str] = frozenset({"experience", "habit", "intention", "opinion"})

    p2_keys: set[tuple[str, str]] = set()
    for fact in facts_p2:
        key = _make_dedup_key(fact.fact_type, fact.fact_text)
        p2_keys.add(key)

    result: list[Any] = []

    for fact in facts_p1:
        key = _make_dedup_key(fact.fact_type, fact.fact_text)
        if fact.fact_type in PERSONAL_TYPES and key in p2_keys:
            continue
        result.append(fact)

    result.extend(facts_p2)

    if fuzzy_match:
        try:
            from rapidfuzz import fuzz as _fuzz
        except ImportError:
            return result

        to_remove: set[int] = set()
        texts_seen: list[tuple[str, str, int]] = []
        for i, fact in enumerate(result):
            key_text = _normalize_key_text(fact.fact_text)
            for j, (ptype, ptext, idx) in enumerate(texts_seen):
                if fact.fact_type != ptype:
                    continue
                ratio = _fuzz.token_set_ratio(key_text, ptext)
                if ratio >= 90:
                    to_remove.add(idx)
                    break
            texts_seen.append((fact.fact_type, key_text, i))

        result = [f for i, f in enumerate(result) if i not in to_remove]

    return result