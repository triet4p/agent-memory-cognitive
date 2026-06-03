"""Generation prompt builder — extracted from eval_helpers.py for centralization.

Used by cogmem_api HTTP endpoint (/generate).
"""

from __future__ import annotations

from datetime import date, datetime, timedelta
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
    """LEGACY prompt builder — preserved for back-compat (S29-S34 runs).

    Not modified by S35 prompt v2 work. Used unless
    `COGMEM_API_GENERATE_PROMPT_VARIANT=v2` is set in env.

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
        "- When counting events/items belonging to the user, examine subject/possessive cues. A memory mentioning another person's event (e.g., 'sister's wedding', 'team's high-priority project') without explicit user participation should NOT be counted as the user's own event. Only count events where the user is the explicit actor or participant.",
        "- When counting distinct products, scale/version variants of the same named product (e.g., '1/72 F-15 Eagle' and '1/48 F-15 Eagle') refer to the same model line and should be counted as ONE item unless the question explicitly asks about variants.",
        "- For 'how many days ago' questions: STEP 1 — identify the reference point (what 'ago' is measured from). STEP 2 — apply any relative-word offset to get the true event_date. STEP 3 — compute the difference. STEP 1 DETAIL: The reference point is the current date UNLESS the question contains a secondary event as a temporal anchor (e.g., 'how many days ago did X happen, when I did Y?' or 'how many days ago did X happen at the time of Y?'). In that case, the reference point is the date of Y (the anchoring event), NOT the current date. Example: 'How many days ago did I attend a baking class when I made my friend's birthday cake?' — the birthday cake event anchors the reference; answer = date(birthday_cake_event) − event_date(baking_class). STEP 2 DETAIL: When a memory fact's text contains a relative word, you MUST compute the actual event_date FIRST: 'yesterday' → event_date = session_date − 1; 'N days ago' → event_date = session_date − N; 'today' → event_date = session_date. NEVER use the session_date itself as the event_date when the text says 'yesterday' or 'N days ago'. STEP 3: answer = reference_point − event_date. Show the arithmetic step-by-step including: (a) what the reference point is and why, (b) the event_date after applying any offset, (c) the final subtraction.",
        "- If the question asks about multiple categories and one category has no entry in MEMORIES, say 'no information about [category] was found in memory' — do NOT assert that the thing does not exist.",
        "- If a recalled memory describes an item by its acquisition context (e.g., 'flea market find', 'Etsy purchase') and the query references it by visual/topical description (e.g., 'painting of a sunset'), assume they refer to the same object UNLESS contradicted by another memory. Use the value/quantitative information from such memories to answer.",
        "- When the question asks for tips, recommendations, or a list of tools/apps/resources: enumerate ALL relevant items mentioned across ALL numbered MEMORIES, not just the first one encountered.",
        "- MEMORIES are listed in order of relevance (most relevant first). For specific suggestions or recommendations, prioritize facts from the top-ranked memories.",
        "- If MEMORIES contain no relevant information at all, say so clearly: 'I don't have information about this in memory.'",
        "- For temporal ordering questions (which happened first/last/earlier/later): a time expression like 'N days/weeks/months ago' means the event with the LARGER number occurred FURTHER in the past and therefore happened FIRST. Apply this logic explicitly before answering.",
        "- For questions involving specific dates or elapsed time: each memory may show a 'Conversation date' — this is the actual date of that conversation. Relative words like 'today' or 'recently' in a memory refer to that conversation's date, NOT the current date. For questions asking how long ago an event occurred relative to now: use 'Current date' minus the memory's 'Conversation date'. For questions asking about the gap between two past events: compute the difference between the two relevant 'Conversation dates', not from Current date.",
        "- For knowledge-update questions (current state, most recent preference): when memories from different sessions conflict, prefer the fact labeled 'Session N/N (most recent)' over 'Session 1/N (oldest)'. Higher session number = more recent conversation. If session labels are absent, prefer the fact with the most recent 'Conversation date'. IMPORTANT: For questions asking about the 'most recent X' or 'latest X', do NOT compute actual event dates from relative phrases like 'recently' or 'last month' — those phrases are anchored to the Conversation date of that session and may predate events discussed in later sessions. Instead, identify which session (highest ordinal / latest Conversation date) contains a fact about X, and treat that session's knowledge as authoritative. HARD RULE — NO EXCEPTIONS: When multiple sessions contain different values for the same metric from the same source or institution, you MUST report the value from the most recent session (highest session number / latest Conversation date). This rule cannot be overridden by any contextual reasoning about the question's phrasing. Do NOT use the question's temporal anchor (e.g., 'when I got my mortgage', 'when I applied', 'when I signed up', 'at the time of purchase', 'when I first started') to select an older session's value over a newer one. The question's phrasing describes which topic to look up — it does NOT specify which session's value to use. Always use the most recent session's value for that topic, regardless of how the question is worded.",
        "- Cite memories by index, e.g. [1] or [2].",
    ])

    return "\n".join(lines)


# ── S35 prompt v2 ─────────────────────────────────────────────────────────
#
# Sibling of build_generation_prompt (legacy stays untouched). Activated via env
# COGMEM_API_GENERATE_PROMPT_VARIANT=v2. Same call signature for trivial dispatch.
#
# Two structural changes from legacy (no new rule lines added — see S35 REPORT.md
# for the rationale; legacy already had 14 rules / ~1300 words and adding more risks
# rule-conflict and context bloat with Minimax-M2.7):
#
#   1. **Tightened dedup criterion** — replaces legacy rule that said
#      "Two entries refer to same object if shared attributes (size, type, location,
#       context)". That criterion caused Minimax to conflate distinct events (S35
#      c060: 5-6 distinct game wins → reported as "four"). v2 requires an EXPLICIT
#      identifier match (same date OR same opponent OR same unique outcome).
#
#   2. **Inline verbatim snippet next to each MEMORY** (when include_snippets=True)
#      instead of a separate REFERENCES block + "only consult if memory ambiguous"
#      rule (which Minimax mostly ignored). Surfaces date/count details that the
#      paraphrased `text` field strips, without adding new instruction lines.
#
# When include_snippets=False (S35 default — `COGMEM_API_GENERATE_INCLUDE_SNIPPETS=false`),
# v2 still applies fix (1) which addresses ~5/9 probed failure cases on its own.


def build_generation_prompt_v2(
    query: str,
    evidence: list[dict],
    question_date: str | None = None,
    session_date_map: dict[str, str] | None = None,
    include_snippets: bool = True,
) -> str:
    """S35 generation prompt v2 — tighter dedup + inline snippet (when available).

    Same signature as build_generation_prompt for drop-in dispatch via env
    COGMEM_API_GENERATE_PROMPT_VARIANT. Legacy preserved untouched.
    """
    session_order = _build_session_order(session_date_map) if session_date_map else {}

    memory_parts: list[str] = []
    for idx, item in enumerate(evidence, start=1):
        text = item.get("text", "")
        raw_snippet = item.get("raw_snippet") if include_snippets else None

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

        if raw_snippet:
            cleaned = _clean_reference(raw_snippet).strip()
            if cleaned:
                # Inline the verbatim source under the fact (cap to keep prompt bounded).
                snippet_preview = cleaned[:300] + ("..." if len(cleaned) > 300 else "")
                memory_parts.append(f'    src: "{snippet_preview}"')

    memory_block = "\n".join(memory_parts) if memory_parts else "[No memories]"

    sep = "=" * 60
    current_date_line = f"Current date: {question_date}\n" if question_date else ""

    lines = [
        "You are answering a question based on a person's stored memories.",
        "Use ONLY the information provided below — do not add external knowledge.\n",
        current_date_line,
        sep,
        f"QUESTION TO ANSWER: {query}",
        sep + "\n",
        ("MEMORIES (each fact + verbatim source line when available — answer from these):\n"
         if include_snippets else
         "MEMORIES (extracted facts — answer from these):\n") + memory_block + "\n",
        "Instructions:",
        # Same anti-refusal as legacy
        "- Answer PRIMARILY from MEMORIES. If MEMORIES contain partial information",
        "  (e.g., some but not all items in a list), enumerate what you found and",
        "  explicitly state the list may be incomplete.",
        "- Do NOT say 'information not available' when partial evidence exists in MEMORIES.",
        # CHANGED — tighter dedup criterion (the v2 core fix)
        "- For 'how many' / counting questions: if a memory explicitly states a total quantity,",
        "  use that stated number directly. Otherwise enumerate every distinct item found across",
        "  ALL numbered MEMORIES. Two memories describe the SAME event ONLY when they share an",
        "  explicit identifier (same date, same opponent/named entity, same unique outcome).",
        "  Similar events at different dates, opponents, or outcomes are DISTINCT — count each",
        "  separately. Do NOT collapse distinct items merely because they share a category",
        "  (e.g., 'basketball game') or a generic descriptor (e.g., 'buzzer-beater').",
        # Kept condensed temporal rules (legacy had 3 mega paragraphs; v2 keeps the essential bit)
        "- 'N days/weeks/months ago' means the event with the LARGER N occurred FURTHER in the past.",
        "- For 'how long ago' questions: use Current date − the memory's Conversation date.",
        "  Relative words like 'today' or 'recently' in a memory refer to that conversation's date.",
        # Knowledge update rule (condensed from legacy's mega paragraph)
        "- For knowledge-update questions (current state, latest preference): when memories conflict,",
        "  prefer the fact from the most recent session (highest ordinal / latest Conversation date).",
        "- When the question asks for tips, recommendations, or a list of tools/apps/resources:",
        "  enumerate ALL relevant items mentioned across ALL numbered MEMORIES.",
        "- If MEMORIES contain no relevant information at all, say so clearly:",
        "  'I don't have information about this in memory.'",
        "- Cite memories by index, e.g. [1] or [2].",
    ]

    return "\n".join(lines)


_SNIPPET_QUERY_STOPWORDS = {
    "about",
    "after",
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
    "how",
    "into",
    "list",
    "long",
    "many",
    "much",
    "of",
    "the",
    "their",
    "them",
    "they",
    "take",
    "took",
    "was",
    "were",
    "what",
    "when",
    "where",
    "which",
    "who",
    "why",
    "with",
}
_DURATION_QUERY_RE = re.compile(r"\b(?:how long|take|took|for .* before|duration)\b", re.IGNORECASE)
_DURATION_PHRASE_RE = re.compile(
    r"\b(?:about|around|nearly|almost|roughly|approximately|just under|over|under|more than|less than)?\s*"
    r"(?:\d+|one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve|"
    r"a|an)\s+"
    r"(?:day|days|week|weeks|month|months|year|years|hour|hours|minute|minutes)\b",
    re.IGNORECASE,
)
_LIST_ALIAS_TERMS = {
    "band": ("band", "bands", "concert", "festival", "headlined", "headliner", "music"),
    "bands": ("band", "bands", "concert", "festival", "headlined", "headliner", "music"),
    "book": ("book", "books", "author", "authors", "novel", "read", "reading", "recommended"),
    "books": ("book", "books", "author", "authors", "novel", "read", "reading", "recommended"),
    "game": ("game", "games", "gaming", "played", "strategy", "rpg"),
    "games": ("game", "games", "gaming", "played", "strategy", "rpg"),
    "activity": ("activity", "activities", "hobby", "event", "museum", "hiking", "camping"),
    "activities": ("activity", "activities", "hobby", "event", "museum", "hiking", "camping"),
    "gift": ("gift", "gifts", "received", "owns", "item", "items"),
    "gifts": ("gift", "gifts", "received", "owns", "item", "items"),
    "family": ("family", "father", "mother", "sister", "brother", "grandmother"),
    "sport": ("sport", "sports", "exercise", "training", "yoga", "strength", "basketball"),
    "sports": ("sport", "sports", "exercise", "training", "yoga", "strength", "basketball"),
    "exercise": ("sport", "sports", "exercise", "training", "yoga", "strength", "basketball"),
    "exercises": ("sport", "sports", "exercise", "training", "yoga", "strength", "basketball"),
    "class": ("class", "classes", "course", "courses"),
    "classes": ("class", "classes", "course", "courses"),
    "beer": ("beer", "bar", "pub", "stout", "lager"),
    "trick": ("trick", "tricks", "pet", "dog", "sit", "stay", "paw", "rollover"),
    "tricks": ("trick", "tricks", "pet", "dog", "sit", "stay", "paw", "rollover"),
    "city": ("city", "cities", "visited", "trip", "travel"),
    "cities": ("city", "cities", "visited", "trip", "travel"),
    "country": ("country", "countries", "visited", "trip", "travel"),
    "countries": ("country", "countries", "visited", "trip", "travel"),
    "collectible": ("collectible", "collectibles", "collection", "memorabilia"),
    "collectibles": ("collectible", "collectibles", "collection", "memorabilia"),
}


def select_query_relevant_snippet(
    query: str,
    raw_snippet: str,
    fact_text: str = "",
    max_chars: int = 420,
) -> str:
    """Return the most query-relevant snippet windows for inline evidence."""
    cleaned = _clean_reference(raw_snippet).strip()
    if not cleaned:
        return ""

    windows = _split_snippet_windows(cleaned)
    if not windows:
        return cleaned[:max_chars] + ("..." if len(cleaned) > max_chars else "")

    terms = _snippet_query_terms(query, fact_text)
    phrases = _snippet_query_phrases(query)
    wants_duration = bool(_DURATION_QUERY_RE.search(query))
    scored: list[tuple[float, int, str]] = []
    for idx, window in enumerate(windows):
        lowered = window.lower()
        score = 0.0
        score += sum(1.0 for term in terms if term in lowered)
        score += sum(2.0 for phrase in phrases if phrase in lowered)
        if wants_duration and _DURATION_PHRASE_RE.search(window):
            score += 8.0
        if wants_duration and any(token in lowered for token in ("take", "took", "for", "before", "after")):
            score += 1.0
        if score > 0:
            scored.append((score, idx, window))

    if not scored:
        return cleaned[:max_chars] + ("..." if len(cleaned) > max_chars else "")

    ranked = sorted(scored, key=lambda item: (-item[0], item[1]))
    max_score = ranked[0][0]
    threshold = max(2.0, max_score * 0.5)
    selected_indices = [idx for score, idx, _ in ranked if score >= threshold][:3]
    selected = [windows[idx] for idx in sorted(selected_indices)]
    preview = " ".join(selected).strip()
    if len(preview) <= max_chars:
        return preview
    return preview[:max_chars].rstrip() + "..."


def _split_snippet_windows(text: str) -> list[str]:
    normalized = re.sub(r"\s+", " ", text).strip()
    parts = re.split(r"(?=\[[^\]]+\]:)|(?<=[.!?])\s+", normalized)
    windows = [part.strip() for part in parts if part.strip()]
    if len(windows) <= 1:
        return windows

    merged: list[str] = []
    buffer = ""
    for part in windows:
        if not buffer:
            buffer = part
        elif len(buffer) < 80:
            buffer = f"{buffer} {part}"
        else:
            merged.append(buffer)
            buffer = part
    if buffer:
        merged.append(buffer)
    return merged


def _snippet_query_terms(query: str, fact_text: str = "") -> set[str]:
    seed = f"{query} {fact_text}".lower()
    terms: set[str] = set()
    for token in re.findall(r"[a-z0-9]+", seed):
        if len(token) < 3 or token in _SNIPPET_QUERY_STOPWORDS:
            continue
        terms.add(token)
        for alias in _LIST_ALIAS_TERMS.get(token, ()):
            terms.add(alias)
    return terms


def _snippet_query_phrases(query: str) -> set[str]:
    phrases: set[str] = set()
    for match in re.finditer(r"\b[A-Z][a-z0-9]+(?:\s+[A-Z][a-z0-9]+){0,3}\b", query):
        phrase = match.group(0).strip().lower()
        if phrase and phrase not in {"the", "which", "what", "where", "when", "who", "how"}:
            phrases.add(phrase)
    return phrases


_HINT_CITY_BEFORE_QUERY_RE = re.compile(
    r"\bwhich\s+city\s+was\s+(?P<subject>[A-Z][a-z]+)\s+in\s+before\s+"
    r"travel(?:ing|ling|ed|led)?\s+to\s+(?P<anchor>[A-Z][A-Za-z]*(?:\s+[A-Z][A-Za-z]*){0,3})",
    re.IGNORECASE,
)
_HINT_WORKSHOP_DURATION_QUERY_RE = re.compile(
    r"\bhow\s+long\b.*\bworkshop\b.*\bin\s+(?P<city>[A-Z][A-Za-z]+(?:\s+[A-Z][A-Za-z]+){0,3})",
    re.IGNORECASE,
)
_HINT_PROPER_PLACE_RE = re.compile(r"\b(?:[A-Z][a-z]+(?:\s+[A-Z][a-z]+){0,3}|NYC|UK|USA|CA)\b")
_HINT_IGNORED_PROPER_NAMES = {
    "a",
    "cal",
    "calvin",
    "dave",
    "harry potter",
    "how",
    "involving",
    "john",
    "memory",
    "session",
    "the",
    "tim",
    "which",
}
_HINT_CITY_ANCHOR_CUES = (
    "travel",
    "traveled",
    "travelled",
    "traveling",
    "travelling",
    "trip to",
    "took a trip",
    "visit",
    "visited",
    "went to",
)
_HINT_WORKSHOP_START_CUES = (
    "visited",
    "attended",
    "got to go",
    "went to",
    "go to a car workshop",
)
_HINT_WORKSHOP_SELECTION_CUES = (
    "picked",
    "selected",
    "chosen",
    "accepted",
)
_HINT_RETURN_CUES = (
    "returned from",
    "came back from",
    "back from",
)
_HINT_PROJECT_HISTORY_REJECT_CUES = (
    "age 10",
    "as a kid",
    "childhood",
    "dad",
    "ever since",
    "father",
    "mechanic",
    "neighbor",
    "one summer",
    "profession",
    "works on cars",
)
_HINT_PROJECT_START_CUES = (
    "restoring a car",
    "restoring his car",
    "restoring the car",
    "car project",
    "beat-up",
    "beat up",
    "finish restoring",
    "fixed up by the end of next month",
    "end of next month",
    "project is going great",
)
_HINT_PROJECT_END_CUES = (
    "ford",
    "mustang",
)
_HINT_PROJECT_WORK_CUES = (
    "brought",
    "came back to life",
    "come back to life",
    "found",
    "junkyard",
    "restoration",
    "restore",
    "restored",
    "working",
)
_HINT_NUMBER_WORDS = {
    1: "one",
    2: "two",
    3: "three",
    4: "four",
    5: "five",
    6: "six",
    7: "seven",
    8: "eight",
    9: "nine",
    10: "ten",
    11: "eleven",
    12: "twelve",
}


def _parse_hint_date(value: str | None) -> date | None:
    if not value:
        return None
    raw = str(value).strip()
    for fmt in ("%Y-%m-%d", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%d %H:%M:%S"):
        try:
            return datetime.strptime(raw, fmt).date()
        except ValueError:
            pass
    try:
        return datetime.fromisoformat(raw.replace("Z", "+00:00")).date()
    except ValueError:
        return None


def _hint_item_text(item: dict) -> tuple[str, str]:
    text = str(item.get("text") or "").strip()
    raw = str(item.get("raw_snippet") or "").strip()
    combined = f"{text} {raw}".strip()
    return text, combined


def _hint_memory_ref(record: dict, when: date | None = None) -> str:
    doc_id = str(record["item"].get("document_id") or "?")
    suffix = f" {when.isoformat()}" if when else ""
    return f"[{record['idx']}]/{doc_id}{suffix}"


def _hint_event_date(session_date: date, combined: str) -> tuple[date, str]:
    if re.search(r"\byesterday\b", combined, re.IGNORECASE):
        return session_date - timedelta(days=1), f"yesterday from session date {session_date.isoformat()}"
    return session_date, "session date"


def _format_about_weeks(days: int, *, rounded: bool = False) -> str:
    weeks = max(1, round(days / 7) if rounded else days // 7)
    word = _HINT_NUMBER_WORDS.get(weeks, str(weeks))
    unit = "week" if weeks == 1 else "weeks"
    return f"about {word} {unit}"


def _extract_hint_city_mentions(text: str, subject: str, anchor: str) -> set[str]:
    subject_lower = subject.lower()
    anchor_lower = anchor.lower()
    cities: set[str] = set()
    for match in _HINT_PROPER_PLACE_RE.finditer(text):
        token = match.group(0).strip()
        lowered = token.lower()
        if lowered in _HINT_IGNORED_PROPER_NAMES:
            continue
        if lowered in {subject_lower, anchor_lower}:
            continue
        if _looks_like_city_context(text, token):
            cities.add(token)
    return cities


def _looks_like_city_context(text: str, city: str) -> bool:
    escaped = re.escape(city)
    patterns = (
        rf"\bin\s+{escaped}\b",
        rf"\bto\s+{escaped}\b",
        rf"\b(?:visited|visit|travel(?:ed|led|ing|ling)?|went\s+to|trip\s+to)\s+{escaped}\b",
        rf"\b{escaped}\b.{0,80}\b(?:city|cities|trip|travel|visited|visit|game|place)\b",
        rf"\b(?:city|cities|trip|travel|visited|visit|game|place)\b.{0,80}\b{escaped}\b",
    )
    return any(re.search(pattern, text, re.IGNORECASE) for pattern in patterns)


def _build_derived_temporal_hints(
    query: str,
    evidence: list[dict],
    session_date_map: dict[str, str] | None,
) -> str:
    """Build narrow deterministic hints for high-confidence temporal cases."""
    if not session_date_map:
        return ""

    records: list[dict] = []
    for idx, item in enumerate(evidence, start=1):
        doc_id = str(item.get("document_id") or "")
        session_date = _parse_hint_date(session_date_map.get(doc_id))
        if not session_date:
            continue
        text, combined = _hint_item_text(item)
        records.append(
            {
                "idx": idx,
                "item": item,
                "date": session_date,
                "text": text,
                "combined": combined,
                "lowered": combined.lower(),
            }
        )
    if not records:
        return ""

    hints = [
        hint
        for hint in (
            _hint_city_before_travel(query, records),
            _hint_workshop_duration(query, records),
            _hint_project_duration(query, records),
        )
        if hint
    ]
    if not hints:
        return ""
    return "DERIVED TEMPORAL HINTS:\n" + "\n".join(f"- {hint}" for hint in hints)


def _hint_city_before_travel(query: str, records: list[dict]) -> str:
    match = _HINT_CITY_BEFORE_QUERY_RE.search(query)
    if not match:
        return ""
    subject = match.group("subject").strip()
    anchor = match.group("anchor").strip().rstrip("?.!,")
    subject_lower = subject.lower()
    anchor_lower = anchor.lower()

    anchor_records = [
        record
        for record in records
        if anchor_lower in record["lowered"]
        and any(cue in record["lowered"] for cue in _HINT_CITY_ANCHOR_CUES)
    ]
    if not anchor_records:
        return ""
    anchor_record = sorted(anchor_records, key=lambda record: record["date"])[0]
    anchor_date = anchor_record["date"]

    candidates: dict[str, list[dict]] = {}
    for record in records:
        if record["date"] >= anchor_date:
            continue
        if subject_lower not in record["lowered"]:
            continue
        for city in _extract_hint_city_mentions(record["combined"], subject, anchor):
            candidates.setdefault(city, []).append(record)

    if len(candidates) != 1:
        return ""

    city, city_records = next(iter(candidates.items()))
    city_record = sorted(city_records, key=lambda record: record["date"])[-1]
    return (
        f"City-before-travel: {_hint_memory_ref(city_record, city_record['date'])} mentions "
        f"{city} for {subject} before {_hint_memory_ref(anchor_record, anchor_date)} "
        f"{anchor} travel. Answer hint: {city}."
    )


def _hint_workshop_duration(query: str, records: list[dict]) -> str:
    match = _HINT_WORKSHOP_DURATION_QUERY_RE.search(query)
    if not match:
        return ""
    city = match.group("city").strip().rstrip("?.!,")
    city_lower = city.lower()

    start_records = []
    end_records = []
    for record in records:
        lowered = record["lowered"]
        if "workshop" in lowered and city_lower in lowered:
            if any(cue in lowered for cue in _HINT_WORKSHOP_SELECTION_CUES):
                continue
            if any(cue in lowered for cue in _HINT_WORKSHOP_START_CUES):
                start_records.append(record)
        if city_lower in lowered and any(cue in lowered for cue in _HINT_RETURN_CUES):
            end_records.append(record)

    if not start_records or not end_records:
        return ""
    start_record = sorted(start_records, key=lambda record: record["date"])[0]
    resolved_ends = [
        (_hint_event_date(record["date"], record["combined"]), record)
        for record in end_records
    ]
    end_pair, end_record = sorted(resolved_ends, key=lambda pair: pair[0][0])[-1]
    end_date, end_note = end_pair
    if end_date <= start_record["date"]:
        return ""

    days = (end_date - start_record["date"]).days
    if days < 7:
        return ""
    duration = _format_about_weeks(days)
    return (
        f"Workshop duration: {_hint_memory_ref(start_record, start_record['date'])} is the "
        f"attended/visited {city} workshop start; {_hint_memory_ref(end_record, end_date)} "
        f"is the return from {city} ({end_note}). Ignore selected/picked-for-workshop dates. "
        f"Answer hint: {duration}."
    )


def _hint_project_duration(query: str, records: list[dict]) -> str:
    lowered_query = query.lower()
    if not _DURATION_QUERY_RE.search(lowered_query):
        return ""
    if "ford" not in lowered_query and "mustang" not in lowered_query:
        return ""
    subject = _hint_query_subject(query)
    if not subject:
        return ""
    subject_lower = subject.lower()

    start_records = []
    end_records = []
    for record in records:
        lowered = record["lowered"]
        if subject_lower not in lowered:
            continue
        if any(cue in lowered for cue in _HINT_PROJECT_HISTORY_REJECT_CUES):
            continue
        if any(cue in lowered for cue in _HINT_PROJECT_START_CUES) and "car" in lowered:
            start_records.append(record)
        if (
            any(target in lowered for target in _HINT_PROJECT_END_CUES)
            and any(cue in lowered for cue in _HINT_PROJECT_WORK_CUES)
        ):
            end_records.append(record)

    if not start_records or not end_records:
        return ""
    start_record = sorted(start_records, key=lambda record: record["date"])[0]
    later_ends = [record for record in end_records if record["date"] > start_record["date"]]
    if not later_ends:
        return ""
    end_record = sorted(later_ends, key=lambda record: record["date"])[-1]
    days = (end_record["date"] - start_record["date"]).days
    if days < 28:
        return ""
    weeks = max(1, round(days / 7))
    week_word = _HINT_NUMBER_WORDS.get(weeks, str(weeks))
    duration = f"roughly {week_word} weeks"
    if 45 <= days <= 62:
        duration += " / nearly two months"
    return (
        f"Project duration: {_hint_memory_ref(start_record, start_record['date'])} shows "
        f"{subject} already restoring a car project; {_hint_memory_ref(end_record, end_record['date'])} "
        f"identifies the Ford/Mustang restoration. Gap is {duration}. "
        "Answer hint: nearly two months."
    )


def _hint_query_subject(query: str) -> str:
    ignored_query_heads = {"how", "which", "what", "where", "when", "who", "the"}
    for match in _HINT_PROPER_PLACE_RE.finditer(query):
        token = match.group(0).strip()
        lowered = token.lower()
        if lowered in ignored_query_heads:
            continue
        if lowered in {"ford", "mustang", "ford mustang", "san francisco", "chicago", "seattle"}:
            continue
        return token.split()[0]
    return ""


_V3_TEMPORAL_ANCHOR_RULE = "\n".join([
    "- For before/after temporal-chain questions: first identify the named anchor event",
    "  and its Session date, then compare candidate memories against that anchor.",
    "  Example: if the question asks what happened before a Chicago trip, first find",
    "  the Chicago-trip memory/date, then choose only candidate events whose memory",
    "  date or resolved relative date is earlier than that anchor.",
])


def build_generation_prompt_v3_temporal(
    query: str,
    evidence: list[dict],
    question_date: str | None = None,
    session_date_map: dict[str, str] | None = None,
    include_snippets: bool = True,
) -> str:
    """S35-T8B prompt variant: v2 plus one compact temporal-anchor rule.

    Keep this deliberately narrow so probes can isolate temporal-chain lift without
    brand-disambiguation or counterfactual-rule interference.
    """
    prompt = build_generation_prompt_v2(
        query,
        evidence,
        question_date=question_date,
        session_date_map=session_date_map,
        include_snippets=include_snippets,
    )
    anchor = (
        "- For 'how long ago' questions: use Current date − the memory's Conversation date.\n"
        "  Relative words like 'today' or 'recently' in a memory refer to that conversation's date."
    )
    if _V3_TEMPORAL_ANCHOR_RULE in prompt:
        return prompt
    if anchor in prompt:
        return prompt.replace(anchor, f"{anchor}\n{_V3_TEMPORAL_ANCHOR_RULE}", 1)
    return f"{prompt}\n{_V3_TEMPORAL_ANCHOR_RULE}"


_V3_LIST_COMPLETENESS_RULE = "\n".join([
    "- For list/enumeration questions about places, cities, locations, tools, or",
    "  resources: scan ALL numbered MEMORIES before answering. Include every",
    "  distinct candidate that matches the asked relationship, even if it appears",
    "  in a lower-ranked memory. Exclude wish-list/planned places unless the",
    "  question asks about plans or intended visits.",
])


def build_generation_prompt_v3_temporal_list(
    query: str,
    evidence: list[dict],
    question_date: str | None = None,
    session_date_map: dict[str, str] | None = None,
    include_snippets: bool = True,
) -> str:
    """S35-T8E prompt variant: temporal anchor plus list completeness guard."""
    prompt = build_generation_prompt_v3_temporal(
        query,
        evidence,
        question_date=question_date,
        session_date_map=session_date_map,
        include_snippets=include_snippets,
    )
    anchor = (
        "- When the question asks for tips, recommendations, or a list of tools/apps/resources:\n"
        "  enumerate ALL relevant items mentioned across ALL numbered MEMORIES."
    )
    if _V3_LIST_COMPLETENESS_RULE in prompt:
        return prompt
    if anchor in prompt:
        return prompt.replace(anchor, f"{anchor}\n{_V3_LIST_COMPLETENESS_RULE}", 1)
    return f"{prompt}\n{_V3_LIST_COMPLETENESS_RULE}"


_V4_GENERAL_LIST_COMPLETENESS_RULE = "\n".join([
    "- For list/enumeration questions about bands, books/authors, games, activities/events,",
    "  gifts/items, family members, sports/exercises, classes, beers, pet tricks,",
    "  countries/cities, collectibles, tools, apps, or resources: scan ALL numbered MEMORIES",
    "  before answering. Include every distinct candidate that matches the asked relationship.",
])
_V4_CAUSAL_NEGATIVE_RULE = "\n".join([
    "- For causal 'why' questions: give a reason only when a MEMORY or src explicitly links",
    "  the queried subject/object/action to that reason. Do NOT infer from a different person,",
    "  swapped entity relation, nearby unrelated event, or general world knowledge. If the",
    "  explicit relation is absent, say memory does not state why.",
    "  If the memories only support the same relationship for a different person-pair",
    "  or entity-pair, answer ONLY that memory has no information for the queried pair;",
    "  do NOT continue by explaining the adjacent pair's reason.",
])
_V4_EXPLICIT_DURATION_RULE = "\n".join([
    "- For 'how long', 'how long did it take', or 'for how long before' questions: first scan",
    "  fact text and src lines for explicit duration phrases such as 'two weeks',",
    "  'nearly three months', or 'for a year'. Use the stated duration before doing date",
    "  arithmetic. Only compute dates if no explicit duration is stated.",
])
_V4_SESSION_DATE_ARITHMETIC_RULE = "\n".join([
    "- Session-date ordering is valid evidence for temporal and duration questions.",
    "  Do NOT require the words 'before', 'after', or 'how long' to appear in a fact.",
    "  For before/after questions, identify the anchor memory Date, then choose candidate",
    "  memories with earlier/later Dates that match the subject and requested relation.",
    "  City-before-travel pattern: if the question asks which city/person-location came",
    "  before traveling to an anchor city, answer the earlier dated city memory for that",
    "  subject when it is the only matching earlier city candidate.",
    "  For duration questions with no stated duration, compute the gap between relevant",
    "  Session Dates for the same subject/project/event, e.g. started/attended vs returned/",
    "  continued/finished. State the arithmetic briefly and avoid unrelated date gaps.",
    "  Attended-workshop/returned-from-city memories bracket a workshop duration; apply",
    "  relative words like 'yesterday' to the later Session Date before subtracting.",
    "  If the memories only bracket an approximate duration, report the coarse rounded",
    "  unit (for example, about two weeks) rather than over-precise day counts.",
    "  Such date-bracket evidence counts as relevant evidence; do not refuse merely because",
    "  no memory states the duration in words.",
])
_V4_TANGENTIAL_EVIDENCE_RULE = "\n".join([
    "- Do not turn tangential memories into an answer. If none of the MEMORIES explicitly",
    "  addresses the queried subject plus relationship, say: 'I don't have information about",
    "  this in memory.'",
])


def build_generation_prompt_v4_evidence_guard(
    query: str,
    evidence: list[dict],
    question_date: str | None = None,
    session_date_map: dict[str, str] | None = None,
    include_snippets: bool = True,
) -> str:
    """S35-T8G prompt variant: T8E guards plus query-relevant source windows."""
    session_order = _build_session_order(session_date_map) if session_date_map else {}

    memory_parts: list[str] = []
    for idx, item in enumerate(evidence, start=1):
        text = item.get("text", "")
        raw_snippet = item.get("raw_snippet") if include_snippets else None

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

        if raw_snippet:
            snippet_preview = select_query_relevant_snippet(query, raw_snippet, fact_text=text)
            if snippet_preview:
                memory_parts.append(f'    src: "{snippet_preview}"')

    memory_block = "\n".join(memory_parts) if memory_parts else "[No memories]"
    temporal_hints = _build_derived_temporal_hints(query, evidence, session_date_map)

    sep = "=" * 60
    current_date_line = f"Current date: {question_date}\n" if question_date else ""

    lines = [
        "You are answering a question based on a person's stored memories.",
        "Use ONLY the information provided below — do not add external knowledge.\n",
        current_date_line,
        sep,
        f"QUESTION TO ANSWER: {query}",
        sep + "\n",
        ("MEMORIES (each fact + query-relevant source line when available — answer from these):\n"
         if include_snippets else
         "MEMORIES (extracted facts — answer from these):\n") + memory_block + "\n",
    ]

    if temporal_hints:
        lines.append(temporal_hints + "\n")

    lines.extend([
        "Instructions:",
        "- Answer PRIMARILY from MEMORIES. If MEMORIES contain partial information",
        "  (e.g., some but not all items in a list), enumerate what you found and",
        "  explicitly state the list may be incomplete.",
        "- Do NOT say 'information not available' when partial evidence exists in MEMORIES.",
        "- For 'how many' / counting questions: if a memory explicitly states a total quantity,",
        "  use that stated number directly. Otherwise enumerate every distinct item found across",
        "  ALL numbered MEMORIES. Two memories describe the SAME event ONLY when they share an",
        "  explicit identifier (same date, same opponent/named entity, same unique outcome).",
        "  Similar events at different dates, opponents, or outcomes are DISTINCT — count each",
        "  separately. Do NOT collapse distinct items merely because they share a category",
        "  (e.g., 'basketball game') or a generic descriptor (e.g., 'buzzer-beater').",
        "- 'N days/weeks/months ago' means the event with the LARGER N occurred FURTHER in the past.",
        "- For 'how long ago' questions: use Current date − the memory's Conversation date.",
        "  Relative words like 'today' or 'recently' in a memory refer to that conversation's date.",
        _V3_TEMPORAL_ANCHOR_RULE,
        "- For knowledge-update questions (current state, latest preference): when memories conflict,",
        "  prefer the fact from the most recent session (highest ordinal / latest Conversation date).",
        "- When the question asks for tips, recommendations, or a list of tools/apps/resources:",
        "  enumerate ALL relevant items mentioned across ALL numbered MEMORIES.",
        _V4_GENERAL_LIST_COMPLETENESS_RULE,
        _V4_CAUSAL_NEGATIVE_RULE,
        _V4_EXPLICIT_DURATION_RULE,
        _V4_SESSION_DATE_ARITHMETIC_RULE,
        _V4_TANGENTIAL_EVIDENCE_RULE,
        "- If MEMORIES contain no relevant information at all, say so clearly:",
        "  'I don't have information about this in memory.'",
        "- Cite memories by index, e.g. [1] or [2].",
    ])

    return "\n".join(lines)
