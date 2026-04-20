"""Retain pipeline — Dialogue: Opinions with different confidence signals.

Scenario:
  Lena expresses three opinions with different certainty levels:
    - Strong certainty: "I am absolutely convinced..."  → confidence near 1.0
    - Moderate:         "I tend to think..."            → confidence ~0.6-0.8
    - Tentative:        "I am not sure, but maybe..."   → confidence ≤ 0.5

Expected extraction (at minimum):
  - 2+ opinion facts
  - High-confidence opinion has confidence > 0.7 (if field present)
  - Low-confidence opinion has confidence ≤ 0.7 (if field present)
  - OR: at least 2 opinions present (confidence field may be absent on SLM output)

Difficulty: HARD — confidence calibration from hedging language. Ministral-3B
  may assign uniform confidence or omit the field entirely.
  Test is lenient: only validates range [0,1] if field is present.
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
USER: Lena, what do you think about event sourcing?
LENA: I am absolutely convinced that event sourcing is the right architecture
      for any system that needs a complete audit trail. No doubts there.
USER: What about eventual consistency?
LENA: I tend to think eventual consistency is acceptable for read-heavy workloads,
      but I would not use it for financial transactions.
USER: Any thoughts on CQRS?
LENA: I am not entirely sure, but CQRS might be overkill for smaller teams.
      I have not seen enough evidence either way.
"""

_FAKE_RESPONSE = {
    "facts": [
        {
            "fact_type": "opinion",
            "what": "Lena is absolutely convinced that event sourcing is the right architecture for systems requiring a complete audit trail",
            "entities": ["Lena"],
            "confidence": 0.97,
        },
        {
            "fact_type": "opinion",
            "what": "Lena tends to think eventual consistency is acceptable for read-heavy workloads but not for financial transactions",
            "entities": ["Lena"],
            "confidence": 0.7,
        },
        {
            "fact_type": "opinion",
            "what": "Lena thinks CQRS might be overkill for smaller teams but is uncertain",
            "entities": ["Lena"],
            "confidence": 0.4,
        },
    ]
}


async def run_test() -> None:
    from cogmem_api.engine.retain.fact_extraction import extract_facts_from_contents
    from cogmem_api.engine.retain.types import RetainContent

    content = RetainContent(
        content=DIALOGUE,
        context="confidence_gradient",
        event_date=datetime(2026, 4, 20, 10, 0, tzinfo=UTC),
    )

    facts, _chunks, _usage = await extract_facts_from_contents(
        contents=[content],
        llm_config=resolve_llm(_FAKE_RESPONSE),
        agent_name="test",
        config=make_config("concise"),
    )

    opinion_facts = [f for f in facts if f.fact_type == "opinion"]
    assert len(opinion_facts) >= 2, (
        f"Expected at least 2 opinion facts, got {len(opinion_facts)}. "
        f"All types: {[f.fact_type for f in facts]}"
    )

    for f in opinion_facts:
        meta = f.metadata or {}
        conf = meta.get("confidence")
        if conf is not None:
            assert 0.0 <= float(conf) <= 1.0, (
                f"confidence out of range [0,1]: {conf!r} for {f.fact_text!r}"
            )

    print(f"OK  {len(opinion_facts)} opinion(s) extracted")

    confidences = [float((f.metadata or {}).get("confidence", -1)) for f in opinion_facts if (f.metadata or {}).get("confidence") is not None]
    if len(confidences) >= 2:
        high = max(confidences)
        low = min(confidences)
        if high > low:
            print(f"OK  confidence gradient detected: max={high:.2f} min={low:.2f}")
        else:
            print(f"NOTE  uniform confidence={high:.2f} (acceptable for 3B model)")
    else:
        print("NOTE  confidence field absent (acceptable for 3B model)")


def main() -> None:
    asyncio.run(run_test())
    print("All confidence gradient dialogue retain tests passed.")


if __name__ == "__main__":
    main()
