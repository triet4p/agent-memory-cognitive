"""S32-T3 artifact: distilled fixture emit -> load through the eval harness.

Proves the generated benchmark is consumable by scripts/eval_cogmem.py UNCHANGED.

Run: uv run python tests/artifacts/test_task_s32_t3_fixtures.py
"""

from __future__ import annotations

import sys
import tempfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from cogmem_bench.fixtures import to_distilled_item, write_distilled_fixture
from cogmem_bench.schema import GeneratedConversation, GeneratedSession, Message
from scripts.eval_cogmem import get_fixture


def _conv() -> GeneratedConversation:
    sessions = []
    for i in range(8):
        if i == 1:
            msgs = [
                Message(role="user", content="I planned to finish the Rust course by September."),
                Message(role="assistant", content="Aligns with your Q3 goal."),
                Message(role="user", content="Dropping it — abandoned the course."),
            ]
        else:
            msgs = [
                Message(role="user", content=f"inference server note day {i}"),
                Message(role="assistant", content="noted"),
            ]
        sessions.append(GeneratedSession(session_id=f"t3_intent_s{i}", date=f"2026-0{i+1}-01", messages=msgs))
    return GeneratedConversation(
        scenario_id="t3_intent",
        target_type="intention",
        sessions=sessions,
        question="Did the user finish the Rust course?",
        gold_answer="No, they abandoned it.",
        question_date="2026-05-21",
        gold_session_ids=["t3_intent_s1"],
    )


def test_distilled_item_shape() -> None:
    item = to_distilled_item(_conv())
    for key in (
        "question_id",
        "question",
        "answer",
        "answer_session_ids",
        "question_type",
        "question_date",
        "haystack_sessions",
        "haystack_session_ids",
        "haystack_dates",
    ):
        assert key in item, f"missing distilled key: {key}"
    assert len(item["haystack_sessions"]) == len(item["haystack_session_ids"]) == 8
    assert item["haystack_sessions"][1][0] == {"role": "user", "content": "I planned to finish the Rust course by September."}
    print("[ok] distilled item has all LongMemEval keys + parallel session arrays")


def test_emit_and_load_through_harness() -> None:
    with tempfile.TemporaryDirectory() as d:
        path = write_distilled_fixture([_conv()], Path(d) / "bench_pilot.json")
        fixture = get_fixture("longmemeval", fixture_path=str(path))

        questions = fixture["questions"]
        assert len(questions) == 1, f"expected 1 question, got {len(questions)}"
        q = questions[0]
        assert q["id"] == "t3_intent"
        assert q["gold_answer"] == "No, they abandoned it."
        assert q["gold_session_ids"] == ["t3_intent_s1"]
        assert q["category"] == "intention"  # target_type passes through type_map
        # sessions parsed for retain
        sess_ids = [sid for sid, _ in q["_sessions"]]
        assert "t3_intent_s1" in sess_ids
        assert len(sess_ids) == 8
        # message-structured form present for retain
        msg_ids = [sid for sid, _ in q["_messages"]]
        assert msg_ids == sess_ids
        # date map wired
        assert q["session_date_map"]["t3_intent_s1"] == "2026-02-01"
        print("[ok] emitted fixture loads through eval_cogmem.get_fixture (8 sessions, dates, gold)")


def main() -> int:
    test_distilled_item_shape()
    test_emit_and_load_through_harness()
    print("\nS32-T3 PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
