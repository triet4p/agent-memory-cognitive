"""Pass 1 retain prompt — extracted from fact_extraction.py for centralization.

This module contains the base prompt and mode variants for Pass 1 of the 2-pass
extraction pipeline. Pass 1 processes full mixed-speaker chunks and extracts
all 6 fact types.
"""

from __future__ import annotations

_ALLOWED_MODES: set[str] = {"concise", "custom", "verbatim", "verbose"}

_BASE_PROMPT = """You are a memory extraction assistant. Extract durable facts from conversations for long-term storage.

OUTPUT RULE: Respond ONLY with valid JSON — no prose, no markdown fences.
Format: {{"facts": [<fact>, ...]}}  or  {{"facts": []}} if nothing to store.

EVERY fact MUST have these REQUIRED fields:
- "fact_type": one of: world | experience | opinion | habit | intention | action_effect
- "what": core statement, under 80 words — must include: WHO did WHAT to/with WHAT OBJECT.
  Be specific: prefer "User bought Tamiya 1/48 Spitfire Mk.V kit" over "User bought a model kit".
  Include scale, brand, model name, or product name when mentioned.
- "entities": ALL named entities — people, places, orgs, tech tools, product names, brand names,
  model kit names, vehicle names, software names. e.g. ["Alice","Tamiya","Spitfire Mk.V","Tiger I"].
  For experience/action_effect facts: entities MUST NOT be empty if the fact involves a named product,
  person, or place. Empty [] only when truly no named entity exists.

OPTIONAL: "when", "who", "why", "fact_kind" (event|conversation), "occurred_start", "occurred_end" (ISO 8601)

FACT TYPE GUIDE:
1. "world" — objective fact, not time-bound: job, role, skill, location, general knowledge,
   technical facts, advice, recommendations, abstract descriptions of challenges.
   Assistant suggestions and general how-to advice are ALWAYS "world", never "experience".
   {{"fact_type":"world","what":"Alice works as ML Engineer at DI","entities":["Alice","DI"]}}
2. "experience" — USER's personal past event at a specific time (purchase, visit, action taken).
   ONLY use "experience" if the USER (not the assistant) did or experienced something specific.
   Do NOT use "experience" for assistant suggestions, general advice, or abstract descriptions.
   Include "why" whenever motivation or context is stated or strongly implied.
   Example: "why": "to practice metal painting techniques"
   {{"fact_type":"experience","what":"Alice joined DI in April 2024","entities":["Alice","DI"],"when":"April 2024","why":"to work on real-world ML projects"}}
3. "opinion" — belief or preference; add "confidence": 0.0-1.0
   {{"fact_type":"opinion","what":"Alice believes Python is best for ML","entities":["Alice"],"confidence":0.85}}
4. "habit" — repeating behavior; triggers: always, usually, every day/week, every morning, tends to, routine, regular
   Use "habit" (NOT "world") when the fact describes what someone *regularly does*.
   {{"fact_type":"habit","what":"Alice always checks email before standup","entities":["Alice"]}}
   {{"fact_type":"habit","what":"Team holds a standup every morning at 9 AM","entities":["Team"]}}
5. "intention" — future plan or goal; add "intention_status": "planning"|"fulfilled"|"abandoned"
   Include "why" whenever the goal reason is stated.
   - planning: goal is still future ("plan to", "will", "going to", "want to", "intend to")
   - fulfilled: goal was already completed ("finished", "completed", "achieved", "done", "it worked", "all tests pass")
   - abandoned: goal was cancelled ("gave up", "decided not to", "dropped", "cancelled")
   When someone says they "finished" or "achieved" a past goal, use fulfilled — NOT planning.
   {{"fact_type":"intention","what":"Alice plans to learn Rust by Q3","entities":["Alice"],"intention_status":"planning","why":"to improve system programming skills"}}
   {{"fact_type":"intention","what":"Alice planned to learn Rust — she finished it last month","entities":["Alice"],"intention_status":"fulfilled"}}
6. "action_effect" — causal triple; REQUIRED fields: "precondition", "action", "outcome", "confidence", "devalue_sensitive"(true|false)
   Each independent cause-effect relationship = ONE separate action_effect fact.
   {{"fact_type":"action_effect","what":"int8 reduced latency","entities":[],"precondition":"Latency>100ms","action":"Switch to int8","outcome":"Latency dropped 75%","confidence":0.92,"devalue_sensitive":true}}
   {{"fact_type":"action_effect","what":"index eliminated full scan","entities":["orders"],"precondition":"Full table scan on orders","action":"Add composite index","outcome":"Query time cut from 3s to 50ms","confidence":0.95,"devalue_sensitive":false}}

RELATIONS (only when facts in same response are linked):
- "causal_relations": [{{"target_index":<int>,"relation_type":"caused_by","strength":0.8}}]
- "action_effect_relations": [{{"target_index":<int>,"relation_type":"a_o_causal","strength":0.9}}]
- "transition_relations": [{{"target_index":<int>,"transition_type":"fulfilled_by"|"triggered"|"enabled_by"|"revised_to"|"contradicted_by","strength":0.9}}]

RULES: (1) Extract ALL facts in the text. (2) Prefer "experience" over "world" when a time is mentioned. (3) Do NOT invent facts. (4) Match output language to input language.

This is Pass 1 of a 2-pass extraction pipeline. A second pass focuses on user-only segments for personal facts. Prioritize cross-turn synthesis facts and assistant-side facts here.
{mission_section}{mode_section}"""

_CONCISE_MODE = """
MODE: concise
- Extract only durable, memory-worthy facts. Skip greetings, filler, and pleasantries.
- Target: 1-5 facts per chunk. Keep each "what" short and precise.
"""

_CUSTOM_MODE = """
MODE: custom — follow these instructions strictly:
{custom_instructions}
"""

_VERBATIM_MODE = """
MODE: verbatim
- Return exactly ONE fact object.
- Do not paraphrase. Use the most informative sentence from the text as "what".
- Focus on extracting "entities", "when", and "fact_type" accurately.
"""

_VERBOSE_MODE = """
MODE: verbose
- Extract every potentially relevant fact, including context, background, and motivation.
- Fill the "why" field whenever motivation is stated or clearly implied.
- Prefer "experience" over "world" when a specific time or event is mentioned.
- Include supporting detail in "what" (up to 80 words is acceptable).
"""


def build_pass1_prompt(config: object) -> tuple[str, str]:
    """Build Pass 1 prompt and mode string from config.

    Args:
        config: Runtime config object with retain_extraction_mode, retain_mission,
                retain_custom_instructions attributes.

    Returns:
        (prompt_string, mode_name) tuple
    """
    mode = str(getattr(config, "retain_extraction_mode", "concise") or "concise").strip().lower()
    if mode not in _ALLOWED_MODES:
        mode = "concise"

    mission = _normalized_optional_text(getattr(config, "retain_mission", None))
    if mission:
        mission_section = f"\nMission:\n{mission}\n"
    else:
        mission_section = ""

    if mode == "custom":
        custom_instructions = _normalized_optional_text(getattr(config, "retain_custom_instructions", None))
        if not custom_instructions:
            mode_section = _CONCISE_MODE
            mode = "concise"
        else:
            mode_section = _CUSTOM_MODE.format(custom_instructions=custom_instructions)
    elif mode == "verbatim":
        mode_section = _VERBATIM_MODE
    elif mode == "verbose":
        mode_section = _VERBOSE_MODE
    else:
        mode_section = _CONCISE_MODE

    return _BASE_PROMPT.format(mission_section=mission_section, mode_section=mode_section), mode


def _normalized_optional_text(value: str | None) -> str | None:
    if not isinstance(value, str):
        return None
    normalized = value.strip()
    if not normalized:
        return None
    if normalized.upper() in {"N/A", "NONE", "NULL"}:
        return None
    return normalized