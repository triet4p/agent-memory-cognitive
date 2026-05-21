"""S32-T1 artifact: cogmem_bench schema round-trip + validation.

Run: uv run python tests/artifacts/test_task_s32_t1_schema.py
Standalone script (no pytest), per repo convention.
"""

from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from pydantic import ValidationError

from cogmem_bench.schema import (
    GateResult,
    GeneratedConversation,
    GeneratedSession,
    GoldFact,
    Message,
    ScenarioSpec,
    SessionPlan,
    Trap,
    EmbeddingGateResult,
)


def _intention_spec() -> ScenarioSpec:
    return ScenarioSpec(
        scenario_id="pilot_intention_01",
        target_type="intention",
        topic="learning Rust before Q3",
        gold_fact=GoldFact(
            text="User planned to finish the Rust async course by end of September but later abandoned it.",
            fact_type="intention",
            session_index=1,
            metadata={"intention_status": "abandoned"},
        ),
        question="Did the user follow through on finishing the Rust async course?",
        gold_answer="No — they abandoned it.",
        traps=[
            Trap(
                trap_type="stale-intention",
                description="An earlier session states the plan confidently; a later one quietly drops it.",
                session_index=4,
            )
        ],
        session_plan=SessionPlan(total_sessions=8, gold_session_indices=[1, 4]),
        shared_context={"course": "Rust async course", "deadline": "end of September"},
        question_date="2026-05-21",
        rationale="Answer requires resolving intention_status (abandoned), which w/e/o cannot represent.",
    )


def test_round_trip() -> None:
    spec = _intention_spec()
    blob = spec.model_dump_json()
    restored = ScenarioSpec.model_validate_json(blob)
    assert restored == spec, "ScenarioSpec round-trip mismatch"
    assert restored.shared_context == {"course": "Rust async course", "deadline": "end of September"}
    print("[ok] ScenarioSpec round-trip (incl. shared_context)")


def test_gold_fact_type_metadata_validation() -> None:
    # intention without status -> reject
    try:
        GoldFact(text="x", fact_type="intention", session_index=0, metadata={})
    except ValidationError:
        print("[ok] intention without intention_status rejected")
    else:
        raise AssertionError("expected ValidationError for intention missing status")

    # action_effect missing outcome -> reject
    try:
        GoldFact(
            text="x",
            fact_type="action_effect",
            session_index=0,
            metadata={"precondition": "latency>100ms", "action": "switch to int8"},
        )
    except ValidationError:
        print("[ok] action_effect missing outcome rejected")
    else:
        raise AssertionError("expected ValidationError for action_effect missing outcome")

    # habit missing frequency -> reject
    try:
        GoldFact(text="x", fact_type="habit", session_index=0, metadata={})
    except ValidationError:
        print("[ok] habit without frequency rejected")
    else:
        raise AssertionError("expected ValidationError for habit missing frequency")


def test_cross_field_validation() -> None:
    # gold_fact.fact_type must equal target_type
    try:
        ScenarioSpec(
            scenario_id="bad",
            target_type="habit",
            topic="t",
            gold_fact=GoldFact(
                text="x", fact_type="intention", session_index=0, metadata={"intention_status": "planning"}
            ),
            question="q",
            gold_answer="a",
            session_plan=SessionPlan(total_sessions=7, gold_session_indices=[0]),
        )
    except ValidationError:
        print("[ok] target_type / gold_fact.fact_type mismatch rejected")
    else:
        raise AssertionError("expected ValidationError for type mismatch")

    # session_plan rejects out-of-range gold index
    try:
        SessionPlan(total_sessions=7, gold_session_indices=[9])
    except ValidationError:
        print("[ok] out-of-range gold_session_index rejected")
    else:
        raise AssertionError("expected ValidationError for out-of-range gold index")


def test_generated_and_gate_round_trip() -> None:
    conv = GeneratedConversation(
        scenario_id="pilot_intention_01",
        target_type="intention",
        sessions=[
            GeneratedSession(
                session_id="s0",
                date="2026-01-10",
                messages=[Message(role="user", content="hi"), Message(role="assistant", content="hello")],
            )
        ],
        question="q",
        gold_answer="a",
        question_date="2026-05-21",
        gold_session_ids=["s1"],
    )
    assert GeneratedConversation.model_validate_json(conv.model_dump_json()) == conv

    gate = GateResult(
        scenario_id="pilot_intention_01",
        embedding_gate=EmbeddingGateResult(
            passed=True, gold_fact_found=True, expected_fact_type="intention", found_fact_type="intention"
        ),
        accepted=False,
    )
    assert GateResult.model_validate_json(gate.model_dump_json()) == gate
    print("[ok] GeneratedConversation + GateResult round-trip")


def main() -> int:
    test_round_trip()
    test_gold_fact_type_metadata_validation()
    test_cross_field_validation()
    test_generated_and_gate_round_trip()
    print("\nS32-T1 PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
