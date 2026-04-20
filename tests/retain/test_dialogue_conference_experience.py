"""Retain pipeline — Dialogue: Conference attendance (experience with explicit date).

Scenario:
  The user attended NeurIPS in December 2025 and gave a talk there.
  Clear past event with an explicit month/year reference.

Expected extraction (at minimum):
  - 1+ "experience" fact
  - experience fact has `when` field referencing "December 2025" or "NeurIPS" context
  - entity "NeurIPS" present

Difficulty: EASY — past event with explicit temporal anchor.
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
USER: I attended NeurIPS in December 2025 and it was an amazing experience.
ASSISTANT: That sounds great! Did you present any work?
USER: Yes, I gave a talk on sparse attention mechanisms. The room was packed.
ASSISTANT: Impressive. Did you network with other researchers?
USER: I met several key researchers there and got valuable feedback on my paper.
"""

_FAKE_RESPONSE = {
    "facts": [
        {
            "fact_type": "experience",
            "what": "User attended NeurIPS in December 2025 and gave a talk on sparse attention mechanisms",
            "entities": ["NeurIPS"],
            "when": "December 2025",
            "fact_kind": "event",
        },
        {
            "fact_type": "experience",
            "what": "User met key researchers at NeurIPS and received feedback on their paper",
            "entities": ["NeurIPS"],
            "when": "December 2025",
            "fact_kind": "event",
        },
    ]
}


async def run_test() -> None:
    from cogmem_api.engine.retain.fact_extraction import extract_facts_from_contents
    from cogmem_api.engine.retain.types import RetainContent

    content = RetainContent(
        content=DIALOGUE,
        context="conference_experience",
        event_date=datetime(2026, 4, 20, 9, 0, tzinfo=UTC),
    )

    facts, _chunks, _usage = await extract_facts_from_contents(
        contents=[content],
        llm_config=resolve_llm(_FAKE_RESPONSE),
        agent_name="test",
        config=make_config("concise"),
    )

    exp_facts = [f for f in facts if f.fact_type == "experience"]
    assert len(exp_facts) >= 1, (
        f"Expected at least 1 experience fact, got {len(exp_facts)}. "
        f"All types: {[f.fact_type for f in facts]}"
    )

    all_entities = [e.lower() for f in facts for e in f.entities]
    all_texts = [f.fact_text.lower() for f in facts]
    assert (
        any("neurips" in e for e in all_entities)
        or any("neurips" in t for t in all_texts)
    ), (
        f"'NeurIPS' not found in entities or fact text. "
        f"Entities: {all_entities}. Texts: {[t[:60] for t in all_texts]}"
    )

    # when field should not be today's date (temporal sanitization check)
    from datetime import date
    today = date.today().isoformat()
    for f in exp_facts:
        meta = f.metadata or {}
        when_val = str(meta.get("when", ""))
        assert today not in when_val, (
            f"Temporal hallucination detected: 'when' = {when_val!r} contains today's date"
        )

    print(f"OK  {len(exp_facts)} experience fact(s) extracted")
    print("OK  entity NeurIPS found")
    print("OK  no temporal hallucination in experience facts")


def main() -> None:
    asyncio.run(run_test())
    print("All conference experience dialogue retain tests passed.")


if __name__ == "__main__":
    main()
