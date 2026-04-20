"""Retain pipeline — Dialogue: action_effect with devalue_sensitive flag.

Scenario:
  Mia's team rolled back a feature flag after it caused a regression.
  The action_effect has a negative outcome that should devalue the original action
  if replayed — this is the devalue_sensitive pattern.

Expected extraction (at minimum):
  - 1+ "action_effect" fact
  - Ideal: devalue_sensitive == True in metadata
  - Fallback: action_effect fact present with rollback/regression language

Difficulty: HARD — devalue_sensitive requires LLM to recognize "bad outcome"
  semantics. Ministral-3B almost certainly will not set this flag.
  Test accepts action_effect present as minimum; devalue_sensitive is a bonus.
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
USER: Mia, what happened with the dark mode feature flag last week?
MIA: We enabled the dark mode flag for 20% of users on Monday.
     By Tuesday morning, crash reports spiked by 300%.
USER: What did you do?
MIA: We immediately rolled back the flag. Crashes returned to baseline within an hour.
     The lesson: never enable a flag on a weekday without a one-hour observation window first.
"""

_FAKE_RESPONSE = {
    "facts": [
        {
            "fact_type": "action_effect",
            "what": "Enabling the dark mode feature flag for 20% of users caused a 300% spike in crash reports, requiring an immediate rollback",
            "entities": ["Mia"],
            "precondition": "Dark mode feature flag was disabled",
            "action": "Enabled dark mode flag for 20% of users",
            "outcome": "Crash reports spiked by 300%; flag rolled back within 24 hours",
            "confidence": 0.95,
            "devalue_sensitive": True,
        },
    ]
}

_ROLLBACK_KEYWORDS = ("rollback", "roll back", "revert", "crash", "regression", "spike")


async def run_test() -> None:
    from cogmem_api.engine.retain.fact_extraction import extract_facts_from_contents
    from cogmem_api.engine.retain.types import RetainContent

    content = RetainContent(
        content=DIALOGUE,
        context="feature_flag_rollback",
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

    devalue_set = [
        f for f in ae_facts
        if (f.metadata or {}).get("devalue_sensitive") is True
    ]
    rollback_in_text = [
        f for f in ae_facts
        if any(kw in f.fact_text.lower() for kw in _ROLLBACK_KEYWORDS)
    ]

    assert devalue_set or rollback_in_text, (
        f"action_effect present but neither devalue_sensitive nor rollback language found. "
        f"Texts: {[f.fact_text[:80] for f in ae_facts]}"
    )

    if devalue_set:
        print(f"OK  devalue_sensitive=True correctly set on {len(devalue_set)} fact(s)")
    else:
        print("OK  rollback/regression language captured in action_effect (devalue_sensitive absent — acceptable for 3B)")


def main() -> None:
    asyncio.run(run_test())
    print("All devalue-sensitive dialogue retain tests passed.")


if __name__ == "__main__":
    main()
