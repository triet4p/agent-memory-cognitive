"""Retain pipeline — Dialogue: Intention lifecycle (planning → fulfilled).

Scenario:
  Last month the user set a goal to write unit tests for the payment module.
  In this conversation they confirm the goal is done — 85% code coverage achieved this week.
  They also announce a new intention: write integration tests for the orders module in Q2.

Expected extraction (at minimum):
  - Completion evidence: EITHER intention(fulfilled) OR experience fact with completion signals
    (Ministral-3B often extracts completion as "experience" rather than intention(fulfilled))
  - 1+ "intention" with intention_status = "planning"   (new goal for Q2)
  - 1+ "experience" OR "world" fact
  - entity "payment" present in at least one fact
  - BONUS: transition_relation fulfilled_by on the fulfilled intention
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
USER: Last month I set a goal to write unit tests for the payment module.
ASSISTANT: How did that go?
USER: I finished it! Code coverage reached 85% this week. All the critical test cases pass.
ASSISTANT: That is excellent. 85% is a strong result for a critical module like payment.
USER: Thanks. I also plan to write integration tests for the orders module in Q2.
"""

_FAKE_RESPONSE = {
    "facts": [
        {
            "fact_type": "intention",
            "what": "User planned to write unit tests for the payment module",
            "entities": ["payment"],
            "intention_status": "fulfilled",
            "transition_relations": [
                {"target_index": 1, "transition_type": "fulfilled_by", "strength": 0.95}
            ],
        },
        {
            "fact_type": "experience",
            "what": "Payment module reached 85% code coverage this week with all critical test cases passing",
            "entities": ["payment"],
            "when": "this week",
            "fact_kind": "event",
        },
        {
            "fact_type": "intention",
            "what": "User plans to write integration tests for the orders module in Q2",
            "entities": ["orders"],
            "intention_status": "planning",
        },
    ]
}


async def run_test() -> None:
    from cogmem_api.engine.retain.fact_extraction import extract_facts_from_contents
    from cogmem_api.engine.retain.types import RetainContent

    content = RetainContent(
        content=DIALOGUE,
        context="goal_tracking",
        event_date=datetime(2026, 4, 17, 10, 0, tzinfo=UTC),
    )

    facts, _chunks, _usage = await extract_facts_from_contents(
        contents=[content],
        llm_config=resolve_llm(_FAKE_RESPONSE),
        agent_name="test",
        config=make_config("verbose"),
    )

    assert len(facts) >= 2, f"Expected at least 2 facts, got {len(facts)}"

    fact_types = {f.fact_type for f in facts}
    assert "intention" in fact_types, f"Missing 'intention' fact. Got: {fact_types}"
    assert "experience" in fact_types, f"Missing 'experience' fact. Got: {fact_types}"

    intention_facts = [f for f in facts if f.fact_type == "intention"]
    statuses = {f.metadata.get("intention_status") for f in intention_facts}

    # Completion evidence: fulfilled intention OR experience/world fact with completion signals
    # Ministral-3B often extracts "I finished it / 85% coverage" as experience, not intention(fulfilled)
    _COMPLETION_SIGNALS = {"85%", "coverage", "finished", "completed", "all the critical", "pass"}
    fulfilled_via_intention = "fulfilled" in statuses
    fulfilled_via_experience = any(
        any(s in f.fact_text.lower() for s in _COMPLETION_SIGNALS)
        for f in facts
        if f.fact_type in ("experience", "world")
    )
    assert fulfilled_via_intention or fulfilled_via_experience, (
        f"Expected a fulfilled intention OR a completion experience/world fact. "
        f"Statuses: {statuses}, "
        f"Non-intention facts: {[f.fact_text for f in facts if f.fact_type != 'intention']}"
    )
    if fulfilled_via_intention:
        print("OK  intention with status=fulfilled present")
    else:
        print("--  no fulfilled intention; completion evidence found in experience fact")

    assert "planning" in statuses, (
        f"Expected at least one intention with status 'planning'. Got: {statuses}"
    )

    all_entities = [e.lower() for f in facts for e in f.entities]
    assert any("payment" in e for e in all_entities), (
        f"Entity 'payment' not found. All entities: {all_entities}"
    )

    fulfilled = next(
        (f for f in intention_facts if f.metadata.get("intention_status") == "fulfilled"),
        None,
    )
    if fulfilled and fulfilled.transition_relations:
        tr = fulfilled.transition_relations[0]
        assert tr.transition_type == "fulfilled_by", (
            f"Expected transition_type='fulfilled_by', got {tr.transition_type!r}"
        )
        print("OK  transition_relation fulfilled_by present")
    else:
        print("--  no transition_relation (optional — skipped)")

    print("OK  intention with status=planning present")
    print("OK  experience fact present")
    print("OK  entity 'payment' found")


def main() -> None:
    asyncio.run(run_test())
    print("All intention lifecycle dialogue retain tests passed.")


if __name__ == "__main__":
    main()
