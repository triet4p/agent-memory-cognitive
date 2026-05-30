"""S34-T1 artifact: agentic schema + prompt branch.

Offline tests for the agentic workload extension. No live LLM, no API needed.

Run: uv run python tests/artifacts/test_task_s34_t1_agentic.py
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from pydantic import ValidationError

from cogmem_api.prompts.retain.pass1 import build_pass1_prompt
from cogmem_bench.prompts import build_session_prompt, session_role
from cogmem_bench.schema import (
    GoldFact,
    GoldFragment,
    ScenarioSpec,
    SessionPlan,
    Trap,
)


class _DummyRetainConfig:
    """Bare config for build_pass1_prompt — only the attrs it reads."""

    retain_extraction_mode = "concise"
    retain_mission = None
    retain_custom_instructions = None


def _gold_ae() -> GoldFact:
    return GoldFact(
        text="rule text",
        fact_type="action_effect",
        metadata={"precondition": "p", "action": "a", "outcome": "o"},
        fragments=[
            GoldFragment(session_index=1, reveal="precondition piece"),
            GoldFragment(session_index=6, reveal="action+outcome piece"),
        ],
    )


def _base_agentic_kwargs() -> dict:
    return dict(
        scenario_id="agentic_x",
        target_type="action_effect",
        topic="topic",
        gold_fact=_gold_ae(),
        question="q",
        gold_answer="a",
        session_plan=SessionPlan(total_sessions=8, gold_session_indices=[1, 6]),
        workload="agentic",
        tools_used=["bash", "grep"],
        episodes=[f"episode {i}" for i in range(8)],
    )


def test_chat_workload_default_back_compat() -> None:
    """Existing chat specs (no workload field) round-trip with workload='chat'."""
    spec = ScenarioSpec(
        scenario_id="s1", target_type="action_effect", topic="t", gold_fact=_gold_ae(),
        question="q", gold_answer="a",
        session_plan=SessionPlan(total_sessions=8, gold_session_indices=[1, 6]),
    )
    assert spec.workload == "chat"
    assert spec.tools_used is None
    assert spec.episodes is None
    assert ScenarioSpec.model_validate_json(spec.model_dump_json()) == spec
    print("[ok] chat workload is default; existing specs unchanged")


def test_agentic_round_trip() -> None:
    spec = ScenarioSpec(**_base_agentic_kwargs())
    blob = spec.model_dump_json()
    restored = ScenarioSpec.model_validate_json(blob)
    assert restored == spec
    assert restored.workload == "agentic"
    assert restored.tools_used == ["bash", "grep"]
    assert restored.episodes is not None and len(restored.episodes) == 8
    print("[ok] agentic ScenarioSpec round-trip")


def test_agentic_requires_tools_and_episodes() -> None:
    # missing tools_used
    bad = _base_agentic_kwargs()
    bad["tools_used"] = []
    try:
        ScenarioSpec(**bad)
    except ValidationError:
        print("[ok] agentic with empty tools_used rejected")
    else:
        raise AssertionError("expected ValidationError for empty tools_used")

    # episodes length mismatch
    bad = _base_agentic_kwargs()
    bad["episodes"] = ["only", "two"]
    try:
        ScenarioSpec(**bad)
    except ValidationError:
        print("[ok] agentic with episodes len != total_sessions rejected")
    else:
        raise AssertionError("expected ValidationError for episodes length mismatch")


def test_agentic_only_action_effect() -> None:
    """S34 scope: agentic only valid for action_effect target_type."""
    bad = _base_agentic_kwargs()
    bad["target_type"] = "intention"
    bad["gold_fact"] = GoldFact(
        text="x", fact_type="intention", metadata={"intention_status": "planning"},
        fragments=[GoldFragment(session_index=0, reveal="a"), GoldFragment(session_index=1, reveal="b")],
    )
    bad["session_plan"] = SessionPlan(total_sessions=8, gold_session_indices=[0, 1])
    try:
        ScenarioSpec(**bad)
    except ValidationError:
        print("[ok] agentic+intention rejected (S34 scope is action_effect only)")
    else:
        raise AssertionError("expected ValidationError for agentic+intention")


def test_chat_cannot_carry_agentic_fields() -> None:
    """Sanity: tools_used/episodes are agentic-only — must not bleed into chat specs."""
    bad = dict(
        scenario_id="s2", target_type="action_effect", topic="t", gold_fact=_gold_ae(),
        question="q", gold_answer="a",
        session_plan=SessionPlan(total_sessions=8, gold_session_indices=[1, 6]),
        workload="chat",
        tools_used=["bash"],
    )
    try:
        ScenarioSpec(**bad)
    except ValidationError:
        print("[ok] chat workload with tools_used rejected")
    else:
        raise AssertionError("expected ValidationError for chat+tools_used")


def test_agentic_prompt_branch_present() -> None:
    """build_session_prompt routes to the agentic builder when workload='agentic'."""
    spec = ScenarioSpec(**_base_agentic_kwargs())

    # gold session
    gold_prompt = build_session_prompt(spec, 1, session_role(spec, 1), prior_recaps=[])
    assert "EPISODE 2 of 8" in gold_prompt
    assert "ALLOWED TOOLS" in gold_prompt
    assert "[tool: <tool_name>]" in gold_prompt
    assert "[output]" in gold_prompt
    assert "ONE PIECE" in gold_prompt
    assert "precondition piece" in gold_prompt
    # anti-leak phrasing must be present
    assert "self-sufficient" in gold_prompt or "do NOT show the FULL" in gold_prompt
    print("[ok] agentic prompt: gold episode has tool-format + anti-leak hints")

    # filler session
    filler_idx = 0
    assert session_role(spec, filler_idx) == "filler"
    filler_prompt = build_session_prompt(spec, filler_idx, "filler", prior_recaps=[])
    assert "FILLER" in filler_prompt
    assert "[tool: <tool_name>]" in filler_prompt
    print("[ok] agentic prompt: filler episode includes tool format too")


def test_chat_prompt_unchanged() -> None:
    """Sanity: chat workload still produces chat prompt (no [tool:] tag)."""
    chat_spec = ScenarioSpec(
        scenario_id="s_chat",
        target_type="action_effect",
        topic="t",
        gold_fact=_gold_ae(),
        question="q",
        gold_answer="a",
        session_plan=SessionPlan(total_sessions=8, gold_session_indices=[1, 6]),
    )
    prompt = build_session_prompt(chat_spec, 1, "gold", prior_recaps=[])
    assert "SESSION 2 of 8" in prompt
    assert "[tool:" not in prompt
    assert "ALLOWED TOOLS" not in prompt
    print("[ok] chat prompt path unchanged")


def test_prototype_spec_loads() -> None:
    """The hand-authored pilot spec parses and is structurally valid."""
    path = REPO_ROOT / "cogmem_bench" / "specs" / "agentic_pilot" / "agentic_ae_pilot_01.json"
    raw = json.loads(path.read_text(encoding="utf-8"))
    spec = ScenarioSpec.model_validate(raw)
    assert spec.workload == "agentic"
    assert spec.target_type == "action_effect"
    assert len(spec.episodes or []) == spec.session_plan.total_sessions
    # the gold fragments must be in different episodes (anti-leak design)
    frag_idxs = spec.gold_fact.fragment_indices
    assert len(frag_idxs) >= 2 and len(set(frag_idxs)) == len(frag_idxs)
    print(f"[ok] prototype spec loads (episodes={len(spec.episodes or [])}, fragments={frag_idxs})")


def test_retain_pass1_addendum_off_by_default() -> None:
    """build_pass1_prompt without agentic_transcript=True must NOT contain the addendum."""
    prompt, _mode = build_pass1_prompt(_DummyRetainConfig())
    assert "AGENTIC TRANSCRIPT MODE" not in prompt
    assert "[tool:" not in prompt
    print("[ok] Pass1 prompt unchanged when agentic_transcript=False (S33 byte-identical)")


def test_retain_pass1_addendum_on() -> None:
    """With agentic_transcript=True, the addendum is appended and instructs tool-tag reading."""
    prompt, _mode = build_pass1_prompt(_DummyRetainConfig(), agentic_transcript=True)
    assert "AGENTIC TRANSCRIPT MODE" in prompt
    assert "[tool:" in prompt
    assert "[output]" in prompt
    assert "precondition" in prompt and "action" in prompt and "outcome" in prompt
    print("[ok] Pass1 prompt addendum activates with agentic_transcript=True")


def test_retain_request_accepts_agentic_transcript() -> None:
    """The HTTP RetainRequest schema accepts agentic_transcript and defaults to False."""
    from cogmem_api.api.http import RetainRequest

    default = RetainRequest(items=[])
    assert default.agentic_transcript is False

    on = RetainRequest.model_validate({"items": [], "agentic_transcript": True})
    assert on.agentic_transcript is True
    print("[ok] RetainRequest carries agentic_transcript flag (default False)")


def test_gates_block_agentic_without_paired_banks() -> None:
    """Sanity guard: agentic spec without --retain-level-ablation must be rejected
    (otherwise the addendum is silently dropped because run_pipeline doesn't pass it)."""
    from cogmem_bench.gates import run_case_gates

    spec = ScenarioSpec(**_base_agentic_kwargs())
    try:
        run_case_gates(
            spec, fixture_path="/dev/null", api_base_url="http://x",
            bank_id="b", retain_level_ablation=False, skip_retain=False,
            post_json_fn=lambda *_a, **_k: {},
        )
    except ValueError as exc:
        assert "agentic" in str(exc) and "retain-level-ablation" in str(exc)
        print("[ok] gates.run_case_gates blocks agentic without --retain-level-ablation")
    except Exception as exc:
        raise AssertionError(f"expected ValueError, got {type(exc).__name__}: {exc}")
    else:
        raise AssertionError("expected ValueError for agentic without paired banks")


def main() -> int:
    test_chat_workload_default_back_compat()
    test_agentic_round_trip()
    test_agentic_requires_tools_and_episodes()
    test_agentic_only_action_effect()
    test_chat_cannot_carry_agentic_fields()
    test_agentic_prompt_branch_present()
    test_chat_prompt_unchanged()
    test_prototype_spec_loads()
    test_retain_pass1_addendum_off_by_default()
    test_retain_pass1_addendum_on()
    test_retain_request_accepts_agentic_transcript()
    test_gates_block_agentic_without_paired_banks()
    print("\nS34-T1 PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
