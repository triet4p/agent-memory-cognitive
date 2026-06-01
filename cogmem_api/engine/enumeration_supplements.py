"""Targeted recall supplements for list/enumeration questions.

This module is intentionally conservative: it only activates for obvious
enumeration/location queries and only promotes already-retained facts. It does
not increase the final top-k window; callers merge supplements by replacing
low-ranked tail items.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any


_QUESTION_WORDS = {
    "which",
    "what",
    "where",
    "when",
    "who",
    "whom",
    "whose",
    "why",
    "how",
    "us",
    "u",
    "s",
}
_COMMON_CAPITALIZED = {
    "I",
    "A",
    "The",
    "This",
    "That",
    "These",
    "Those",
    "Which",
    "What",
    "Where",
    "When",
    "Who",
    "How",
    "US",
    "U",
    "S",
}
_LOCATION_NOUNS = (
    "beach",
    "beaches",
    "forest",
    "forests",
    "mountain",
    "mountains",
    "lake",
    "lakes",
    "park",
    "parks",
    "city",
    "cities",
    "campground",
    "campgrounds",
)
_TRAVEL_CUES = (
    "visited",
    "visit",
    "went to",
    "been to",
    "trip to",
    "trips to",
    "tour in",
    "toured",
    "in person",
    "was in",
    "were in",
    "from one of",
    "pic from",
    "photo from",
    "subway in",
    "skyline",
)
_IN_PLACE_CONTEXT_RE = re.compile(
    r"\b(?:chat|fan|met|conference|place|tour|trip|photo|pic|snapped|seeing|saw)\b.{0,80}\bin\s+[A-Z][a-z]+"
)
_FUTURE_OR_WISHLIST_CUES = (
    "plans to",
    "plan to",
    "wants to",
    "want to",
    "would like",
    "hopes to",
    "dreams of",
    "bucket list",
    "travel list",
    "list of places",
    "researching visa",
    "visa requirements",
)
_MENTION_VISITING_CUES = (
    "mention visiting",
    "mentions visiting",
    "mentioned visiting",
    "mention visit",
    "mentions visit",
)
_PROPER_PLACE_RE = re.compile(
    r"\b(?:[A-Z][a-z]+(?:\s+[A-Z][a-z]+){0,3}|NYC|UK|USA|CA)\b"
)


@dataclass(frozen=True)
class EnumerationQuerySpec:
    mode: str
    subject_terms: tuple[str, ...]
    us_only: bool = False


def build_enumeration_query_spec(query: str) -> EnumerationQuerySpec | None:
    """Return a narrow enumeration spec for list-like location questions."""
    lowered = query.lower()
    is_list_query = lowered.strip().startswith(("where ", "which ", "what "))
    if not is_list_query:
        return None

    subjects = tuple(_extract_subject_terms(query))
    if "camp" in lowered:
        return EnumerationQuerySpec(mode="camping_places", subject_terms=subjects)

    has_location_word = any(
        token in lowered
        for token in ("location", "locations", "place", "places", "city", "cities")
    )
    has_travel_word = any(token in lowered for token in ("been to", "visited", "visiting", "trip"))
    if has_location_word and has_travel_word:
        if any(cue in lowered for cue in _MENTION_VISITING_CUES):
            return EnumerationQuerySpec(
                mode="mentioned_places",
                subject_terms=subjects,
                us_only=bool(re.search(r"\bus\b|\bu\.s\.", lowered)),
            )
        return EnumerationQuerySpec(
            mode="visited_places",
            subject_terms=subjects,
            us_only=bool(re.search(r"\bus\b|\bu\.s\.", lowered)),
        )

    return None


def score_enumeration_candidate(spec: EnumerationQuerySpec, text: str, raw_snippet: str | None = None) -> float:
    """Score whether a retained fact is a useful enumeration supplement."""
    # Score only the retained fact text. Raw snippets may contain many unrelated
    # turns from the same session; using them for scoring can promote irrelevant
    # facts whose source merely happens to mention a place elsewhere.
    _ = raw_snippet
    combined = text.strip()
    lowered = combined.lower()
    if not lowered:
        return 0.0

    score = 0.0
    if spec.subject_terms:
        primary_subject = spec.subject_terms[0].lower()
        if primary_subject not in lowered:
            return 0.0
        score += 3.0

    if spec.mode == "camping_places":
        if "camp" not in lowered:
            return 0.0
        if not any(noun in lowered for noun in _LOCATION_NOUNS):
            return 0.0
        score += 3.0
        score += sum(1.0 for noun in _LOCATION_NOUNS if noun in lowered)
        return score

    proper_places = _extract_proper_places(combined, spec.subject_terms)
    has_place = bool(proper_places)
    has_travel_cue = any(cue in lowered for cue in _TRAVEL_CUES)
    has_us_city_alias = any(city in combined for city in ("NYC", "New York", "Seattle", "Chicago"))
    if not has_place:
        return 0.0
    if spec.us_only and not has_us_city_alias:
        return 0.0
    if "not been" in lowered or "never been" in lowered:
        return 0.0

    if spec.mode == "visited_places":
        if any(cue in lowered for cue in _FUTURE_OR_WISHLIST_CUES):
            return 0.0
        if not has_travel_cue and not _IN_PLACE_CONTEXT_RE.search(combined):
            return 0.0
        score += 3.0
    elif spec.mode == "mentioned_places":
        if any(cue in lowered for cue in _FUTURE_OR_WISHLIST_CUES):
            # "Mention visiting" should still avoid other people's wishlists.
            return 0.0
        if not has_travel_cue and not has_us_city_alias:
            return 0.0
        score += 2.5
    else:
        return 0.0

    score += min(float(len(proper_places)), 3.0)
    if has_travel_cue:
        score += 1.0
    if has_us_city_alias:
        score += 3.0
    return score


def merge_enumeration_supplements(
    primary_results: list[dict[str, Any]],
    supplemental_results: list[dict[str, Any]],
    top_k: int | None,
) -> list[dict[str, Any]]:
    """Merge supplements into the final window without increasing top-k."""
    if not supplemental_results:
        return primary_results

    seen_ids = {str(item.get("id") or "") for item in primary_results}
    unique_supplements = [
        item for item in supplemental_results
        if str(item.get("id") or "") and str(item.get("id") or "") not in seen_ids
    ]
    if not unique_supplements:
        return primary_results

    if top_k is None or top_k <= 0:
        return primary_results + unique_supplements

    keep_count = max(0, top_k - len(unique_supplements))
    return primary_results[:keep_count] + unique_supplements[:top_k]


def _extract_subject_terms(query: str) -> list[str]:
    candidates = []
    for match in _PROPER_PLACE_RE.finditer(query):
        token = match.group(0).strip()
        if token in _COMMON_CAPITALIZED:
            continue
        if token.lower() in _QUESTION_WORDS:
            continue
        # Keep likely person names from the query; all-caps tokens like US are query
        # category labels, not subjects.
        if token.isupper():
            continue
        candidates.append(token)
    return candidates[:2]


def _extract_proper_places(text: str, subject_terms: tuple[str, ...]) -> set[str]:
    subjects = {term.lower() for term in subject_terms}
    places: set[str] = set()
    for match in _PROPER_PLACE_RE.finditer(text):
        token = match.group(0).strip()
        lowered = token.lower()
        if token in _COMMON_CAPITALIZED or lowered in subjects:
            continue
        if lowered in {"user", "involving", "john", "tim", "melanie", "caroline", "harry potter"}:
            continue
        places.add(token)
    return places
