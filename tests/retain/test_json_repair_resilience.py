"""Retain pipeline — JSON repair resilience.

Verifies that CogMem's parse_llm_json() (with json_repair fallback) can recover
facts from malformed/truncated SLM output that the server no longer pre-repairs.

Scenarios:
  1. Truncated JSON — missing closing brackets  ]}
  2. Trailing comma in facts array
  3. Unquoted fact_type value

All cases must still yield at least 1 valid fact.
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


class _RawStringLLM:
    """FakeLLM that returns a raw string (not a dict) to exercise parse_llm_json."""

    def __init__(self, raw: str) -> None:
        self._raw = raw

    async def call(self, messages: list[dict[str, Any]], **kwargs: Any) -> Any:
        from cogmem_api.engine.response_models import TokenUsage
        return self._raw, TokenUsage(input_tokens=50, output_tokens=30, total_tokens=80)


DIALOGUE = "Alice works as a Data Scientist at OpenAI and recently completed the GPT-5 evaluation."

# --- Scenario 1: truncated — missing closing  ]}
_TRUNCATED = (
    '{"facts": [{"fact_type": "world", "what": "Alice works as Data Scientist at OpenAI", '
    '"entities": ["Alice", "OpenAI"]'
    # deliberately cut off here — no closing }]}
)

# --- Scenario 2: trailing comma after last fact
_TRAILING_COMMA = (
    '{"facts": ['
    '{"fact_type": "world", "what": "Alice works at OpenAI", "entities": ["Alice", "OpenAI"]},'
    '{"fact_type": "experience", "what": "Alice completed GPT-5 evaluation", "entities": ["Alice"]},'
    ']}'
)

# --- Scenario 3: unquoted fact_type value (common SLM mistake)
_UNQUOTED_TYPE = (
    '{"facts": [{"fact_type": world, "what": "Alice is a Data Scientist", "entities": ["Alice"]}]}'
)


async def run_scenario(label: str, raw: str) -> None:
    from cogmem_api.engine.retain.fact_extraction import extract_facts_from_contents
    from cogmem_api.engine.retain.types import RetainContent

    content = RetainContent(
        content=DIALOGUE,
        context="test_json_repair",
        event_date=datetime(2026, 4, 20, 10, 0, tzinfo=UTC),
    )

    facts, _chunks, _usage = await extract_facts_from_contents(
        contents=[content],
        llm_config=_RawStringLLM(raw),
        agent_name="test",
        config=make_config("concise"),
    )

    assert len(facts) >= 1, (
        f"[{label}] Expected at least 1 fact after json_repair, got 0. "
        f"Raw input: {raw[:80]}..."
    )
    print(f"OK  [{label}] {len(facts)} fact(s) recovered from malformed JSON")


async def run_test() -> None:
    await run_scenario("truncated", _TRUNCATED)
    await run_scenario("trailing_comma", _TRAILING_COMMA)
    await run_scenario("unquoted_type", _UNQUOTED_TYPE)


def main() -> None:
    asyncio.run(run_test())
    print("All json-repair resilience tests passed.")


if __name__ == "__main__":
    main()
