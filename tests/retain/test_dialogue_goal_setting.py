"""Retain pipeline — Dialogue: Goal setting (intention).

Scenario:
  Eve explicitly states a future goal: she plans to earn her AWS Solutions
  Architect certification by the end of Q3 2026. Unambiguous future intention
  with a clear deadline.

Expected extraction (at minimum):
  - 1+ "intention" fact
  - intention_status == "planning"
  - entity "Eve" or "AWS" present

Difficulty: MEDIUM — clear future goal, but intention_status inference required.
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
USER: Eve, what are your professional goals for this year?
EVE: I plan to earn my AWS Solutions Architect certification by the end of Q3 2026.
     I have been studying for it on weekends.
USER: That is ambitious. Any other goals?
EVE: I also want to mentor two junior engineers on my team before the year is out.
"""

_FAKE_RESPONSE = {
    "facts": [
        {
            "fact_type": "intention",
            "what": "Eve plans to earn AWS Solutions Architect certification by end of Q3 2026",
            "entities": ["Eve", "AWS"],
            "intention_status": "planning",
        },
        {
            "fact_type": "intention",
            "what": "Eve wants to mentor two junior engineers on her team before year end",
            "entities": ["Eve"],
            "intention_status": "planning",
        },
        {
            "fact_type": "habit",
            "what": "Eve studies for AWS certification on weekends",
            "entities": ["Eve", "AWS"],
        },
    ]
}


async def run_test() -> None:
    from cogmem_api.engine.retain.fact_extraction import extract_facts_from_contents
    from cogmem_api.engine.retain.types import RetainContent

    content = RetainContent(
        content=DIALOGUE,
        context="goal_setting",
        event_date=datetime(2026, 4, 20, 9, 0, tzinfo=UTC),
    )

    facts, _chunks, _usage = await extract_facts_from_contents(
        contents=[content],
        llm_config=resolve_llm(_FAKE_RESPONSE),
        agent_name="test",
        config=make_config("concise"),
    )

    intent_facts = [f for f in facts if f.fact_type == "intention"]
    assert len(intent_facts) >= 1, (
        f"Expected at least 1 intention fact, got {len(intent_facts)}. "
        f"All types: {[f.fact_type for f in facts]}"
    )

    for f in intent_facts:
        meta = f.metadata or {}
        status = meta.get("intention_status")
        assert status is not None, f"intention_status missing on {f.fact_text!r}"
        assert status in ("planning", "fulfilled", "abandoned"), (
            f"intention_status must be planning|fulfilled|abandoned, got {status!r}"
        )

    planning_facts = [f for f in intent_facts if (f.metadata or {}).get("intention_status") == "planning"]
    assert len(planning_facts) >= 1, (
        f"Expected at least 1 'planning' intention. "
        f"Statuses: {[(f.metadata or {}).get('intention_status') for f in intent_facts]}"
    )

    all_entities = [e.lower() for f in facts for e in f.entities]
    assert any(kw in e for e in all_entities for kw in ("eve", "aws")), (
        f"Expected entity 'Eve' or 'AWS'. Got: {all_entities}"
    )

    print(f"OK  {len(intent_facts)} intention fact(s) extracted")
    print(f"OK  {len(planning_facts)} planning intention(s) found")
    print("OK  entity Eve or AWS found")


def main() -> None:
    asyncio.run(run_test())
    print("All goal setting dialogue retain tests passed.")


if __name__ == "__main__":
    main()
