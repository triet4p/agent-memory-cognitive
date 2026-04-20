"""Retain pipeline — Dialogue: Abandoned intention lifecycle.

Scenario:
  Henry had planned to migrate the database to CockroachDB, but the plan
  was abandoned due to licensing costs. The abandonment is explicit.

Expected extraction (at minimum):
  - 1+ "intention" fact
  - At least one intention has intention_status == "abandoned"
    OR the word "abandoned"/"cancelled"/"dropped" appears in a world/experience fact

Difficulty: HARD — abandoned intentions require the LLM to infer negative status
  from context. Ministral-3B may return "planning" instead of "abandoned".
  Test accepts either a correct intention OR a world/experience fact mentioning
  the abandonment — at least one must capture the outcome.
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
USER: Henry, what happened with the CockroachDB migration plan?
HENRY: We had planned to migrate the main database to CockroachDB for better horizontal scaling.
USER: Did it go through?
HENRY: No, we abandoned the plan after discovering the enterprise licensing cost was too high.
       The project was cancelled three weeks ago. We are sticking with PostgreSQL.
"""

_FAKE_RESPONSE = {
    "facts": [
        {
            "fact_type": "intention",
            "what": "Henry's team planned to migrate the main database to CockroachDB for horizontal scaling",
            "entities": ["Henry", "CockroachDB"],
            "intention_status": "abandoned",
        },
        {
            "fact_type": "world",
            "what": "The CockroachDB migration was abandoned due to high enterprise licensing costs",
            "entities": ["CockroachDB"],
        },
    ]
}

_ABANDONMENT_SIGNALS = frozenset({"abandon", "cancel", "drop", "abort", "gave up", "scrapped"})


async def run_test() -> None:
    from cogmem_api.engine.retain.fact_extraction import extract_facts_from_contents
    from cogmem_api.engine.retain.types import RetainContent

    content = RetainContent(
        content=DIALOGUE,
        context="abandoned_plan",
        event_date=datetime(2026, 4, 20, 10, 0, tzinfo=UTC),
    )

    facts, _chunks, _usage = await extract_facts_from_contents(
        contents=[content],
        llm_config=resolve_llm(_FAKE_RESPONSE),
        agent_name="test",
        config=make_config("concise"),
    )

    assert len(facts) >= 1, f"Expected at least 1 fact, got 0"

    # Check 1: abandoned intention_status
    abandoned_intentions = [
        f for f in facts
        if f.fact_type == "intention"
        and (f.metadata or {}).get("intention_status") == "abandoned"
    ]

    # Check 2: any fact mentioning abandonment
    abandonment_in_text = [
        f for f in facts
        if any(sig in f.fact_text.lower() for sig in _ABANDONMENT_SIGNALS)
    ]

    assert abandoned_intentions or abandonment_in_text, (
        f"No evidence of abandonment found. "
        f"Intentions: {[(f.fact_text, (f.metadata or {}).get('intention_status')) for f in facts if f.fact_type == 'intention']}. "
        f"All facts: {[f.fact_text[:60] for f in facts]}"
    )

    if abandoned_intentions:
        print(f"OK  {len(abandoned_intentions)} intention(s) correctly marked 'abandoned'")
    else:
        print(f"OK  abandonment captured in world/experience fact text (acceptable fallback)")


def main() -> None:
    asyncio.run(run_test())
    print("All abandoned intention dialogue retain tests passed.")


if __name__ == "__main__":
    main()
