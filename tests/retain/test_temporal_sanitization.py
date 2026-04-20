"""Retain pipeline — temporal hallucination sanitization.

Verifies that CogMem's _sanitize_temporal_fact() clears today's ISO date
from `when`/`occurred_start`/`occurred_end` when the fact has no real
time context, and preserves fields when the fact does reference "today".

Scenarios:
  1. Hallucinated `when` (today's date, no time keyword) → cleared to "N/A"
  2. Hallucinated `occurred_start` (today's date, no time keyword) → cleared to None
  3. Real time context: `what` contains "today" → fields preserved
  4. ISO timestamp in `when` without time context → cleared to "N/A"

All checks run directly against _sanitize_temporal_fact() — no LLM needed.
"""

from __future__ import annotations

import sys
from datetime import date
from pathlib import Path
from typing import Any

_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))


def _get_sanitizer():
    from cogmem_api.engine.retain.fact_extraction import _sanitize_temporal_fact
    return _sanitize_temporal_fact


def test_hallucinated_when_cleared() -> None:
    """Today's date in `when` without time keywords → cleared to 'N/A'."""
    sanitize = _get_sanitizer()
    today = date.today().isoformat()

    payload: dict[str, Any] = {
        "fact_type": "experience",
        "what": "Alice joined the company",
        "when": today,
    }
    result = sanitize(payload)
    assert result["when"] == "N/A", (
        f"Expected 'when' to be cleared to 'N/A', got {result['when']!r}"
    )
    print(f"OK  [hallucinated_when] 'when' cleared: {today!r} -> 'N/A'")


def test_hallucinated_occurred_start_cleared() -> None:
    """Today's date in `occurred_start` without time keywords → cleared to None."""
    sanitize = _get_sanitizer()
    today = date.today().isoformat()

    payload: dict[str, Any] = {
        "fact_type": "experience",
        "what": "Bob completed the onboarding",
        "occurred_start": today,
        "occurred_end": today,
    }
    result = sanitize(payload)
    assert result["occurred_start"] is None, (
        f"Expected 'occurred_start' to be None, got {result['occurred_start']!r}"
    )
    assert result["occurred_end"] is None, (
        f"Expected 'occurred_end' to be None, got {result['occurred_end']!r}"
    )
    print(f"OK  [hallucinated_occurred] 'occurred_start'/'occurred_end' cleared")


def test_real_time_context_preserved() -> None:
    """When `what` contains 'today', temporal fields must NOT be cleared."""
    sanitize = _get_sanitizer()
    today = date.today().isoformat()

    payload: dict[str, Any] = {
        "fact_type": "experience",
        "what": "Alice met her manager today for the first time",
        "when": today,
        "occurred_start": today,
    }
    result = sanitize(payload)
    assert result["when"] == today, (
        f"Expected 'when' to be preserved as {today!r}, got {result['when']!r}"
    )
    assert result["occurred_start"] == today, (
        f"Expected 'occurred_start' to be preserved as {today!r}, got {result['occurred_start']!r}"
    )
    print(f"OK  [real_time_context] fields preserved when 'today' is in fact text")


def test_iso_timestamp_without_context_cleared() -> None:
    """ISO timestamp (with T and :) in `when` without time context → cleared to 'N/A'."""
    sanitize = _get_sanitizer()
    today = date.today().isoformat()

    payload: dict[str, Any] = {
        "fact_type": "experience",
        "what": "Carol deployed the new service",
        "when": f"{today}T14:32:00",
    }
    result = sanitize(payload)
    assert result["when"] == "N/A", (
        f"Expected ISO timestamp to be cleared to 'N/A', got {result['when']!r}"
    )
    print(f"OK  [iso_timestamp] ISO timestamp cleared without time context")


def test_past_date_unaffected() -> None:
    """A past date that is NOT today should not be cleared."""
    sanitize = _get_sanitizer()

    payload: dict[str, Any] = {
        "fact_type": "experience",
        "what": "Dave finished the migration",
        "when": "2025-12-01",
        "occurred_start": "2025-11-15",
    }
    result = sanitize(payload)
    assert result["when"] == "2025-12-01", (
        f"Past 'when' must not be cleared, got {result['when']!r}"
    )
    assert result["occurred_start"] == "2025-11-15", (
        f"Past 'occurred_start' must not be cleared, got {result['occurred_start']!r}"
    )
    print("OK  [past_date] past dates are not affected by sanitization")


def main() -> None:
    test_hallucinated_when_cleared()
    test_hallucinated_occurred_start_cleared()
    test_real_time_context_preserved()
    test_iso_timestamp_without_context_cleared()
    test_past_date_unaffected()
    print("\nAll temporal sanitization tests passed.")


if __name__ == "__main__":
    main()
