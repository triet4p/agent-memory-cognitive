"""Retain pipeline — Dialogue: Team collaboration (world + experience + habit).

Scenario:
  Grace is the engineering lead for a 6-person backend team at FinCore.
  The dialogue covers her role (world), a recent sprint retrospective (experience),
  and the team's daily standup habit (habit).

Expected extraction (at minimum):
  - 1+ "world" fact (team/role)
  - 1+ "experience" fact (sprint retro)
  - 1+ "habit" fact (standups)
  - entity "Grace" or "FinCore" present

Difficulty: MEDIUM — three distinct types from one dialogue, moderate inference.
Known flaky with Ministral-3B: standup/review routines are sometimes classified
as "world" instead of "habit". Source-side heuristic override added in
fact_extraction.py to reclassify world facts with strong habit signals.
"""

from __future__ import annotations

import asyncio
import sys
from datetime import UTC, datetime
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from tests.retain._shared import make_config, resolve_llm  # noqa: E402

DIALOGUE = """\
USER: Grace, tell me about your team at FinCore.
GRACE: I lead a 6-person backend engineering team at FinCore focused on the payments platform.
USER: How was the last sprint?
GRACE: Last sprint we completed the fraud detection module ahead of schedule.
       The retrospective last Friday surfaced a lot of useful process improvements.
USER: What does your daily process look like?
GRACE: We hold a 15-minute standup every morning at 9 AM.
       I always review the board before the standup to prepare talking points.
"""

_FAKE_RESPONSE = {
    "facts": [
        {
            "fact_type": "world",
            "what": "Grace leads a 6-person backend engineering team at FinCore focused on the payments platform",
            "entities": ["Grace", "FinCore"],
        },
        {
            "fact_type": "experience",
            "what": "Grace's team completed the fraud detection module ahead of schedule last sprint and held a retrospective",
            "entities": ["Grace", "FinCore"],
            "when": "last sprint",
            "fact_kind": "event",
        },
        {
            "fact_type": "habit",
            "what": "Grace's team holds a 15-minute standup every morning at 9 AM",
            "entities": ["Grace"],
        },
        {
            "fact_type": "habit",
            "what": "Grace always reviews the board before the morning standup",
            "entities": ["Grace"],
        },
    ]
}


async def run_test() -> None:
    from cogmem_api.engine.retain.fact_extraction import extract_facts_from_contents
    from cogmem_api.engine.retain.types import RetainContent

    content = RetainContent(
        content=DIALOGUE,
        context="team_collaboration",
        event_date=datetime(2026, 4, 20, 9, 0, tzinfo=UTC),
    )

    facts, _chunks, _usage = await extract_facts_from_contents(
        contents=[content],
        llm_config=resolve_llm(_FAKE_RESPONSE),
        agent_name="test",
        config=make_config("concise"),
    )

    fact_types = {f.fact_type for f in facts}
    assert "world" in fact_types, f"Missing 'world' fact. Got: {fact_types}"
    assert "experience" in fact_types, f"Missing 'experience' fact. Got: {fact_types}"
    assert "habit" in fact_types, f"Missing 'habit' fact. Got: {fact_types}"

    all_entities = [e.lower() for f in facts for e in f.entities]
    assert any(kw in e for e in all_entities for kw in ("grace", "fincore")), (
        f"Expected entity 'Grace' or 'FinCore'. Got: {all_entities}"
    )

    print("OK  world fact present")
    print("OK  experience fact present")
    print("OK  habit fact present")
    print("OK  entity Grace or FinCore found")


def main() -> None:
    asyncio.run(run_test())
    print("All team collaboration dialogue retain tests passed.")


if __name__ == "__main__":
    main()
