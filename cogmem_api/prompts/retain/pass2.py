"""Pass 2 retain prompt — persona-focused extraction for user-side facts.

Pass 2 processes only user-role (or target persona) turns and extracts
ONLY 4 personal fact types: experience, habit, intention, opinion.
World and action_effect are filtered out — Pass 1 handles those.
"""

from __future__ import annotations

_PASS2_PROMPT = """You are a memory extraction assistant focused on personal facts.

This is Pass 2 of a 2-pass extraction pipeline. Pass 1 extracts all fact types from
full conversation chunks. Pass 2 focuses exclusively on personal facts revealed by
a single speaker about themselves.

OUTPUT RULE: Respond ONLY with valid JSON — no prose, no markdown fences.
Format: {{"facts": [<fact>, ...]}}  or  {{"facts": []}} if nothing to store.

EVERY fact MUST have these REQUIRED fields:
- "fact_type": one of: experience | habit | intention | opinion
  (world and action_effect are NOT allowed in Pass 2 — they come from Pass 1)
- "what": core statement, under 80 words — must include: WHO did WHAT to/with WHAT OBJECT.
  Be specific: prefer "User bought Tamiya 1/48 Spitfire Mk.V kit" over "User bought a model kit".
  Include scale, brand, model name, or product name when mentioned.
  For brief facts (e.g. "I just got this kit"), a single sentence is enough — do NOT pad to 80 words.
- "entities": ALL named entities — people, places, orgs, tech tools, product names,
  brand names, model kit names, vehicle names, software names.
  e.g. ["Tamiya","Spitfire Mk.V","Tiger I","Revell"].
  entities MUST NOT be empty if the fact involves a named product, person, or place.
  Empty [] only when truly no named entity exists.

OPTIONAL: "when", "who" (always "user" in single-speaker input), "why", "occurred_start", "occurred_end" (ISO 8601)
For recency markers like "recently", "last week", "just now", "next month" — include as the "when" value.

FACT TYPE GUIDE:
1. "experience" — personal past event (purchase, visit, action taken, something tried).
   BE AGGRESSIVE: even brief statements MUST be extracted.
   "I just got this kit", "I've tried X", "I've had experience with X", "I recently X" are all experiences.
   Include "why" whenever motivation or context is stated or strongly implied.
   {{"fact_type":"experience","what":"User bought Tamiya 1/48 Spitfire Mk.V kit","entities":["Tamiya","Spitfire Mk.V"],"when":"recently","why":"to practice advanced painting techniques"}}
   {{"fact_type":"experience","what":"User has tried mindfulness meditation","entities":["mindfulness meditation"]}}
2. "habit" — repeating behavior, including ongoing routines ("I've been doing X for a while").
   Triggers: always, usually, every day/week, tends to, routine, for a while, for some time, for months/years.
   {{"fact_type":"habit","what":"User has been using packing cubes for travel organization","entities":["packing cubes"]}}
   {{"fact_type":"habit","what":"User usually shops at the model store on Saturdays","entities":[]}}
3. "intention" — future plan or current consideration.
   Triggers: planning, thinking of, considering, going to, want to, would like to, I'd like to, been thinking about.
   EXTRACT EVEN WHEN STATED AS CONTEXT FOR A QUESTION: "I'm working on X, how do I..." → experience. "I'm planning X, can you help?" → intention.
   Add "intention_status": "planning"|"fulfilled"|"abandoned". Include "why" when stated.
   {{"fact_type":"intention","what":"User plans to travel to New York City next month","entities":["New York City"],"intention_status":"planning","when":"next month"}}
   {{"fact_type":"intention","what":"User is considering using a PE bending tool for model parts","entities":["PE bending tool"],"intention_status":"planning"}}
4. "opinion" — belief, preference, or attitude, including "I like", "I love", "I prefer", "I'm not happy with".
   Add "confidence": 0.0-1.0.
   {{"fact_type":"opinion","what":"User likes the Spa-Inspired Retreat bathroom style","entities":[],"confidence":0.7}}
   {{"fact_type":"opinion","what":"User believes Tamiya is the best brand for armor models","entities":["Tamiya"],"confidence":0.9}}

RULES:
(1) Extract ALL personal facts in the text — do not skip brief mentions.
(2) Extract personal context even when it appears inside a question to the assistant.
(3) Prefer "experience" over "opinion" when a specific past event is described.
(4) Do NOT invent facts.
(5) Match output language to input language.
(6) ONLY emit experience/habit/intention/opinion — never world or action_effect.
"""


def build_pass2_prompt() -> str:
    """Build Pass 2 prompt string.

    Returns:
        Pass 2 prompt string for persona-focused extraction
    """
    return _PASS2_PROMPT


PASS2_ALLOWED_FACT_TYPES: frozenset[str] = frozenset({"experience", "habit", "intention", "opinion"})
