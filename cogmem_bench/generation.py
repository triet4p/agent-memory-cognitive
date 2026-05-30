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
    """Cheap pre-retain checks for the distributed gold fact.

    Two things matter for a discriminating case:
      - UNION of the gold-fragment sessions must cover the gold-fact keywords (the pieces
        are present somewhere).
      - NO single gold session should be self-sufficient (anti-leak) — otherwise a
        world/experience/opinion-only system answers from one recalled sentence and the
        case won't discriminate. This is a WARNING, not a hard fail.

    NOT the authoritative embedding gate (that retains + checks fact_type in gate.py).
    """
    if len(conv.sessions) != spec.session_plan.total_sessions:
        return False, f"expected {spec.session_plan.total_sessions} sessions, got {len(conv.sessions)}"
    gold_kw = _keywords(spec.gold_fact.text)
    if not gold_kw:
        return True, "no gold keywords to check"
    gold_ids = set(conv.gold_session_ids)
    gold_sessions = [s for s in conv.sessions if s.session_id in gold_ids]

    union_text = " ".join(m.content for s in gold_sessions for m in s.messages)
    union_cov = len(gold_kw & _keywords(union_text)) / len(gold_kw)

    per_session_cov = [
        len(gold_kw & _keywords(" ".join(m.content for m in s.messages))) / len(gold_kw)
        for s in gold_sessions
    ]
    max_single = max(per_session_cov) if per_session_cov else 0.0

    if union_cov < 0.5:
        return False, f"union gold coverage {union_cov:.0%} < 50% across {len(gold_sessions)} fragment sessions (drift)"
    leak = " ⚠ possible leak: one session covers {:.0%} (≥80%) — may not discriminate".format(max_single) if max_single >= 0.8 else ""
    return True, f"union gold coverage {union_cov:.0%}, max single-session {max_single:.0%}{leak}"


def soft_validate_no_action_leak(
    conv: GeneratedConversation, spec: ScenarioSpec
) -> tuple[bool, str]:
    """Detect gold-action tokens leaking into non-gold (filler/trap) episodes.

    Agentic specs (S34) declare `gold_action_tokens` — distinctive strings (env vars,
    CLI flags, command names) that uniquely identify the gold action. If any non-gold
    episode contains those strings, the ablation can be defeated: an experience-only
    system can extract `[experience] agent ran X with <gold_token>` from the filler and
    answer the gold question wrongly-but-correctly. T1 lesson: Minimax borrowed
    `-p no:cacheprovider` into a filler pytest invocation; we hand-patched it.

    WARNING-only (returns (True/False, message)): hard-failing would re-trigger
    expensive generation; better to surface the leak so the human can either hand-edit
    the work fixture or regenerate. Returns False ONLY when leaks are present (so the
    caller can decide policy).
    """
    tokens = getattr(spec, "gold_action_tokens", None) or []
    if not tokens or getattr(spec, "workload", "chat") != "agentic":
        return True, "no gold_action_tokens declared (skip)"

    gold_ids = set(conv.gold_session_ids)
    leaks: list[tuple[str, str]] = []  # (session_id, leaked_token)
    for sess in conv.sessions:
        if sess.session_id in gold_ids:
            continue
        body = " ".join(m.content for m in sess.messages)
        for tok in tokens:
            if tok in body:
                leaks.append((sess.session_id, tok))

    if not leaks:
        return True, f"no gold-action leak across {len(conv.sessions) - len(gold_ids)} non-gold episodes"
    summary = "; ".join(f"{sid}: {tok!r}" for sid, tok in leaks)
    return False, f"⚠ gold-action leak in non-gold episodes — {summary}"


async def generate_conversation(
    spec: ScenarioSpec,
    llm: _Caller,
    *,
    gold_tokens: int = 16000,
    filler_tokens: int = 8000,
    temperature: float = 0.7,
    last_k_verbatim: int = 2,
    max_retries: int = 3,
) -> GeneratedConversation:
    """Generate the conversation session-by-session (one LLM call per session).

    Consistency across calls is maintained by (1) `spec.shared_context` injected into every
    prompt, (2) model-emitted one-line recaps of older sessions, and (3) the last
    `last_k_verbatim` sessions passed verbatim for tight local continuity.

    Each session call is retried up to `max_retries` times on transient failures (empty/
    malformed output, truncation, API hiccup); per-session progress is logged.
    """
    plan = spec.session_plan
    total = plan.total_sessions
    dates = plan.dates or [None] * total

    sessions: list[GeneratedSession] = []
    recaps: list[str] = []  # aligned to session index
    for i in range(total):
        role = session_role(spec, i)
        split = max(0, i - last_k_verbatim)
        older_recaps = recaps[:split]
        recent_sessions = [(f"Session {j}", sessions[j].messages) for j in range(split, i)]
        prompt = build_session_prompt(spec, i, role, older_recaps, recent_sessions)
        max_tokens = gold_tokens if role in ("gold", "trap") else filler_tokens

        model_recap: str | None = None
        messages: list[Message] | None = None
        last_exc: Exception | None = None
        for attempt in range(1, max_retries + 1):
            print(f"    [{spec.scenario_id}] session {i + 1}/{total} ({role}) attempt {attempt}/{max_retries} ...")
            try:
                raw = await llm.call(
                    messages=[{"role": "user", "content": prompt}],
                    temperature=temperature,
                    max_completion_tokens=max_tokens,
                )
                model_recap, messages = parse_session_response(str(raw or ""))
                print(f"    [{spec.scenario_id}] session {i + 1}/{total} ({role}) ok — {len(messages)} msgs")
                break
            except Exception as exc:  # noqa: BLE001 — retry any transient generation failure
                last_exc = exc
                print(f"    [{spec.scenario_id}] session {i + 1}/{total} ({role}) attempt {attempt} FAILED: {type(exc).__name__}: {exc}")
        if messages is None:
            raise RuntimeError(
                f"session {i} of {spec.scenario_id} failed after {max_retries} attempts: {last_exc}"
            ) from last_exc

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
