"""Pass 3 prompt: intra-session inter-chunk relationship identification.

Called after Pass 1 + Pass 2 facts are merged (dedup_facts). Receives the full
list of facts for a session and asks the SLM to identify cross-chunk causal,
transition, and action-effect relations that target_index-based extraction
inside each chunk could not capture.
"""

from __future__ import annotations


def build_pass3_prompt(facts: list[tuple[str, str]]) -> str:
    """Build relationship-identification prompt for merged session facts.

    Args:
        facts: List of (fact_text, fact_type) tuples, 0-indexed.
               Should already be deduped (output of dedup_facts).

    Returns:
        Prompt string for the LLM.
    """
    numbered = "\n".join(f"[{i}][{ftype}] {text}" for i, (text, ftype) in enumerate(facts))
    return f"""You are identifying relationships between memory facts extracted from a conversation.

FACTS (format: [index][fact_type] text):
{numbered}

Identify HIGH-CONFIDENCE relationships only. Three types are allowed:
- "causal"       : fact A directly caused or triggered fact B  (source_index MUST be < target_index — cause precedes effect)
- "fulfilled_by" : source fact must be type "intention", target fact must be type "experience"
- "a_o_causal"   : source fact must be type "action_effect", target is the observable outcome fact

Return ONLY valid JSON matching this schema — no markdown, no explanation:
{{"relations": [
  {{"source": <int>, "target": <int>, "type": "causal|fulfilled_by|a_o_causal", "strength": <float 0.0-1.0}},
  ...
]}}

Rules:
- Only include relations with strength >= 0.6
- For "causal": source < target (cause must appear before effect in the list)
- For "fulfilled_by": only when source is [intention] and target is [experience]
- For "a_o_causal": only when source is [action_effect]
- source and target are 0-based indices into the FACTS list above
- If no clear relationships exist: {{"relations": []}}
"""
