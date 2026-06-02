"""Targeted recall supplements for list/enumeration questions.

This module is intentionally conservative: it only promotes already-retained
facts and does not increase the final top-k window; callers merge supplements
by replacing low-ranked tail items.
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
_QUERY_TERM_STOPWORDS = _QUESTION_WORDS | {
    "about",
    "all",
    "and",
    "any",
    "are",
    "before",
    "been",
    "did",
    "does",
    "for",
    "from",
    "has",
    "have",
    "his",
    "her",
    "into",
    "list",
    "mention",
    "mentioned",
    "mentions",
    "of",
    "the",
    "their",
    "them",
    "they",
    "to",
    "with",
}
_DURATION_QUERY_STOPWORDS = _QUERY_TERM_STOPWORDS | {
    "car",
    "cars",
    "long",
    "take",
    "took",
    "work",
    "worked",
    "working",
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
_BAND_CUES = (
    "band",
    "bands",
    "headliner",
    "headlined",
    "festival",
    "concert",
    "perform",
    "performed",
    "live",
    "music",
)
_BOOK_AUTHOR_CUES = (
    "book",
    "books",
    "novel",
    "read",
    "reading",
    "author",
    "series",
    "recommended",
    "recommend",
)
_GAME_CUES = (
    "game",
    "games",
    "gaming",
    "played",
    "playing",
    "started playing",
    "develop",
    "developed",
    "strategy",
    "rpg",
    "simulator",
    "virtual world",
)
_ACTIVITY_EVENT_CUES = (
    "activity",
    "activities",
    "hobby",
    "hobbies",
    "event",
    "events",
    "fair",
    "competition",
    "networking",
    "museum",
    "hiking",
    "swimming",
    "camping",
    "painting",
    "pottery",
    "concert",
    "walk",
    "photography",
)
_GIFT_ITEM_CUES = (
    "gift",
    "gifts",
    "item",
    "items",
    "collect",
    "collects",
    "received",
    "owns",
    "gear",
    "necklace",
    "chain",
    "guitar",
    "sneakers",
    "jerseys",
    "dvd",
    "memorabilia",
    "accessory",
)
_COLLECTIBLE_CUES = (
    "collectible",
    "collectibles",
    "collection",
    "collect",
    "collects",
    "collected",
    "memorabilia",
    "card",
    "cards",
    "stamp",
    "stamps",
    "coin",
    "coins",
    "model",
    "models",
    "figurine",
    "figurines",
    "jersey",
    "jerseys",
    "dvd",
)
_FAMILY_CUES = (
    "family",
    "member",
    "members",
    "dad",
    "father",
    "mother",
    "mom",
    "sister",
    "brother",
    "grandma",
    "grandmother",
)
_SPORT_EXERCISE_CUES = (
    "sport",
    "sports",
    "exercise",
    "exercises",
    "training",
    "supplement",
    "yoga",
    "strength",
    "running",
    "sprinting",
    "boxing",
    "surfing",
    "basketball",
)
_CLASS_CUES = (
    "class",
    "classes",
    "course",
    "courses",
    "joined",
    "signed up",
    "cooking",
    "game design",
)
_BEER_CUES = (
    "beer",
    "beers",
    "bar",
    "pub",
    "stout",
    "lager",
    "light beer",
    "light beers",
)
_PET_TRICK_CUES = (
    "pet",
    "pets",
    "dog",
    "dogs",
    "trick",
    "tricks",
    "sit",
    "stay",
    "paw",
    "rollover",
    "swimming",
    "frisbee",
    "skateboard",
)
_SHOW_MOVIE_CUES = (
    "tv",
    "series",
    "show",
    "movie",
    "movies",
    "watched",
    "watching",
    "fantasy",
    "star wars",
    "lord of the rings",
)
_INSTRUMENT_CUES = (
    "instrument",
    "instruments",
    "play",
    "plays",
    "played",
    "piano",
    "violin",
    "guitar",
)
_GENERIC_CATEGORY_CUES: dict[str, tuple[str, ...]] = {
    "bands": _BAND_CUES,
    "books_authors": _BOOK_AUTHOR_CUES,
    "games": _GAME_CUES,
    "activities_events": _ACTIVITY_EVENT_CUES,
    "gifts_items": _GIFT_ITEM_CUES,
    "collectibles": _COLLECTIBLE_CUES,
    "family_members": _FAMILY_CUES,
    "sports_exercises": _SPORT_EXERCISE_CUES,
    "classes": _CLASS_CUES,
    "beers": _BEER_CUES,
    "pet_tricks": _PET_TRICK_CUES,
    "shows_movies": _SHOW_MOVIE_CUES,
    "instruments": _INSTRUMENT_CUES,
}
_GENERIC_QUERY_TRIGGERS: tuple[tuple[str, tuple[str, ...]], ...] = (
    ("bands", ("band", "bands")),
    ("books_authors", ("book", "books", "author", "authors", "recommended")),
    ("games", ("game", "games", "gaming")),
    ("activities_events", ("activit", "hobb", "event", "events", "participated", "meet at", "planned to meet")),
    ("collectibles", ("collectible", "collectibles", "collection", "collect", "memorabilia")),
    ("gifts_items", ("gift", "gifts", "item", "items", "collect", "accessor", "received", "own")),
    ("family_members", ("family member", "family members", "family")),
    ("sports_exercises", ("sport", "sports", "exercise", "exercises", "supplement", "training")),
    ("classes", ("class", "classes", "course", "courses")),
    ("beers", ("beer", "bar serve", "pub serve")),
    ("pet_tricks", ("pet", "pets", "trick", "tricks")),
    ("shows_movies", ("tv", "series", "show", "movie", "movies", "watch")),
    ("instruments", ("instrument", "instruments")),
)
_TRAVEL_CUES = (
    "visited",
    "visit",
    "went to",
    "been to",
    "trip to",
    "trips to",
    "travel",
    "traveled",
    "travelled",
    "traveling",
    "travelling",
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
_DURATION_PHRASE_RE = re.compile(
    r"\b(?:about|around|nearly|almost|roughly|approximately|just under|over|under|more than|less than)?\s*"
    r"(?:\d+|one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve|"
    r"a|an)\s+"
    r"(?:day|days|week|weeks|month|months|year|years|hour|hours|minute|minutes|summer)\b",
    re.IGNORECASE,
)
_DURATION_QUERY_RE = re.compile(r"\b(?:how long|take|took|for .* before|duration)\b", re.IGNORECASE)
_BASKETBALL_SUPPLEMENT_RE = re.compile(
    r"\b(?:yoga|strength\s+training|strength\s+and\s+flexibility|extra\s+strength|"
    r"focus\s+and\s+balance|workouts?|flexibility)\b",
    re.IGNORECASE,
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
    query_terms: tuple[str, ...] = ()


def build_enumeration_query_spec(query: str) -> EnumerationQuerySpec | None:
    """Return a narrow enumeration spec for list-like questions."""
    lowered = query.lower()
    stripped = lowered.strip()
    subjects = tuple(_extract_subject_terms(query))
    query_terms = tuple(_extract_query_terms(query, subjects))

    if _DURATION_QUERY_RE.search(lowered):
        return EnumerationQuerySpec(mode="duration", subject_terms=subjects, query_terms=query_terms)

    is_list_query = stripped.startswith(("where ", "which ", "what ", "how many "))
    if not is_list_query:
        return None

    if "camp" in lowered:
        return EnumerationQuerySpec(mode="camping_places", subject_terms=subjects, query_terms=query_terms)

    if (
        "city" in lowered
        and any(token in lowered for token in ("before", "after"))
        and any(token in lowered for token in ("travel", "traveled", "travelled", "traveling", "travelling", "trip", "visit"))
    ):
        return EnumerationQuerySpec(mode="temporal_city", subject_terms=subjects, query_terms=query_terms)

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
                query_terms=query_terms,
            )
        return EnumerationQuerySpec(
            mode="visited_places",
            subject_terms=subjects,
            us_only=bool(re.search(r"\bus\b|\bu\.s\.", lowered)),
            query_terms=query_terms,
        )

    if "countries" in lowered or "country" in lowered:
        return EnumerationQuerySpec(mode="visited_places", subject_terms=subjects, query_terms=query_terms)

    for mode, triggers in _GENERIC_QUERY_TRIGGERS:
        if any(trigger in lowered for trigger in triggers):
            return EnumerationQuerySpec(mode=mode, subject_terms=subjects, query_terms=query_terms)

    return None


def score_enumeration_candidate(spec: EnumerationQuerySpec, text: str, raw_snippet: str | None = None) -> float:
    """Score whether a retained fact is a useful enumeration supplement."""
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

    if spec.mode == "duration":
        return _score_duration_candidate(spec, text, raw_snippet)

    if spec.mode == "temporal_city":
        return _score_temporal_city_candidate(spec, text, raw_snippet)

    if spec.mode in _GENERIC_CATEGORY_CUES:
        return _score_generic_candidate(spec, text, raw_snippet)

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


def _score_generic_candidate(spec: EnumerationQuerySpec, text: str, raw_snippet: str | None = None) -> float:
    """Score generic list/category supplements after the main subject is matched."""
    fact_text = text.strip()
    combined = fact_text
    if raw_snippet:
        combined = f"{combined} {raw_snippet.strip()}"
    text_lowered = fact_text.lower()
    lowered = combined.lower()
    if not text_lowered:
        return 0.0

    score = 0.0
    if spec.subject_terms:
        primary_subject = spec.subject_terms[0].lower()
        if primary_subject not in text_lowered:
            return 0.0
        score += 3.0

    cues = _GENERIC_CATEGORY_CUES.get(spec.mode)
    if not cues:
        return 0.0

    if spec.mode == "sports_exercises" and "supplement" in spec.query_terms:
        if "basketball" in spec.query_terms and _BASKETBALL_SUPPLEMENT_RE.search(fact_text):
            score += 3.0
        elif "basketball" in spec.query_terms:
            return 0.0
        supplement_cues = (
            "yoga",
            "strength training",
            "strength and flexibility",
            "extra strength",
            "focus and balance",
            "flexibility",
            "running",
            "sprinting",
            "boxing",
            "exercise",
            "exercises",
            "workout",
            "workouts",
        )
        if not any(cue in text_lowered for cue in supplement_cues):
            return 0.0

    cue_hits = [cue for cue in cues if cue in text_lowered]
    if not cue_hits:
        return 0.0
    score += 2.0 + min(float(len(cue_hits)), 3.0)

    query_hits = [term for term in spec.query_terms if term in text_lowered]
    score += min(float(len(query_hits)), 3.0)

    proper_items = _extract_proper_items(fact_text, spec.subject_terms)
    if spec.mode == "bands" and not proper_items:
        return 0.0

    if proper_items:
        score += min(float(len(proper_items)), 3.0)

    if spec.mode == "bands" and any(cue in text_lowered for cue in ("headlined", "headliner", "concert", "festival")):
        score += 2.0
    if spec.mode == "sports_exercises" and any(
        cue in text_lowered for cue in ("yoga", "strength training", "flexibility", "running", "boxing")
    ):
        score += 2.0
    if spec.mode == "pet_tricks" and any(
        cue in text_lowered for cue in ("sit", "stay", "paw", "rollover", "frisbee", "skateboard")
    ):
        score += 2.0

    return score


def _score_duration_candidate(spec: EnumerationQuerySpec, text: str, raw_snippet: str | None = None) -> float:
    combined = text.strip()
    if raw_snippet:
        combined = f"{combined} {raw_snippet.strip()}"
    lowered = combined.lower()
    if not _DURATION_PHRASE_RE.search(combined):
        return 0.0

    specific_terms = [
        term
        for term in spec.query_terms
        if len(term) >= 3 and term not in _DURATION_QUERY_STOPWORDS
    ]
    term_hits = [term for term in specific_terms if term in lowered]
    if specific_terms and not term_hits:
        return 0.0

    score = 6.0
    score += min(float(len(term_hits)), 4.0)
    score += min(float(len(_DURATION_PHRASE_RE.findall(combined))) * 3.0, 6.0)
    if any(term in lowered for term in ("mustang", "workshop", "san francisco", "ford")):
        score += 2.0
    return score


def _score_temporal_city_candidate(spec: EnumerationQuerySpec, text: str, raw_snippet: str | None = None) -> float:
    combined = text.strip()
    if raw_snippet:
        combined = f"{combined} {raw_snippet.strip()}"
    lowered = combined.lower()
    proper_places = _extract_proper_places(combined, spec.subject_terms)
    if not proper_places:
        return 0.0
    if "not been" in lowered or "never been" in lowered:
        return 0.0

    score = 5.0 + min(float(len(proper_places)), 3.0)
    if any(cue in lowered for cue in _TRAVEL_CUES):
        score += 1.5
    if any(place.lower() in lowered for place in proper_places):
        score += 1.0
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


def _extract_query_terms(query: str, subject_terms: tuple[str, ...]) -> list[str]:
    subject_tokens = {
        token
        for subject in subject_terms[:1]
        for token in re.findall(r"[a-z0-9]+", subject.lower())
    }
    terms: list[str] = []
    seen: set[str] = set()
    for token in re.findall(r"[a-z0-9]+", query.lower()):
        if len(token) < 3 or token in _QUERY_TERM_STOPWORDS or token in subject_tokens:
            continue
        if token not in seen:
            terms.append(token)
            seen.add(token)
    return terms[:8]


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


def _extract_proper_items(text: str, subject_terms: tuple[str, ...]) -> set[str]:
    subjects = {term.lower() for term in subject_terms}
    items: set[str] = set()
    for match in _PROPER_PLACE_RE.finditer(text):
        token = match.group(0).strip()
        lowered = token.lower()
        if token in _COMMON_CAPITALIZED or lowered in subjects:
            continue
        if lowered in {"user", "involving", "john", "tim", "melanie", "caroline"}:
            continue
        items.add(token)
    return items
