"""Retain pipeline — Dialogue: Mixed fact types in a single conversation.

Scenario:
  Alice is an ML engineer at Anthropic working on the CogMem project.
  The conversation covers her role (world), a past deployment event (experience),
  a technical opinion (opinion), and a daily code review habit (habit).
  Tests that the pipeline correctly classifies all four types from one chunk.

Expected extraction (at minimum):
  - 1+ "world"      : Alice's role / project at Anthropic
  - 1+ "experience" : Alice deployed CogMem API to production in March 2026
  - 1+ "opinion"    : Alice's belief about knowledge graphs vs vector stores
  - 1+ "habit"      : Alice always reviews code before merging PRs
  - entity "Alice" present in at least one fact
  - entity "Anthropic" or "CogMem" present in at least one fact
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
USER: Alice, what do you do at Anthropic?
ALICE: I am an ML engineer at Anthropic, focused on memory systems for AI agents.
USER: What is your most recent project?
ALICE: In March 2026 I successfully deployed the CogMem API to production.
       It uses a knowledge graph to store long-term memory.
USER: Do you have a preference between knowledge graphs and vector stores?
ALICE: I believe knowledge graphs are better suited for long-term memory than vector stores
       because they preserve the relational structure between facts.
USER: What does your code review workflow look like?
ALICE: I always do a thorough code review before merging any PR. It usually takes about an hour a day.
"""

_FAKE_RESPONSE = {
    "facts": [
        {
            "fact_type": "world",
            "what": "Alice is an ML engineer at Anthropic, focused on memory systems for AI agents",
            "entities": ["Alice", "Anthropic"],
        },
        {
            "fact_type": "experience",
            "what": "Alice deployed CogMem API to production in March 2026",
            "entities": ["Alice", "CogMem"],
            "when": "March 2026",
            "fact_kind": "event",
        },
        {
            "fact_type": "world",
            "what": "CogMem API uses a knowledge graph for long-term memory storage",
            "entities": ["CogMem"],
        },
        {
            "fact_type": "opinion",
            "what": "Alice believes knowledge graphs are better suited than vector stores for long-term memory because they preserve relational structure",
            "entities": ["Alice"],
            "confidence": 0.85,
        },
        {
            "fact_type": "habit",
            "what": "Alice always does a thorough code review before merging any PR, spending about an hour a day",
            "entities": ["Alice"],
        },
    ]
}


async def run_test() -> None:
    from cogmem_api.engine.retain.fact_extraction import extract_facts_from_contents
    from cogmem_api.engine.retain.types import RetainContent

    content = RetainContent(
        content=DIALOGUE,
        context="mixed_types_conversation",
        event_date=datetime(2026, 4, 17, 11, 0, tzinfo=UTC),
    )

    facts, _chunks, _usage = await extract_facts_from_contents(
        contents=[content],
        llm_config=resolve_llm(_FAKE_RESPONSE),
        agent_name="test",
        config=make_config("verbose"),
    )

    assert len(facts) >= 4, f"Expected at least 4 facts, got {len(facts)}"

    fact_types = {f.fact_type for f in facts}
    assert "world" in fact_types, f"Missing 'world' fact. Got: {fact_types}"
    assert "experience" in fact_types, f"Missing 'experience' fact. Got: {fact_types}"
    assert "opinion" in fact_types, f"Missing 'opinion' fact. Got: {fact_types}"
    assert "habit" in fact_types, f"Missing 'habit' fact. Got: {fact_types}"

    all_entities = [e.lower() for f in facts for e in f.entities]
    assert any("alice" in e for e in all_entities), (
        f"Entity 'Alice' not found. All entities: {all_entities}"
    )
    assert any(kw in e for e in all_entities for kw in ("anthropic", "cogmem")), (
        f"Neither 'Anthropic' nor 'CogMem' found. All entities: {all_entities}"
    )

    print("OK  world fact present")
    print("OK  experience fact present")
    print("OK  opinion fact present")
    print("OK  habit fact present")
    print("OK  entity Alice found")
    print("OK  entity Anthropic or CogMem found")


def main() -> None:
    asyncio.run(run_test())
    print("All mixed-types dialogue retain tests passed.")


if __name__ == "__main__":
    main()
