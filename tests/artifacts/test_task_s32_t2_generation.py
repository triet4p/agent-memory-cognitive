"""S32-T2 artifact: multi-call, fragment-distributed generation (offline, FakeLLM).

Verifies: per-session prompts reveal ONLY their gold fragment (no full-fact leak),
consistency blocks (canonical ledger + recap + last-K verbatim), one LLM call per session,
and the union/anti-leak soft check over distributed gold fragments.

Run: uv run python tests/artifacts/test_task_s32_t2_generation.py
"""

from __future__ import annotations

import asyncio
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from cogmem_bench.generation import generate_conversation, parse_session_response, soft_validate_embedding
from cogmem_bench.prompts import build_session_prompt, session_role
from cogmem_bench.schema import GoldFact, GoldFragment, Message, ScenarioSpec, SessionPlan, Trap

TOTAL = 8


def _spec() -> ScenarioSpec:
    return ScenarioSpec(
        scenario_id="t2_intent",
        target_type="intention",
        topic="learning Rust before Q3 to optimize an inference server",
        gold_fact=GoldFact(
            text="User planned to finish the Rust async course by end of September but abandoned it after switching priorities.",
            fact_type="intention",
            metadata={"intention_status": "abandoned"},
            fragments=[
                GoldFragment(session_index=1, reveal="user states the PLAN to finish the Rust async course by September"),
                GoldFragment(session_index=5, reveal="user mentions they dropped the course after priorities shifted"),
            ],
        ),
        question="Did the user finish the Rust async course they planned?",
        gold_answer="No, they abandoned it.",
        traps=[Trap(trap_type="stale-intention", description="Mid-thread enthusiasm for Rust generally.", session_index=3)],
        session_plan=SessionPlan(total_sessions=TOTAL, gold_session_indices=[1, 5]),
        shared_context={"course": "Rust async course", "deadline": "end of September"},
        question_date="2026-05-21",
    )


def _wrap(obj: dict) -> str:
    """Minimax-style output: <think> block + fenced JSON."""
    return f"<think>\nrendering one session.\n</think>\n```json\n{json.dumps(obj, ensure_ascii=False)}\n```"


class FakeSessionLLM:
    """Per-session FakeLLM — returns a canned single-session string and counts calls.

    Distinguishes the two gold fragments by the reveal text the prompt carries.
    """

    def __init__(self) -> None:
        self.calls = 0

    async def call(self, messages, **kwargs):  # noqa: ANN001
        self.calls += 1
        prompt = messages[0]["content"]
        is_gold = "ONE PIECE" in prompt
        if is_gold and "PLAN" in prompt:  # session 1 — the plan fragment
            obj = {
                "recap": "user plans to finish the Rust async course by September",
                "messages": [
                    {"role": "user", "content": "I'm planning to finish the Rust async course by end of September."},
                    {"role": "assistant", "content": "Great target — that lines up with your Q3 inference server goal."},
                ],
            }
        elif is_gold:  # session 5 — the drop fragment
            obj = {
                "recap": "user dropped the Rust course after priorities shifted",
                "messages": [
                    {"role": "user", "content": "I've dropped the course — priorities shifted to the data pipeline."},
                    {"role": "assistant", "content": "Understandable; the pipeline work is more pressing right now."},
                ],
            }
        else:
            obj = {
                "recap": "generic on-topic inference server chat",
                "messages": [
                    {"role": "user", "content": "Quick update on the inference server work."},
                    {"role": "assistant", "content": "Thanks for the context — noted."},
                ],
            }
        return _wrap(obj)


def test_roles_and_fragment_prompt() -> None:
    spec = _spec()
    assert session_role(spec, 1) == "gold"
    assert session_role(spec, 5) == "gold"
    assert session_role(spec, 3) == "trap"
    assert session_role(spec, 0) == "filler"

    gold1 = build_session_prompt(spec, 1, "gold", [], recent_sessions=[])
    # reveals ONLY this fragment, not the full fact / answer / other fragment
    assert "ONE PIECE" in gold1
    assert "PLAN" in gold1 and "September" in gold1
    assert spec.gold_fact.text not in gold1, "gold prompt must NOT contain the full canonical fact"
    assert spec.gold_answer not in gold1, "gold prompt must NOT contain the answer"
    assert "dropped" not in gold1, "session-1 prompt must NOT contain the session-5 fragment"
    # canonical ledger + recap request present
    assert "CANONICAL FACTS" in gold1 and "Rust async course" in gold1
    assert '"recap"' in gold1
    print("[ok] gold session prompt reveals only its fragment (no full-fact leak)")


def test_last_k_verbatim_block() -> None:
    spec = _spec()
    recent = [("Session 4", [Message(role="user", content="UNIQUE_VERBATIM_TOKEN")])]
    p = build_session_prompt(spec, 5, "gold", ["Session 0 recap"], recent_sessions=recent)
    assert "Session 0 recap" in p           # older recap
    assert "UNIQUE_VERBATIM_TOKEN" in p      # recent verbatim
    print("[ok] prompt threads older recaps + last-K verbatim")


def test_parse_session_response() -> None:
    recap, msgs = parse_session_response(_wrap({"recap": "r", "messages": [{"role": "user", "content": "hi"}]}))
    assert recap == "r" and len(msgs) == 1
    no_recap, msgs2 = parse_session_response('{"messages":[{"role":"assistant","content":"yo"}]}')
    assert no_recap is None and msgs2[0].role == "assistant"
    print("[ok] parsed single-session output incl. optional model recap")


def test_multicall_generate_and_softcheck() -> None:
    spec = _spec()
    llm = FakeSessionLLM()
    conv = asyncio.run(generate_conversation(spec, llm))
    assert llm.calls == TOTAL, f"expected one call per session ({TOTAL}), got {llm.calls}"
    assert conv.gold_session_ids == ["t2_intent_s1", "t2_intent_s5"]
    # each gold session carries only its piece
    s1 = " ".join(m.content for m in conv.sessions[1].messages).lower()
    s5 = " ".join(m.content for m in conv.sessions[5].messages).lower()
    assert "september" in s1 and "dropped" not in s1
    assert "dropped" in s5 and "september" not in s5
    # union covers the gold; neither session is self-sufficient
    ok, detail = soft_validate_embedding(conv, spec)
    assert ok, f"soft check failed: {detail}"
    print(f"[ok] multi-call ({llm.calls} calls), fragments distributed — {detail}")


def test_bad_response_rejected() -> None:
    try:
        parse_session_response("no json here")
    except ValueError:
        print("[ok] malformed session response rejected")
    else:
        raise AssertionError("expected ValueError for malformed response")


def main() -> int:
    test_roles_and_fragment_prompt()
    test_last_k_verbatim_block()
    test_parse_session_response()
    test_multicall_generate_and_softcheck()
    test_bad_response_rejected()
    print("\nS32-T2 PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
