"""Retain pipeline — Dialogue: Researcher profile (world facts).

Scenario:
  Dr. Kim is a computational biology researcher at MIT who has published
  3 papers on protein folding. Clear, factual, no ambiguity — the LLM
  should reliably extract world facts.

Expected extraction (at minimum):
  - 2+ "world" facts
  - entity "Kim" or "MIT" present
  - no hallucinated temporal fields (Kim's role is timeless)

Difficulty: EASY — clear declarative facts, minimal inference required.
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
USER: Tell me about Dr. Kim.
ASSISTANT: Dr. Kim is a computational biology researcher at MIT.
USER: What has she published?
ASSISTANT: She has published 3 peer-reviewed papers on protein folding.
           Her most cited paper introduced a new graph-based folding model.
USER: What team does she lead?
ASSISTANT: Dr. Kim leads the Structural Genomics Lab at MIT, which has 8 members.
"""

_FAKE_RESPONSE = {
    "facts": [
        {
            "fact_type": "world",
            "what": "Dr. Kim is a computational biology researcher at MIT",
            "entities": ["Kim", "MIT"],
        },
        {
            "fact_type": "world",
            "what": "Dr. Kim has published 3 peer-reviewed papers on protein folding",
            "entities": ["Kim"],
        },
        {
            "fact_type": "world",
            "what": "Dr. Kim leads the Structural Genomics Lab at MIT with 8 members",
            "entities": ["Kim", "MIT", "Structural Genomics Lab"],
        },
    ]
}


async def run_test() -> None:
    from cogmem_api.engine.retain.fact_extraction import extract_facts_from_contents
    from cogmem_api.engine.retain.types import RetainContent

    content = RetainContent(
        content=DIALOGUE,
        context="researcher_profile",
        event_date=datetime(2026, 4, 20, 9, 0, tzinfo=UTC),
    )

    facts, _chunks, _usage = await extract_facts_from_contents(
        contents=[content],
        llm_config=resolve_llm(_FAKE_RESPONSE),
        agent_name="test",
        config=make_config("concise"),
    )

    world_facts = [f for f in facts if f.fact_type == "world"]
    assert len(world_facts) >= 2, (
        f"Expected at least 2 world facts, got {len(world_facts)}. "
        f"All types: {[f.fact_type for f in facts]}"
    )

    all_entities = [e.lower() for f in facts for e in f.entities]
    assert any(kw in e for e in all_entities for kw in ("kim", "mit")), (
        f"Expected entity 'Kim' or 'MIT', got: {all_entities}"
    )

    print(f"OK  {len(world_facts)} world fact(s) extracted")
    print("OK  entity Kim or MIT found")


def main() -> None:
    asyncio.run(run_test())
    print("All researcher profile dialogue retain tests passed.")


if __name__ == "__main__":
    main()
