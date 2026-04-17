"""Retain pipeline — Dialogue: New employee onboarding.

Scenario:
  Bob just joined TechVN last week as a Backend Engineer.
  He will work with Python and FastAPI, plans to learn Kubernetes in Q2,
  and thinks FastAPI is better than Django for microservices.

Expected extraction (at minimum):
  - 1+ "world"      : Bob's role / tech stack at TechVN
  - 1+ "experience" : Bob joined TechVN last week (specific past event)
  - 1+ "intention"  : Bob plans to learn Kubernetes in Q2
  - 1+ "opinion"    : Bob prefers FastAPI over Django
  - entity "TechVN" in at least one fact
  - entity "Bob" in at least one fact
  - intention fact has intention_status = "planning"
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
USER: Hi! I joined TechVN last week as a Backend Engineer.
ASSISTANT: Welcome to TechVN! What tech stack will you be working with?
USER: Mainly Python and FastAPI. I plan to learn Kubernetes in Q2 this year.
ASSISTANT: Great choice. FastAPI works really well for modern backend services.
USER: Agreed. I think FastAPI is better than Django for microservices — it is lighter and async-native.
"""

_FAKE_RESPONSE = {
    "facts": [
        {
            "fact_type": "world",
            "what": "Bob works as Backend Engineer at TechVN",
            "entities": ["Bob", "TechVN"],
        },
        {
            "fact_type": "experience",
            "what": "Bob joined TechVN last week",
            "entities": ["Bob", "TechVN"],
            "when": "last week",
            "fact_kind": "event",
        },
        {
            "fact_type": "world",
            "what": "Bob works with Python and FastAPI at TechVN",
            "entities": ["Bob", "Python", "FastAPI"],
        },
        {
            "fact_type": "intention",
            "what": "Bob plans to learn Kubernetes in Q2",
            "entities": ["Bob", "Kubernetes"],
            "intention_status": "planning",
        },
        {
            "fact_type": "opinion",
            "what": "Bob thinks FastAPI is better than Django for microservices because it is lighter and async-native",
            "entities": ["Bob", "FastAPI", "Django"],
            "confidence": 0.9,
        },
    ]
}


async def run_test() -> None:
    from cogmem_api.engine.retain.fact_extraction import extract_facts_from_contents
    from cogmem_api.engine.retain.types import RetainContent

    content = RetainContent(
        content=DIALOGUE,
        context="onboarding",
        event_date=datetime(2026, 4, 17, 9, 0, tzinfo=UTC),
    )

    facts, _chunks, usage = await extract_facts_from_contents(
        contents=[content],
        llm_config=resolve_llm(_FAKE_RESPONSE),
        agent_name="test",
        config=make_config("concise"),
    )

    assert len(facts) >= 4, f"Expected at least 4 facts, got {len(facts)}"

    fact_types = {f.fact_type for f in facts}
    assert "world" in fact_types, f"Missing 'world' fact. Got: {fact_types}"
    assert "experience" in fact_types, f"Missing 'experience' fact. Got: {fact_types}"
    assert "intention" in fact_types, f"Missing 'intention' fact. Got: {fact_types}"
    assert "opinion" in fact_types, f"Missing 'opinion' fact. Got: {fact_types}"

    all_entities = [e.lower() for f in facts for e in f.entities]
    assert any("techvn" in e for e in all_entities), \
        f"Entity 'TechVN' not found. All entities: {all_entities}"
    assert any("bob" in e for e in all_entities), \
        f"Entity 'Bob' not found. All entities: {all_entities}"

    for intention in [f for f in facts if f.fact_type == "intention"]:
        status = intention.metadata.get("intention_status")
        assert status == "planning", \
            f"intention_status should be 'planning', got: {status!r}"

    assert usage.total_tokens > 0, "Token usage should be tracked"

    print("OK  world fact present")
    print("OK  experience fact present")
    print("OK  intention fact with status=planning")
    print("OK  opinion fact present")
    print("OK  entities TechVN and Bob found")
    print("OK  token usage tracked")


def main() -> None:
    asyncio.run(run_test())
    print("All onboarding dialogue retain tests passed.")


if __name__ == "__main__":
    main()
