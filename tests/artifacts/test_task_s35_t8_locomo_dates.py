"""S35-T8A artifact: LoCoMo session_date_map plumbing.

Verifies:
  - Exact LoCoMo date strings parse to ISO dates.
  - session_2 sorts before session_10 and maps to D2 / D10.
  - Every LoCoMo QA receives the complete date map for its conversation.
  - Existing QA-index to conversation mapping remains unchanged.

Run: uv run python tests/artifacts/test_task_s35_t8_locomo_dates.py
"""

from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.eval_cogmem import (
    _build_locomo_session_date_map,
    _locomo_key_sort_value,
    _parse_locomo_session_date,
    get_fixture,
)


def test_exact_locomo_date_strings_parse() -> None:
    assert _parse_locomo_session_date("4:04 pm on 20 January, 2023") == "2023-01-20"
    assert _parse_locomo_session_date("4:15 pm on 20 April, 2023") == "2023-04-20"
    print("[ok] exact LoCoMo date strings parse to ISO dates")


def test_numeric_session_sort_and_mapping() -> None:
    keys = ["session_10", "session_2", "session_1", "session_10_date_time", "session_2_date_time"]
    assert sorted(keys, key=_locomo_key_sort_value) == [
        "session_1",
        "session_2",
        "session_10",
        "session_2_date_time",
        "session_10_date_time",
    ]

    conversation = {
        "session_10_date_time": "11:24 am on 25 April, 2023",
        "session_2_date_time": "7:06 pm on 5 February, 2023",
    }
    date_map = _build_locomo_session_date_map(conversation)
    assert date_map["D2"] == "2023-02-05"
    assert date_map["D10"] == "2023-04-25"
    print("[ok] numeric session sort maps session_2/session_10 to D2/D10")


def test_locomo_qas_receive_conversation_date_maps() -> None:
    fixture = get_fixture("locomo")
    questions = fixture["questions"]

    assert len(questions) == 161
    assert questions[0]["id"] == "locomo_q1"
    assert questions[13]["id"] == "locomo_q14"
    assert questions[14]["id"] == "locomo_q15"
    assert questions[47]["id"] == "locomo_q48"
    assert questions[48]["id"] == "locomo_q49"
    assert questions[93]["id"] == "locomo_q94"
    assert questions[94]["id"] == "locomo_q95"
    assert questions[131]["id"] == "locomo_q132"
    assert questions[132]["id"] == "locomo_q133"
    assert questions[160]["id"] == "locomo_q161"

    conv30_dates = questions[0]["session_date_map"]
    assert len(conv30_dates) == 19
    assert conv30_dates["D1"] == "2023-01-20"
    assert conv30_dates["D10"] == "2023-04-25"
    assert questions[13]["session_date_map"] == conv30_dates

    conv50_dates = questions[94]["session_date_map"]
    assert len(conv50_dates) == 30
    assert conv50_dates["D3"] == "2023-04-20"
    assert questions[131]["session_date_map"] == conv50_dates
    print("[ok] LoCoMo QAs receive complete per-conversation session_date_map")


def main() -> int:
    test_exact_locomo_date_strings_parse()
    test_numeric_session_sort_and_mapping()
    test_locomo_qas_receive_conversation_date_maps()
    print("\nS35-T8A PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
