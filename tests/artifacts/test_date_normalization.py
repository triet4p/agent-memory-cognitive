"""Tests for normalize_dates_in_fact_text — date normalization post-processor.

Verifies that absolute dates in fact_text within ±7 days of today are replaced
with relative labels (today/yesterday/past week/tomorrow/next week), and that
dates outside that window are left unchanged.
"""

from __future__ import annotations

import sys
from datetime import date, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from cogmem_api.engine.retain.fact_extraction import normalize_dates_in_fact_text

TODAY = date.today()


def d(delta: int) -> date:
    return TODAY + timedelta(days=delta)


def iso(delta: int) -> str:
    return d(delta).isoformat()


# ---------------------------------------------------------------------------
# ISO 8601 format
# ---------------------------------------------------------------------------

def test_iso_today():
    text = f"User attended service on {iso(0)}"
    result = normalize_dates_in_fact_text(text, today=TODAY)
    assert "today" in result, f"Expected 'today' in: {result}"
    assert iso(0) not in result


def test_iso_yesterday():
    text = f"User went to the gym on {iso(-1)}"
    result = normalize_dates_in_fact_text(text, today=TODAY)
    assert "yesterday" in result, f"Expected 'yesterday' in: {result}"


def test_iso_3_days_ago():
    text = f"User cooked dinner on {iso(-3)}"
    result = normalize_dates_in_fact_text(text, today=TODAY)
    assert "past week" in result, f"Expected 'past week' in: {result}"


def test_iso_7_days_ago_boundary():
    text = f"User planted seeds on {iso(-7)}"
    result = normalize_dates_in_fact_text(text, today=TODAY)
    assert "past week" in result, f"Expected 'past week' at -7 boundary: {result}"


def test_iso_8_days_ago_unchanged():
    text = f"User visited friend on {iso(-8)}"
    result = normalize_dates_in_fact_text(text, today=TODAY)
    assert iso(-8) in result, f"Date -8 days should be unchanged: {result}"
    assert "past week" not in result


def test_iso_tomorrow():
    text = f"User has appointment on {iso(1)}"
    result = normalize_dates_in_fact_text(text, today=TODAY)
    assert "tomorrow" in result, f"Expected 'tomorrow' in: {result}"


def test_iso_3_days_future():
    text = f"User plans to travel on {iso(3)}"
    result = normalize_dates_in_fact_text(text, today=TODAY)
    assert "next week" in result, f"Expected 'next week' in: {result}"


def test_iso_7_days_future_boundary():
    text = f"User meeting on {iso(7)}"
    result = normalize_dates_in_fact_text(text, today=TODAY)
    assert "next week" in result, f"Expected 'next week' at +7 boundary: {result}"


def test_iso_8_days_future_unchanged():
    text = f"User plans vacation on {iso(8)}"
    result = normalize_dates_in_fact_text(text, today=TODAY)
    assert iso(8) in result, f"Date +8 days should be unchanged: {result}"
    assert "next week" not in result


def test_iso_far_past_unchanged():
    old_date = "2023-04-06"
    text = f"User attended Maundy Thursday service on {old_date}"
    result = normalize_dates_in_fact_text(text, today=TODAY)
    assert old_date in result, f"Old date should be unchanged: {result}"


# ---------------------------------------------------------------------------
# ISO 8601 with time component
# ---------------------------------------------------------------------------

def test_iso_datetime_with_time():
    dt_str = d(0).isoformat() + "T14:30:00Z"
    text = f"User logged in at {dt_str}"
    result = normalize_dates_in_fact_text(text, today=TODAY)
    assert "today" in result, f"ISO datetime should resolve to 'today': {result}"
    assert dt_str not in result


def test_iso_datetime_with_offset():
    dt_str = d(-1).isoformat() + "T08:00:00+07:00"
    text = f"User woke up at {dt_str}"
    result = normalize_dates_in_fact_text(text, today=TODAY)
    assert "yesterday" in result, f"ISO datetime+offset should resolve to 'yesterday': {result}"


# ---------------------------------------------------------------------------
# Named month MDY format
# ---------------------------------------------------------------------------

def test_named_month_mdy_full():
    month_names = [
        "January", "February", "March", "April", "May", "June",
        "July", "August", "September", "October", "November", "December"
    ]
    target = d(0)
    month_str = month_names[target.month - 1]
    date_str = f"{month_str} {target.day}, {target.year}"
    text = f"User attended event on {date_str}"
    result = normalize_dates_in_fact_text(text, today=TODAY)
    assert "today" in result, f"Named month full MDY should resolve: {result}"


def test_named_month_mdy_abbreviated():
    abbr = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
            "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    target = d(-1)
    month_str = abbr[target.month - 1]
    date_str = f"{month_str} {target.day}, {target.year}"
    text = f"User baked cake on {date_str}"
    result = normalize_dates_in_fact_text(text, today=TODAY)
    assert "yesterday" in result, f"Named month abbreviated MDY should resolve: {result}"


def test_named_month_mdy_no_comma():
    abbr = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
            "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    target = d(1)
    month_str = abbr[target.month - 1]
    date_str = f"{month_str} {target.day} {target.year}"
    text = f"User has interview {date_str}"
    result = normalize_dates_in_fact_text(text, today=TODAY)
    assert "tomorrow" in result, f"Named month no-comma MDY should resolve: {result}"


# ---------------------------------------------------------------------------
# Named month DMY format
# ---------------------------------------------------------------------------

def test_named_month_dmy_full():
    month_names = [
        "January", "February", "March", "April", "May", "June",
        "July", "August", "September", "October", "November", "December"
    ]
    target = d(-2)
    month_str = month_names[target.month - 1]
    date_str = f"{target.day} {month_str} {target.year}"
    text = f"User bought groceries on {date_str}"
    result = normalize_dates_in_fact_text(text, today=TODAY)
    assert "past week" in result, f"Named month DMY should resolve: {result}"


def test_named_month_dmy_abbreviated():
    abbr = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
            "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    target = d(2)
    month_str = abbr[target.month - 1]
    date_str = f"{target.day} {month_str} {target.year}"
    text = f"User dentist appointment {date_str}"
    result = normalize_dates_in_fact_text(text, today=TODAY)
    assert "next week" in result, f"Named month abbreviated DMY should resolve: {result}"


# ---------------------------------------------------------------------------
# US slash format MM/DD/YYYY
# ---------------------------------------------------------------------------

def test_us_slash_today():
    target = d(0)
    date_str = f"{target.month:02d}/{target.day:02d}/{target.year}"
    text = f"User signed contract on {date_str}"
    result = normalize_dates_in_fact_text(text, today=TODAY)
    assert "today" in result, f"US slash today should resolve: {result}"


def test_us_slash_yesterday():
    target = d(-1)
    date_str = f"{target.month}/{target.day}/{target.year}"
    text = f"User exercised on {date_str}"
    result = normalize_dates_in_fact_text(text, today=TODAY)
    assert "yesterday" in result, f"US slash yesterday should resolve: {result}"


def test_us_slash_far_past_unchanged():
    text = "User started job on 03/15/2020"
    result = normalize_dates_in_fact_text(text, today=TODAY)
    assert "03/15/2020" in result, f"Old US slash date should be unchanged: {result}"


# ---------------------------------------------------------------------------
# US dash format M-D-YYYY
# ---------------------------------------------------------------------------

def test_us_dash_today():
    target = d(0)
    date_str = f"{target.month}-{target.day}-{target.year}"
    text = f"User filed taxes on {date_str}"
    result = normalize_dates_in_fact_text(text, today=TODAY)
    assert "today" in result, f"US dash today should resolve: {result}"


def test_us_dash_does_not_corrupt_iso():
    # ISO date like 2023-04-06 should NOT be matched by us_dash (4-digit year first)
    old_iso = "2023-04-06"
    text = f"User attended service on {old_iso}"
    result = normalize_dates_in_fact_text(text, today=TODAY)
    assert old_iso in result, f"ISO far-past date must not be double-parsed: {result}"


# ---------------------------------------------------------------------------
# Edge cases
# ---------------------------------------------------------------------------

def test_no_date_unchanged():
    text = "User always checks email before standup"
    result = normalize_dates_in_fact_text(text, today=TODAY)
    assert result == text


def test_multiple_dates_only_recent_replaced():
    old_date = "2020-06-01"
    recent_date = iso(0)
    text = f"User started job on {old_date} and checked in {recent_date}"
    result = normalize_dates_in_fact_text(text, today=TODAY)
    assert old_date in result, f"Old date should remain: {result}"
    assert "today" in result, f"Recent date should become 'today': {result}"
    assert recent_date not in result


def test_two_recent_dates_both_replaced():
    text = f"User worked out on {iso(-1)} and meal-prepped on {iso(-3)}"
    result = normalize_dates_in_fact_text(text, today=TODAY)
    assert "yesterday" in result, f"Expected 'yesterday': {result}"
    assert "past week" in result, f"Expected 'past week': {result}"


def test_text_already_has_today():
    text = "User went to the store today and felt good"
    result = normalize_dates_in_fact_text(text, today=TODAY)
    assert result == text, f"Text with 'today' already should be unchanged: {result}"


def test_year_only_not_matched():
    text = "User was born in 1990"
    result = normalize_dates_in_fact_text(text, today=TODAY)
    assert result == text, f"Year-only should not be replaced: {result}"


def test_custom_today_param():
    custom_today = date(2023, 4, 10)
    text = "User attended service on 2023-04-06"
    result = normalize_dates_in_fact_text(text, today=custom_today)
    assert "past week" in result, f"With custom today=2023-04-10, date 2023-04-06 should be 'past week': {result}"


def test_custom_today_c018_scenario():
    """Exact c018 scenario: event on 2023-04-06, query on 2023-04-10 (4 days difference)."""
    custom_today = date(2023, 4, 10)
    text = "User attended Maundy Thursday service on 2023-04-06"
    result = normalize_dates_in_fact_text(text, today=custom_today)
    assert "past week" in result, f"c018 scenario: 4 days ago should be 'past week': {result}"
    assert "2023-04-06" not in result


def test_hallucinated_today_in_old_session():
    """Simulates the c018 bug: LLM writes today's actual date (2026-05-18) into a
    2023 session fact. The post-processor converts it to 'today', which is still
    wrong semantically, but prevents the 'future' interpretation that caused c018 to fail.
    """
    # eval_today is the date the eval was run (2026-05-18)
    eval_today = date(2026, 5, 18)
    text = "attended Maundy Thursday service on 2026-05-18"
    result = normalize_dates_in_fact_text(text, today=eval_today)
    assert "today" in result, f"Hallucinated today-date should become 'today': {result}"
    assert "2026-05-18" not in result


if __name__ == "__main__":
    tests = [name for name, obj in list(globals().items()) if name.startswith("test_") and callable(obj)]
    passed = 0
    failed = 0
    for name in tests:
        try:
            globals()[name]()
            print(f"  PASS  {name}")
            passed += 1
        except Exception as exc:
            print(f"  FAIL  {name}: {exc}")
            failed += 1
    print(f"\n{passed}/{passed + failed} tests passed")
    if failed:
        sys.exit(1)
