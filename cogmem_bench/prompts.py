"""Per-session generation prompts — render ONE session of a ScenarioSpec at a time.

Multi-call generation: one call per session, threading a running recap of prior sessions
so the conversation stays consistent and on-topic. A single call for 7-10 coherent,
trap-laden sessions is unreliable (dropped sessions, flattened metadata, lost continuity).

Separate from cogmem_api/prompts/eval. The generator produces surface text only; the gold
fact, gold answer, and discriminating metadata are fixed in the spec.
"""

from __future__ import annotations

import json

from .schema import Message, ScenarioSpec

# Per-target-type guidance: how to embed the discriminating fact so a
# world/experience/opinion-only reader cannot reconstruct the answer.
_TYPE_GUIDANCE: dict[str, str] = {
    "intention": (
        "This session must show the INTENTION and its lifecycle. Let the user FORM, REVISE, "
        "or RESOLVE the plan (fulfilled / abandoned) through how they talk — the answer "
        "depends on the FINAL status, not on the plan merely being mentioned. Never state the "
        "status as a flat labelled fact."
    ),
    "action_effect": (
        "This session must convey an ACTION->EFFECT causal rule: under a precondition, the "
        "user takes an action that produces an outcome. Surface all three naturally across "
        "turns; never list them as a bullet summary."
    ),
    "habit": (
        "This session must show a HABIT — a repeated behaviour — recurring with its frequency, "
        "so the answer requires aggregating repetitions into a pattern. A single one-off "
        "mention must not be enough."
    ),
}

_TRAP_GUIDANCE: dict[str, str] = {
    "type-confusion": "Add a one-off event that superficially resembles the gold pattern but is the wrong type.",
    "stale-intention": "Add a confident statement of a plan that is later quietly dropped or changed.",
    "contradiction": "Add a preference/belief the user states here that conflicts with the gold, to test recency handling.",
    "volume": "Add several similar-but-irrelevant facts to force aggregation and tempt miscounting.",
}

Role = str  # "gold" | "trap" | "filler"


def session_role(spec: ScenarioSpec, session_index: int) -> Role:
    if session_index == spec.gold_fact.session_index:
        return "gold"
    trap_idxs = {t.session_index for t in spec.traps if t.session_index is not None}
    if session_index in trap_idxs:
        return "trap"
    return "filler"


def _canonical_block(shared_context: dict[str, str]) -> str:
    if not shared_context:
        return ""
    facts = "\n".join(f"  - {k}: {v}" for k, v in shared_context.items())
    return (
        "CANONICAL FACTS (every session must agree with these EXACTLY — same names, "
        f"dates, numbers):\n{facts}\n\n"
    )


def _older_recap_block(prior_recaps: list[str]) -> str:
    if not prior_recaps:
        return "  (none yet)"
    return "\n".join(f"  - {r}" for r in prior_recaps)


def _recent_verbatim_block(recent_sessions: list[tuple[str, list[Message]]]) -> str:
    if not recent_sessions:
        return "  (none yet)"
    out: list[str] = []
    for label, messages in recent_sessions:
        out.append(f"  [{label}]")
        for m in messages:
            out.append(f"    {m.role}: {m.content}")
    return "\n".join(out)


def build_session_prompt(
    spec: ScenarioSpec,
    session_index: int,
    role: Role,
    prior_recaps: list[str],
    recent_sessions: list[tuple[str, list[Message]]] | None = None,
) -> str:
    """Build the prompt for ONE session.

    Consistency across calls comes from three sources, strongest last:
      - `spec.shared_context`: canonical facts injected into every session.
      - `prior_recaps`: one-line recaps of older sessions (model-emitted).
      - `recent_sessions`: the last K sessions verbatim, for tight local continuity.
    """
    total = spec.session_plan.total_sessions
    header = f"""You are simulating one session of a long-running, natural USER/ASSISTANT chat history used to build a memory benchmark. Produce realistic, varied dialogue — NOT a summary.

OVERALL TOPIC (every session stays thematically consistent): {spec.topic}
This is SESSION {session_index + 1} of {total} (a conversation on its own day).

{_canonical_block(spec.shared_context)}EARLIER SESSIONS (recaps — stay consistent; do not contradict):
{_older_recap_block(prior_recaps)}

RECENT SESSIONS (verbatim — maintain exact continuity with these, reuse the same names/numbers):
{_recent_verbatim_block(recent_sessions or [])}
"""

    if role == "gold":
        gold_meta = json.dumps(spec.gold_fact.metadata, ensure_ascii=False)
        directive = f"""THIS SESSION CARRIES THE GOLD FACT:
  fact: {spec.gold_fact.text}
  type: {spec.gold_fact.fact_type}
  structured metadata the benchmark answer depends on: {gold_meta}

HOW TO EMBED IT:
  {_TYPE_GUIDANCE[spec.target_type]}
"""
    elif role == "trap":
        matching = [t for t in spec.traps if t.session_index == session_index]
        traps_lines = "\n".join(
            f"  - [{t.trap_type}] {t.description} (hint: {_TRAP_GUIDANCE.get(t.trap_type, '')})"
            for t in matching
        ) or "  - (distractor session, on-topic but answer-irrelevant)"
        directive = f"""THIS SESSION IS A DISTRACTOR/TRAP. It must be on-topic but must NOT let the
benchmark question be answered from it alone:
{traps_lines}
"""
    else:
        directive = (
            "THIS SESSION IS FILLER: on-topic small talk / unrelated detail. It must NOT reveal "
            "the gold fact or let the question be answered from it.\n"
        )

    footer = """HARD RULES:
  - Do NOT mention the benchmark, the question, the gold answer, or any
    "status/precondition/outcome/frequency" labels verbatim.
  - Keep it natural: indirection, coreference, realistic detail.

OUTPUT — return ONLY a JSON object for THIS ONE session, no prose:
{
  "recap": "one sentence summarizing what this session established (names/facts later sessions must stay consistent with)",
  "messages": [
    {"role": "user", "content": "..."},
    {"role": "assistant", "content": "..."}
  ]
}
"""
    return header + "\n" + directive + "\n" + footer
