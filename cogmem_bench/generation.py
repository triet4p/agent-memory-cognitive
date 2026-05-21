"""Generation step — render a ScenarioSpec into a GeneratedConversation via Minimax.

Multi-call: one call per session, threading a running recap forward so sessions stay
consistent. Gold/trap sessions get a larger token budget than filler. Response processing
reuses cogmem_api's parse_llm_json (strips <think>/fences, repairs truncated JSON).

The assembled conversation is a *frozen* artifact; never regenerated at eval time. The
schema / fixtures / gates layers are unchanged by the multi-call switch.
"""

from __future__ import annotations

import re
from typing import Any, Protocol

from cogmem_api.engine.llm_wrapper import parse_llm_json

from .prompts import build_session_prompt, session_role
from .schema import GeneratedConversation, GeneratedSession, Message, ScenarioSpec


class _Caller(Protocol):
    async def call(self, messages: list[dict[str, str]], **kwargs: Any) -> Any: ...


def _session_id(spec: ScenarioSpec, index: int) -> str:
    return f"{spec.scenario_id}_s{index}"


def parse_session_response(raw: str) -> tuple[str | None, list[Message]]:
    """Parse one session's raw output into (model_recap, messages).

    `model_recap` is the generator's own one-line summary of the session (used to keep
    later sessions consistent); None if absent.
    """
    parsed = parse_llm_json(raw)
    recap_raw: object = None
    if isinstance(parsed, dict):
        msgs_raw = parsed.get("messages")
        recap_raw = parsed.get("recap")
        if msgs_raw is None and isinstance(parsed.get("session"), dict):
            msgs_raw = parsed["session"].get("messages")
            recap_raw = recap_raw or parsed["session"].get("recap")
    elif isinstance(parsed, list):
        msgs_raw = parsed
    else:
        msgs_raw = None
    if not isinstance(msgs_raw, list) or not msgs_raw:
        raise ValueError("session response missing a non-empty 'messages' list")
    messages = [
        Message(
            role="assistant" if str(m.get("role", "")).strip().lower() == "assistant" else "user",
            content=str(m.get("content", "")),
        )
        for m in msgs_raw
        if isinstance(m, dict) and str(m.get("content", "")).strip()
    ]
    if not messages:
        raise ValueError("session response had no usable messages")
    model_recap = recap_raw.strip() if isinstance(recap_raw, str) and recap_raw.strip() else None
    return model_recap, messages


def _recap(messages: list[Message], limit: int = 160) -> str:
    first_user = next((m.content for m in messages if m.role == "user"), messages[0].content)
    return first_user.strip()[:limit]


def _keywords(text: str) -> set[str]:
    return {w for w in re.findall(r"[a-z0-9]+", text.lower()) if len(w) >= 4}


def soft_validate_embedding(conv: GeneratedConversation, spec: ScenarioSpec) -> tuple[bool, str]:
    """Cheap pre-retain drift check: does the gold session text overlap the gold fact?

    NOT the authoritative embedding gate (that retains + checks fact_type in gate.py).
    """
    if len(conv.sessions) != spec.session_plan.total_sessions:
        return False, f"expected {spec.session_plan.total_sessions} sessions, got {len(conv.sessions)}"
    gold_kw = _keywords(spec.gold_fact.text)
    if not gold_kw:
        return True, "no gold keywords to check"
    gold_ids = set(conv.gold_session_ids)
    gold_text = " ".join(m.content for s in conv.sessions if s.session_id in gold_ids for m in s.messages)
    coverage = len(gold_kw & _keywords(gold_text)) / len(gold_kw)
    if coverage < 0.3:
        return False, f"gold-session keyword coverage {coverage:.0%} < 30% (likely drift)"
    return True, f"gold-session keyword coverage {coverage:.0%}"


async def generate_conversation(
    spec: ScenarioSpec,
    llm: _Caller,
    *,
    gold_tokens: int = 3500,
    filler_tokens: int = 1800,
    temperature: float = 0.7,
    last_k_verbatim: int = 2,
) -> GeneratedConversation:
    """Generate the conversation session-by-session (one LLM call per session).

    Consistency across calls is maintained by (1) `spec.shared_context` injected into every
    prompt, (2) model-emitted one-line recaps of older sessions, and (3) the last
    `last_k_verbatim` sessions passed verbatim for tight local continuity.
    """
    plan = spec.session_plan
    dates = plan.dates or [None] * plan.total_sessions

    sessions: list[GeneratedSession] = []
    recaps: list[str] = []  # aligned to session index
    for i in range(plan.total_sessions):
        role = session_role(spec, i)
        split = max(0, i - last_k_verbatim)
        older_recaps = recaps[:split]
        recent_sessions = [(f"Session {j}", sessions[j].messages) for j in range(split, i)]
        prompt = build_session_prompt(spec, i, role, older_recaps, recent_sessions)
        max_tokens = gold_tokens if role in ("gold", "trap") else filler_tokens
        raw = await llm.call(
            messages=[{"role": "user", "content": prompt}],
            temperature=temperature,
            max_completion_tokens=max_tokens,
        )
        model_recap, messages = parse_session_response(str(raw or ""))
        sessions.append(
            GeneratedSession(
                session_id=_session_id(spec, i),
                date=dates[i] if i < len(dates) else None,
                messages=messages,
            )
        )
        recaps.append(f"Session {i} [{role}]: {model_recap or _recap(messages)}")

    gold_session_ids = [_session_id(spec, idx) for idx in plan.gold_session_indices]
    return GeneratedConversation(
        scenario_id=spec.scenario_id,
        target_type=spec.target_type,
        sessions=sessions,
        question=spec.question,
        gold_answer=spec.gold_answer,
        question_date=spec.question_date,
        gold_session_ids=gold_session_ids,
    )
