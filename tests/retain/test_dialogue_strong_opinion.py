"""Retain pipeline — Dialogue: Strong technical opinion.

Scenario:
  Dave is a senior engineer who expresses a clear technical preference:
  he strongly believes TypeScript is better than JavaScript for large teams,
  and is lukewarm on microservices. Two opinions with different confidence signals.

Expected extraction (at minimum):
  - 1+ "opinion" fact
  - opinion about TypeScript/JavaScript present
  - confidence field present and in range [0, 1]

Difficulty: EASY-MEDIUM — opinions with explicit "I believe / I think" markers.
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
USER: What do you think about TypeScript vs JavaScript for a large engineering team?
DAVE: I strongly believe TypeScript is a far better choice for large teams.
      The static typing prevents whole classes of runtime errors before they reach production.
USER: What about microservices vs monoliths?
DAVE: I am somewhat skeptical of microservices for early-stage products.
      They add a lot of operational overhead before the team is ready to handle it.
"""

_FAKE_RESPONSE = {
    "facts": [
        {
            "fact_type": "opinion",
            "what": "Dave strongly believes TypeScript is better than JavaScript for large teams because static typing prevents runtime errors",
            "entities": ["Dave"],
            "confidence": 0.92,
        },
        {
            "fact_type": "opinion",
            "what": "Dave is skeptical of microservices for early-stage products due to operational overhead",
            "entities": ["Dave"],
            "confidence": 0.65,
        },
    ]
}


async def run_test() -> None:
    from cogmem_api.engine.retain.fact_extraction import extract_facts_from_contents
    from cogmem_api.engine.retain.types import RetainContent

    content = RetainContent(
        content=DIALOGUE,
        context="technical_opinions",
        event_date=datetime(2026, 4, 20, 10, 0, tzinfo=UTC),
    )

    facts, _chunks, _usage = await extract_facts_from_contents(
        contents=[content],
        llm_config=resolve_llm(_FAKE_RESPONSE),
        agent_name="test",
        config=make_config("concise"),
    )

    opinion_facts = [f for f in facts if f.fact_type == "opinion"]
    assert len(opinion_facts) >= 1, (
        f"Expected at least 1 opinion fact, got {len(opinion_facts)}. "
        f"All types: {[f.fact_type for f in facts]}"
    )

    _TS_KEYWORDS = ("typescript", "javascript", "type", "static")
    ts_opinion = next(
        (f for f in opinion_facts if any(kw in f.fact_text.lower() for kw in _TS_KEYWORDS)),
        None,
    )
    assert ts_opinion is not None, (
        f"No opinion about TypeScript/JavaScript found. "
        f"Opinion texts: {[f.fact_text for f in opinion_facts]}"
    )

    for f in opinion_facts:
        meta = f.metadata or {}
        conf = meta.get("confidence")
        if conf is not None:
            assert 0.0 <= float(conf) <= 1.0, (
                f"confidence out of range [0,1]: {conf!r} for fact {f.fact_text!r}"
            )

    print(f"OK  {len(opinion_facts)} opinion fact(s) extracted")
    print("OK  TypeScript/JavaScript opinion found")
    print("OK  confidence values in valid range [0, 1]")


def main() -> None:
    asyncio.run(run_test())
    print("All strong opinion dialogue retain tests passed.")


if __name__ == "__main__":
    main()
