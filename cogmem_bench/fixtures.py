"""Emit frozen GeneratedConversations as LongMemEval-distilled JSON.

The output matches the schema consumed by scripts/eval_cogmem.py
`_make_benchmark_fixture(path, "longmemeval")`, so the existing eval harness can run our
cases unchanged via `--fixture longmemeval --fixture-path <file> --conv-index N`.

Distilled item shape (per scripts/eval_cogmem.py lines 269-319):
  question_id, question, answer, answer_session_ids, question_type, question_date,
  haystack_sessions (list of sessions; each a list of {role,content} turns),
  haystack_session_ids (parallel), haystack_dates (parallel).
"""

from __future__ import annotations

import json
from pathlib import Path

from .schema import GeneratedConversation

JsonDict = dict[str, object]


def to_distilled_item(conv: GeneratedConversation) -> JsonDict:
    """Convert one frozen conversation to a LongMemEval-distilled item."""
    haystack_sessions: list[list[dict[str, str]]] = []
    haystack_ids: list[str] = []
    haystack_dates: list[str] = []
    for sess in conv.sessions:
        haystack_sessions.append([{"role": m.role, "content": m.content} for m in sess.messages])
        haystack_ids.append(sess.session_id)
        haystack_dates.append(sess.date or "")

    return {
        "question_id": conv.scenario_id,
        # question_type is used by the harness as the judge category; target_type keeps
        # it transparent in reports (falls through type_map to the raw string).
        "question_type": conv.target_type,
        "question": conv.question,
        "answer": conv.gold_answer,
        "answer_session_ids": list(conv.gold_session_ids),
        "question_date": conv.question_date or "",
        "haystack_sessions": haystack_sessions,
        "haystack_session_ids": haystack_ids,
        "haystack_dates": haystack_dates,
    }


def write_distilled_fixture(convs: list[GeneratedConversation], path: str | Path) -> Path:
    """Write a list of conversations to a distilled JSON fixture file (frozen benchmark)."""
    out = Path(path)
    out.parent.mkdir(parents=True, exist_ok=True)
    items = [to_distilled_item(c) for c in convs]
    out.write_text(json.dumps(items, ensure_ascii=False, indent=2), encoding="utf-8")
    return out
