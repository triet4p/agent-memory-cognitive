"""Unit test — action_effect metadata field completeness.

Verifies that every action_effect fact produced by the retain pipeline
has all three required fields: precondition, action, outcome.
Uses a FakeLLM that intentionally omits some fields to confirm the
fallback in _normalize_llm_facts() fills them with "N/A".

Difficulty: EASY (unit test, no real LLM needed)
"""

from __future__ import annotations

import asyncio
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from tests.retain._shared import make_config  # noqa: E402


class _PartialAEFakeLLM:
    """Returns action_effect facts with missing triplet fields to exercise fallback."""

    async def call(self, messages: list[dict[str, Any]], **kwargs: Any) -> Any:
        from cogmem_api.engine.response_models import TokenUsage
        return {
            "facts": [
                {
                    "fact_type": "action_effect",
                    "what": "Adding indexes to the users table sped up queries",
                    "entities": ["users table"],
                    # precondition, action, outcome intentionally omitted
                },
                {
                    "fact_type": "action_effect",
                    "what": "Disabling logging in production reduced overhead",
                    "entities": [],
                    "action": "Disabling logging in production",
                    # precondition and outcome omitted
                },
            ]
        }, TokenUsage(input_tokens=50, output_tokens=40, total_tokens=90)


DIALOGUE = """\
USER: We added indexes to the users table and queries became 10x faster.
ASSISTANT: That is a significant improvement.
USER: Yes, and we also disabled logging in production which reduced CPU overhead.
"""


async def run_test() -> None:
    from cogmem_api.engine.retain.fact_extraction import extract_facts_from_contents
    from cogmem_api.engine.retain.types import RetainContent

    content = RetainContent(
        content=DIALOGUE,
        context="ae_field_completeness",
        event_date=datetime(2026, 4, 20, 10, 0, tzinfo=UTC),
    )

    facts, _chunks, _usage = await extract_facts_from_contents(
        contents=[content],
        llm_config=_PartialAEFakeLLM(),
        agent_name="test",
        config=make_config("concise"),
    )

    ae_facts = [f for f in facts if f.fact_type == "action_effect"]
    assert len(ae_facts) >= 1, f"Expected at least 1 action_effect fact, got {len(ae_facts)}"

    for f in ae_facts:
        meta = f.metadata or {}
        assert "precondition" in meta, f"Missing 'precondition' in metadata: {meta}"
        assert "action" in meta, f"Missing 'action' in metadata: {meta}"
        assert "outcome" in meta, f"Missing 'outcome' in metadata: {meta}"
        print(f"OK  [{f.fact_text[:50]!r}] has precondition/action/outcome")


def main() -> None:
    asyncio.run(run_test())
    print("All action_effect field completeness tests passed.")


if __name__ == "__main__":
    main()
