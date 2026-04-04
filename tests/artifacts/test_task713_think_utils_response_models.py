from __future__ import annotations

import sys
from datetime import datetime
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from cogmem_api.engine.response_models import DispositionTraits, MemoryFact
from cogmem_api.engine.search.think_utils import format_entity_summaries_for_prompt, format_facts_for_prompt


class _Observation:
    def __init__(self, text: str) -> None:
        self.text = text


class _EntityState:
    def __init__(self, observations: list[_Observation]) -> None:
        self.observations = observations


def assert_disposition_traits_contract() -> None:
    neutral = DispositionTraits()
    assert neutral.skepticism == 3
    assert neutral.literalism == 3
    assert neutral.empathy == 3

    try:
        DispositionTraits(skepticism=6)
    except ValueError:
        pass
    else:
        raise AssertionError("DispositionTraits must reject out-of-range values")


def assert_memory_fact_formatting_contract() -> None:
    fact = MemoryFact(
        id="fact-1",
        text="Alice accepted the proposal",
        fact_type="world",
        context="meeting room",
        occurred_start=datetime(2026, 4, 4, 8, 30, 0),
    )
    payload = format_facts_for_prompt([fact])

    assert '"text": "Alice accepted the proposal"' in payload
    assert '"context": "meeting room"' in payload
    assert '"occurred_start": "2026-04-04 08:30:00"' in payload


def assert_entity_summary_contract() -> None:
    entities = {
        "Alice": _EntityState([_Observation("Alice is detail-oriented")]),
        "Bob": {"observations": [{"text": "Bob prefers async updates"}]},
    }
    summary = format_entity_summaries_for_prompt(entities)

    assert "## Alice" in summary
    assert "Alice is detail-oriented" in summary
    assert "## Bob" in summary
    assert "Bob prefers async updates" in summary


def main() -> None:
    assert_disposition_traits_contract()
    assert_memory_fact_formatting_contract()
    assert_entity_summary_contract()
    print("Task 713 think_utils/response_models checks passed.")


if __name__ == "__main__":
    main()
