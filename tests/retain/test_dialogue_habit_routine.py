"""Retain pipeline — Dialogue: Daily habit routine.

Scenario:
  The user describes their morning routine: always checks email before work,
  spending about 30 minutes every morning. Yesterday they handled 15 important emails.

Expected extraction (at minimum):
  - 1+ "habit"      : checks email before work every morning
  - 1+ "experience" : processed 15 emails yesterday (specific past event)
  - habit fact text contains a repetition keyword (always / every / routine)
  - all facts have raw_snippet set (lossless metadata)
"""

from __future__ import annotations

import asyncio
import re
import sys
from datetime import UTC, datetime
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from tests.retain._shared import make_config, resolve_llm  # noqa: E402

DIALOGUE = """\
USER: I always check my email before starting the workday.
ASSISTANT: That is a solid habit. How long do you usually spend on it?
USER: About 30 minutes every morning. Yesterday I handled 15 important emails.
ASSISTANT: Impressive. Sounds like you manage your inbox very efficiently.
USER: Yes, I also usually sort emails by priority every morning before diving into work.
"""

_FAKE_RESPONSE = {
    "facts": [
        {
            "fact_type": "habit",
            "what": "User always checks email before starting the workday, spending about 30 minutes every morning",
            "entities": [],
        },
        {
            "fact_type": "habit",
            "what": "User usually sorts emails by priority every morning before starting work",
            "entities": [],
        },
        {
            "fact_type": "experience",
            "what": "User handled 15 important emails yesterday",
            "entities": [],
            "when": "yesterday",
            "fact_kind": "event",
        },
    ]
}

_HABIT_KEYWORDS = re.compile(
    r"\b(always|usually|every\s+\w+|routine|habit|tends\s+to)\b",
    re.IGNORECASE,
)


async def run_test() -> None:
    from cogmem_api.engine.retain.fact_extraction import extract_facts_from_contents
    from cogmem_api.engine.retain.types import RetainContent

    content = RetainContent(
        content=DIALOGUE,
        context="daily_routine",
        event_date=datetime(2026, 4, 17, 8, 0, tzinfo=UTC),
    )

    facts, _chunks, _usage = await extract_facts_from_contents(
        contents=[content],
        llm_config=resolve_llm(_FAKE_RESPONSE),
        agent_name="test",
        config=make_config("concise"),
    )

    assert len(facts) >= 2, f"Expected at least 2 facts, got {len(facts)}"

    fact_types = {f.fact_type for f in facts}
    assert "habit" in fact_types, f"Missing 'habit' fact. Got: {fact_types}"
    assert "experience" in fact_types, f"Missing 'experience' fact. Got: {fact_types}"

    habit_facts = [f for f in facts if f.fact_type == "habit"]
    found_keyword = any(_HABIT_KEYWORDS.search(f.fact_text) for f in habit_facts)
    assert found_keyword, (
        f"Habit fact should contain a repetition keyword. "
        f"Texts: {[f.fact_text for f in habit_facts]}"
    )

    for f in facts:
        assert f.raw_snippet, f"raw_snippet missing on fact: {f.fact_text!r}"

    print("OK  habit fact present")
    print("OK  experience fact present")
    print("OK  habit fact contains repetition keyword")
    print("OK  all facts have raw_snippet")


def main() -> None:
    asyncio.run(run_test())
    print("All habit routine dialogue retain tests passed.")


if __name__ == "__main__":
    main()
