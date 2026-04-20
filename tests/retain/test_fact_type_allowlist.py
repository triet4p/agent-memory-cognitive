"""Unit test — unknown fact types are filtered out by the pipeline.

If the LLM returns a fact_type that is not in COGMEM_FACT_TYPES
(e.g. "skill", "preference", "trait"), those facts must be dropped
rather than stored with an invalid type.

Valid types: world, experience, opinion, habit, intention, action_effect

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

_VALID_TYPES = frozenset({"world", "experience", "opinion", "habit", "intention", "action_effect"})


class _InvalidTypeFakeLLM:
    """Returns a mix of valid and invalid fact types."""

    async def call(self, messages: list[dict[str, Any]], **kwargs: Any) -> Any:
        from cogmem_api.engine.response_models import TokenUsage
        return {
            "facts": [
                {
                    "fact_type": "world",
                    "what": "Carol is a senior engineer at DataCo",
                    "entities": ["Carol", "DataCo"],
                },
                {
                    "fact_type": "skill",
                    "what": "Carol is proficient in Python and Go",
                    "entities": ["Carol"],
                },
                {
                    "fact_type": "preference",
                    "what": "Carol prefers remote work",
                    "entities": ["Carol"],
                },
                {
                    "fact_type": "trait",
                    "what": "Carol is detail-oriented",
                    "entities": ["Carol"],
                },
            ]
        }, TokenUsage(input_tokens=60, output_tokens=50, total_tokens=110)


DIALOGUE = """\
USER: Carol is a senior engineer at DataCo. She is proficient in Python and Go,
      prefers remote work, and is known for being very detail-oriented.
"""


async def run_test() -> None:
    from cogmem_api.engine.retain.fact_extraction import extract_facts_from_contents
    from cogmem_api.engine.retain.types import RetainContent

    content = RetainContent(
        content=DIALOGUE,
        context="type_allowlist",
        event_date=datetime(2026, 4, 20, 10, 0, tzinfo=UTC),
    )

    facts, _chunks, _usage = await extract_facts_from_contents(
        contents=[content],
        llm_config=_InvalidTypeFakeLLM(),
        agent_name="test",
        config=make_config("concise"),
    )

    invalid = [f for f in facts if f.fact_type not in _VALID_TYPES]
    assert len(invalid) == 0, (
        f"Facts with invalid types must be filtered out. Found: "
        f"{[(f.fact_type, f.fact_text) for f in invalid]}"
    )

    valid = [f for f in facts if f.fact_type in _VALID_TYPES]
    assert len(valid) >= 1, f"Expected at least 1 valid fact to survive, got 0"
    print(f"OK  {len(valid)} valid fact(s) kept, {len(invalid)} invalid dropped")


def main() -> None:
    asyncio.run(run_test())
    print("All fact type allowlist tests passed.")


if __name__ == "__main__":
    main()
