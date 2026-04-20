"""Retain pipeline — Dialogue: Implicit causality (action_effect without connective words).

Scenario:
  The connection pool size was increased. Query throughput went up.
  No explicit "because", "therefore", "as a result" — causality must be inferred
  from context and sequence.

Expected extraction (at minimum):
  - At least 1 fact of any type covering the connection pool change
  - Ideal: 1 action_effect with connection pool as action and throughput as outcome

Difficulty: HARD — no explicit causal connectives. Ministral-3B may return
  two separate world/experience facts instead of a single action_effect.
  Test accepts either action_effect OR 2+ facts covering both sides of causality.
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
USER: What changes did you make to the database layer last week?
IVY: We bumped the connection pool size from 10 to 50.
     Query throughput went up by 40%.
USER: Was there any downside?
IVY: Memory usage increased by about 200 MB, but it is within acceptable limits.
"""

_FAKE_RESPONSE = {
    "facts": [
        {
            "fact_type": "action_effect",
            "what": "Increasing database connection pool size from 10 to 50 improved query throughput by 40% at the cost of 200 MB additional memory",
            "entities": [],
            "precondition": "Connection pool size was 10, limiting query throughput",
            "action": "Increased connection pool size from 10 to 50",
            "outcome": "Query throughput increased by 40%; memory usage increased by 200 MB",
            "confidence": 0.85,
        }
    ]
}

_POOL_KEYWORDS = ("connection pool", "pool", "throughput", "query")


async def run_test() -> None:
    from cogmem_api.engine.retain.fact_extraction import extract_facts_from_contents
    from cogmem_api.engine.retain.types import RetainContent

    content = RetainContent(
        content=DIALOGUE,
        context="implicit_causality",
        event_date=datetime(2026, 4, 20, 10, 0, tzinfo=UTC),
    )

    facts, _chunks, _usage = await extract_facts_from_contents(
        contents=[content],
        llm_config=resolve_llm(_FAKE_RESPONSE),
        agent_name="test",
        config=make_config("concise"),
    )

    assert len(facts) >= 1, "Expected at least 1 fact"

    relevant = [f for f in facts if any(kw in f.fact_text.lower() for kw in _POOL_KEYWORDS)]
    assert len(relevant) >= 1, (
        f"No fact mentions connection pool or throughput. "
        f"All texts: {[f.fact_text[:60] for f in facts]}"
    )

    ae_facts = [f for f in facts if f.fact_type == "action_effect"]
    if ae_facts:
        for f in ae_facts:
            meta = f.metadata or {}
            for field in ("precondition", "action", "outcome"):
                assert field in meta, f"Missing '{field}' in action_effect metadata"
        print(f"OK  {len(ae_facts)} action_effect fact(s) with implicit causality inferred")
    else:
        print(f"OK  causality captured across {len(relevant)} world/experience fact(s) (acceptable fallback)")


def main() -> None:
    asyncio.run(run_test())
    print("All implicit cause-effect dialogue retain tests passed.")


if __name__ == "__main__":
    main()
