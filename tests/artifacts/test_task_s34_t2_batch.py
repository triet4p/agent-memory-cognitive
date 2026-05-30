"""S34-T2 artifact: agentic batch — schema field + leak validator + spec load.

Offline tests for the T2 additions on top of T1:
  - gold_action_tokens optional field on ScenarioSpec
  - soft_validate_no_action_leak in cogmem_bench.generation
  - all 12 hand-authored agentic specs parse and have leak tokens declared

Run: uv run python tests/artifacts/test_task_s34_t2_batch.py
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from pydantic import ValidationError

from cogmem_bench.generation import soft_validate_no_action_leak
from cogmem_bench.schema import (
    GeneratedConversation,
    GeneratedSession,
    GoldFact,
    GoldFragment,
    Message,
    ScenarioSpec,
    SessionPlan,
)

AGENTIC_DIR = REPO_ROOT / "cogmem_bench" / "specs" / "agentic"


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


def _make_agentic_spec(tokens: list[str] | None) -> ScenarioSpec:
    return ScenarioSpec(
        scenario_id="agentic_test",
        target_type="action_effect",
        topic="topic",
        gold_fact=_gold_ae(),
        question="q",
        gold_answer="a",
        session_plan=SessionPlan(total_sessions=8, gold_session_indices=[1, 6]),
        workload="agentic",
        tools_used=["bash"],
        episodes=[f"ep {i}" for i in range(8)],
        gold_action_tokens=tokens,
    )


def _make_conv(gold_text: str, filler_text: str) -> GeneratedConversation:
    sessions = []
    for i in range(8):
        is_gold = i in (1, 6)
        text = gold_text if is_gold else filler_text
        sessions.append(GeneratedSession(
            session_id=f"agentic_test_s{i}",
            messages=[Message(role="user", content=f"q{i}"), Message(role="assistant", content=text)],
        ))
    return GeneratedConversation(
        scenario_id="agentic_test", target_type="action_effect",
        sessions=sessions, question="q", gold_answer="a",
        gold_session_ids=["agentic_test_s1", "agentic_test_s6"],
    )


# ── Schema field ─────────────────────────────────────────────────────────


def test_gold_action_tokens_optional_default_none() -> None:
    spec = _make_agentic_spec(tokens=None)
    assert spec.gold_action_tokens is None
    assert ScenarioSpec.model_validate_json(spec.model_dump_json()) == spec
    print("[ok] gold_action_tokens defaults to None")


def test_gold_action_tokens_round_trip() -> None:
    toks = ["--foo-bar", "BAZ_OPT=quux", "ghcr.io/whatever"]
    spec = _make_agentic_spec(tokens=toks)
    restored = ScenarioSpec.model_validate_json(spec.model_dump_json())
    assert restored.gold_action_tokens == toks
    print("[ok] gold_action_tokens round-trips with multiple distinctive strings")


def test_chat_cannot_carry_gold_action_tokens() -> None:
    """Sanity: gold_action_tokens is agentic-only, must reject on chat workload."""
    bad = dict(
        scenario_id="chat_x", target_type="action_effect", topic="t",
        gold_fact=_gold_ae(), question="q", gold_answer="a",
        session_plan=SessionPlan(total_sessions=8, gold_session_indices=[1, 6]),
        workload="chat",
        gold_action_tokens=["x"],
    )
    try:
        ScenarioSpec(**bad)
    except ValidationError:
        print("[ok] chat workload with gold_action_tokens rejected")
    else:
        raise AssertionError("expected ValidationError for chat + gold_action_tokens")


# ── soft_validate_no_action_leak ─────────────────────────────────────────


def test_leak_skipped_when_no_tokens() -> None:
    spec = _make_agentic_spec(tokens=None)
    conv = _make_conv(gold_text="gold uses --special-flag", filler_text="--special-flag everywhere")
    ok, detail = soft_validate_no_action_leak(conv, spec)
    assert ok is True and "skip" in detail
    print("[ok] leak validator skips when gold_action_tokens unset")


def test_leak_clean_when_tokens_only_in_gold() -> None:
    spec = _make_agentic_spec(tokens=["--special-flag", "UNIQUE_TOKEN_xyz"])
    conv = _make_conv(
        gold_text="agent runs --special-flag with UNIQUE_TOKEN_xyz",
        filler_text="totally unrelated work no tokens",
    )
    ok, detail = soft_validate_no_action_leak(conv, spec)
    assert ok is True and "no gold-action leak" in detail
    print(f"[ok] leak validator passes when tokens only in gold: {detail}")


def test_leak_detected_in_filler() -> None:
    spec = _make_agentic_spec(tokens=["--special-flag", "UNIQUE_TOKEN_xyz"])
    conv = _make_conv(
        gold_text="agent runs --special-flag with UNIQUE_TOKEN_xyz",
        filler_text="oops the filler also says UNIQUE_TOKEN_xyz",
    )
    ok, detail = soft_validate_no_action_leak(conv, spec)
    assert ok is False
    assert "UNIQUE_TOKEN_xyz" in detail
    assert "agentic_test_s0" in detail  # at least one non-gold session flagged
    # Encode-safe print (Windows cp1252 trips on the leading warning glyph).
    safe = detail.encode("ascii", "replace").decode("ascii")
    print(f"[ok] leak validator detects token in filler: {safe[:140]}...")


# ── All 12 specs parse + each declares gold_action_tokens ────────────────


def test_all_agentic_specs_load() -> None:
    files = sorted(AGENTIC_DIR.glob("*.json"))
    assert len(files) == 12, f"expected 12 agentic specs, found {len(files)}"
    seen_ids: set[str] = set()
    for p in files:
        raw = json.loads(p.read_text(encoding="utf-8"))
        spec = ScenarioSpec.model_validate(raw)
        assert spec.workload == "agentic"
        assert spec.target_type == "action_effect"
        assert spec.episodes and len(spec.episodes) == spec.session_plan.total_sessions
        assert spec.gold_action_tokens, f"{p.name} missing gold_action_tokens"
        assert spec.scenario_id not in seen_ids, f"duplicate id {spec.scenario_id}"
        seen_ids.add(spec.scenario_id)
        frag_idxs = spec.gold_fact.fragment_indices
        assert len(frag_idxs) >= 2 and len(set(frag_idxs)) == len(frag_idxs), f"{p.name} fragments collide"
    print(f"[ok] all 12 agentic specs load (unique ids, gold_action_tokens declared)")


def main() -> int:
    test_gold_action_tokens_optional_default_none()
    test_gold_action_tokens_round_trip()
    test_chat_cannot_carry_gold_action_tokens()
    test_leak_skipped_when_no_tokens()
    test_leak_clean_when_tokens_only_in_gold()
    test_leak_detected_in_filler()
    test_all_agentic_specs_load()
    print("\nS34-T2 PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
