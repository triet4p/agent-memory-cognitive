"""Shared prompt components used by both Pass 1 and Pass 2.

Contains constants and helper functions that are reused across
retain extraction prompts.
"""

from __future__ import annotations

from typing import Any


def sanitize_temporal_fact(payload: dict[str, Any]) -> dict[str, Any]:
    """Clear hallucinated dates from a single fact payload.

    SLMs often fill 'when'/'occurred_start'/'occurred_end' with today's date
    when no real time context exists.  We detect this and reset those fields.
    World facts are time-independent by definition — always strip temporal fields.
    """
    from datetime import date

    if str(payload.get("fact_type", "")).lower() == "world":
        payload["when"] = None
        payload["occurred_start"] = None
        payload["occurred_end"] = None
        return payload

    today_prefix = date.today().isoformat()
    what_lower = str(payload.get("what", "")).lower()
    has_real_time_context = any(kw in what_lower for kw in _TODAY_TIME_KEYWORDS)

    if not has_real_time_context:
        for field in ("occurred_start", "occurred_end"):
            val = str(payload.get(field, ""))
            if today_prefix in val:
                payload[field] = None

        when_val = str(payload.get("when", ""))
        if today_prefix in when_val:
            payload["when"] = "N/A"
        if "T" in when_val and ":" in when_val:
            payload["when"] = "N/A"

    return payload


_TODAY_TIME_KEYWORDS = frozenset(
    {"today", "now", "current", "this morning", "at this moment", "currently"}
)