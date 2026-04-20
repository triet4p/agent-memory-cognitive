"""Retain pipeline — Dialogue: Code refactoring with measurable outcome (action_effect).

Scenario:
  Frank refactored the payment service by extracting a shared retry module.
  The action had a clear precondition (duplicate retry logic), a specific action
  (extraction + abstraction), and a measurable outcome (30% code reduction).

Expected extraction (at minimum):
  - 1+ "action_effect" fact
  - metadata has precondition, action, outcome
  - confidence ∈ [0, 1]

Difficulty: MEDIUM — explicit cause-effect with a quantified outcome.
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
USER: Frank, can you walk me through the payment service refactor you did last sprint?
FRANK: Sure. The payment service had duplicate retry logic spread across four modules.
       I extracted it into a shared RetryManager class.
USER: What was the result?
FRANK: We reduced total lines of code by about 30% and the retry behavior is now
       consistent across all payment flows. No more silent failures either.
"""

_FAKE_RESPONSE = {
    "facts": [
        {
            "fact_type": "action_effect",
            "what": "Frank extracted duplicate retry logic from the payment service into a shared RetryManager class, reducing code by 30% and eliminating silent failures",
            "entities": ["Frank", "RetryManager", "payment service"],
            "precondition": "Duplicate retry logic spread across four payment service modules",
            "action": "Extracted retry logic into a shared RetryManager class",
            "outcome": "30% reduction in code and consistent retry behavior across all payment flows",
            "confidence": 0.9,
        },
    ]
}


async def run_test() -> None:
    from cogmem_api.engine.retain.fact_extraction import extract_facts_from_contents
    from cogmem_api.engine.retain.types import RetainContent

    content = RetainContent(
        content=DIALOGUE,
        context="payment_refactor",
        event_date=datetime(2026, 4, 20, 10, 0, tzinfo=UTC),
    )

    facts, _chunks, _usage = await extract_facts_from_contents(
        contents=[content],
        llm_config=resolve_llm(_FAKE_RESPONSE),
        agent_name="test",
        config=make_config("concise"),
    )

    ae_facts = [f for f in facts if f.fact_type == "action_effect"]
    assert len(ae_facts) >= 1, (
        f"Expected at least 1 action_effect fact, got {len(ae_facts)}. "
        f"All types: {[f.fact_type for f in facts]}"
    )

    for f in ae_facts:
        meta = f.metadata or {}
        for field in ("precondition", "action", "outcome"):
            assert field in meta, f"Missing '{field}' in metadata: {meta}"
        conf = meta.get("confidence")
        if conf is not None:
            assert 0.0 <= float(conf) <= 1.0, f"confidence out of range: {conf!r}"

    print(f"OK  {len(ae_facts)} action_effect fact(s) extracted")
    print("OK  precondition / action / outcome all present")
    print("OK  confidence in valid range [0, 1]")


def main() -> None:
    asyncio.run(run_test())
    print("All refactoring outcome dialogue retain tests passed.")


if __name__ == "__main__":
    main()
