"""S32-T2 artifact: generation response-processing (offline, FakeLLM).

Verifies the Minimax response processing path: strip <think>/fences, parse JSON,
build a validated GeneratedConversation, and run the soft embedding pre-check.

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

from cogmem_bench.generation import (
    generate_conversation,
    parse_session_response,
    soft_validate_embedding,
)
from cogmem_bench.prompts import build_session_prompt, session_role
from cogmem_bench.schema import GoldFact, ScenarioSpec, SessionPlan, Trap

TOTAL = 8


def _spec() -> ScenarioSpec:
    return ScenarioSpec(
        scenario_id="t2_intent",
        target_type="intention",
        topic="learning Rust before Q3 to optimize an inference server",
        gold_fact=GoldFact(
            text="User planned to finish the Rust async course by end of September but abandoned it after switching priorities.",
            fact_type="intention",
            session_index=1,
            metadata={"intention_status": "abandoned"},
        ),
        question="Did the user finish the Rust async course they planned?",
        gold_answer="No, they abandoned it.",
        traps=[Trap(trap_type="stale-intention", description="Early confident plan, later dropped.", session_index=1)],
        session_plan=SessionPlan(total_sessions=TOTAL, gold_session_indices=[1]),
        shared_context={"course": "Rust async course", "deadline": "end of September"},
        question_date="2026-05-21",
    )


def _canned_session(role: str) -> str:
    """One session's Minimax-style output: <think> block + fenced JSON {messages:[...]}."""
    if role == "gold":
        msgs = [
            {"role": "user", "content": "I'm planning to finish the Rust async course by end of September."},
            {"role": "assistant", "content": "Nice, that aligns with your Q3 inference server goal."},
            {"role": "user", "content": "Actually I'm dropping it — priorities shifted to the data pipeline, so I abandoned the course."},
        ]
        recap = "User abandoned the Rust async course they had planned for September."
    else:
        msgs = [
            {"role": "user", "content": "Quick update on the inference server work."},
            {"role": "assistant", "content": "Got it, thanks for the context."},
        ]
        recap = "Generic on-topic inference server chat."
    body = json.dumps({"recap": recap, "messages": msgs}, ensure_ascii=False)
    return f"<think>\nrendering one session ({role}).\n</think>\n```json\n{body}\n```"


class FakeSessionLLM:
    """Per-session FakeLLM — returns a canned single-session string and counts calls.

    Detects the gold session by the prompt carrying the gold metadata ("abandoned").
    """

    def __init__(self) -> None:
        self.calls = 0

    async def call(self, messages, **kwargs):  # noqa: ANN001
        self.calls += 1
        prompt = messages[0]["content"]
        role = "gold" if "GOLD FACT" in prompt and "abandoned" in prompt else "filler"
        return _canned_session(role)


def test_session_prompt_consistency_blocks() -> None:
    spec = _spec()
    assert session_role(spec, 1) == "gold"
    gold_prompt = build_session_prompt(spec, 1, "gold", [], recent_sessions=[])
    assert "abandoned" in gold_prompt and "GOLD FACT" in gold_prompt
    # canonical-context ledger injected
    assert "CANONICAL FACTS" in gold_prompt and "Rust async course" in gold_prompt
    # output asks for a recap field
    assert '"recap"' in gold_prompt

    # last-K verbatim: a recent session's exact text appears
    from cogmem_bench.schema import Message

    recent = [("Session 4", [Message(role="user", content="UNIQUE_VERBATIM_TOKEN")])]
    filler_prompt = build_session_prompt(spec, 5, "filler", ["Session 0 recap"], recent_sessions=recent)
    assert "FILLER" in filler_prompt
    assert "Session 0 recap" in filler_prompt           # older recap
    assert "UNIQUE_VERBATIM_TOKEN" in filler_prompt      # recent verbatim
    print("[ok] prompt carries canonical ledger + older recaps + last-K verbatim + recap request")


def test_parse_session_response() -> None:
    recap, msgs = parse_session_response(_canned_session("gold"))
    assert len(msgs) == 3
    assert msgs[-1].role == "user"
    assert recap and "abandoned" in recap
    # recap optional: still parses if absent
    no_recap, msgs2 = parse_session_response('{"messages":[{"role":"user","content":"hi"}]}')
    assert no_recap is None and len(msgs2) == 1
    print("[ok] parsed single-session <think>+fenced JSON incl. model recap")


def test_async_multicall_generate() -> None:
    spec = _spec()
    llm = FakeSessionLLM()
    conv = asyncio.run(generate_conversation(spec, llm))
    assert conv.scenario_id == "t2_intent"
    assert len(conv.sessions) == TOTAL
    assert llm.calls == TOTAL, f"expected one call per session ({TOTAL}), got {llm.calls}"
    assert conv.gold_session_ids == ["t2_intent_s1"]
    # gold session got the gold content
    assert "abandoned" in " ".join(m.content for m in conv.sessions[1].messages)
    ok, detail = soft_validate_embedding(conv, spec)
    assert ok, f"soft embedding check failed: {detail}"
    print(f"[ok] multi-call generation: {llm.calls} calls, {len(conv.sessions)} sessions, {detail}")


def test_bad_response_rejected() -> None:
    try:
        parse_session_response("no json here")
    except ValueError:
        print("[ok] malformed session response rejected")
    else:
        raise AssertionError("expected ValueError for malformed response")


def main() -> int:
    test_session_prompt_consistency_blocks()
    test_parse_session_response()
    test_async_multicall_generate()
    test_bad_response_rejected()
    print("\nS32-T2 PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
