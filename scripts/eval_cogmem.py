from __future__ import annotations

import argparse
import json
import logging
import os
import re
import time
import uuid
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Callable

import requests

logging.basicConfig(level=logging.DEBUG, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger(__name__)


JsonDict = dict[str, Any]


@dataclass(frozen=True)
class EvalLLMConfig:
    provider: str
    model: str
    api_key: str
    base_url: str
    timeout_seconds: float
    max_completion_tokens: int


@dataclass(frozen=True)
class AblationProfile:
    profile_id: str
    description: str
    enabled_networks: tuple[str, ...]
    recall_fact_types: tuple[str, ...]
    adaptive_router_enabled: bool
    sum_activation_enabled: bool


ABLATION_PROFILES: dict[str, AblationProfile] = {
    "E1": AblationProfile(
        profile_id="E1",
        description="Baseline rebuilt behavior",
        enabled_networks=("world", "experience", "opinion"),
        recall_fact_types=("world", "experience", "opinion"),
        adaptive_router_enabled=False,
        sum_activation_enabled=False,
    ),
    "E2": AblationProfile(
        profile_id="E2",
        description="E1 + Habit network",
        enabled_networks=("world", "experience", "opinion", "habit"),
        recall_fact_types=("world", "experience", "opinion", "habit"),
        adaptive_router_enabled=False,
        sum_activation_enabled=False,
    ),
    "E3": AblationProfile(
        profile_id="E3",
        description="E1 + Intention network",
        enabled_networks=("world", "experience", "opinion", "intention"),
        recall_fact_types=("world", "experience", "opinion", "intention"),
        adaptive_router_enabled=False,
        sum_activation_enabled=False,
    ),
    "E4": AblationProfile(
        profile_id="E4",
        description="E1 + Action-Effect network",
        enabled_networks=("world", "experience", "opinion", "action_effect"),
        recall_fact_types=("world", "experience", "opinion", "action_effect"),
        adaptive_router_enabled=False,
        sum_activation_enabled=False,
    ),
    "E5": AblationProfile(
        profile_id="E5",
        description="E1 + Adaptive query routing",
        enabled_networks=("world", "experience", "opinion", "habit", "intention", "action_effect"),
        recall_fact_types=("world", "experience", "opinion", "habit", "intention", "action_effect"),
        adaptive_router_enabled=True,
        sum_activation_enabled=False,
    ),
    "E6": AblationProfile(
        profile_id="E6",
        description="E1 + SUM activation",
        enabled_networks=("world", "experience", "opinion", "habit", "intention", "action_effect"),
        recall_fact_types=("world", "experience", "opinion", "habit", "intention", "action_effect"),
        adaptive_router_enabled=False,
        sum_activation_enabled=True,
    ),
    "E7": AblationProfile(
        profile_id="E7",
        description="Full CogMem",
        enabled_networks=("world", "experience", "opinion", "habit", "intention", "action_effect"),
        recall_fact_types=("world", "experience", "opinion", "habit", "intention", "action_effect"),
        adaptive_router_enabled=True,
        sum_activation_enabled=True,
    ),
}


SHORT_DIALOGUE_FIXTURE: JsonDict = {
    "name": "short_conversation_v1",
    "turns": [
        "USER: Mình đang lên kế hoạch học Rust trước Q3 để tối ưu inference server.",
        "ASSISTANT: Bạn có deadline cụ thể không?",
        "USER: Deadline là cuối tháng 9. Khi latency vượt 100ms thì mình thường chuyển sang int8 và latency giảm còn khoảng 45ms.",
    ],
    "questions": [
        {
            "id": "q1",
            "query": "User đang có kế hoạch gì và deadline khi nào?",
            "expected_keywords": ["rust", "q3", "tháng 9"],
            "gold_answer": "User có kế hoạch học Rust trước Q3, deadline cuối tháng 9.",
        },
        {
            "id": "q2",
            "query": "Khi latency cao thì user làm gì và kết quả ra sao?",
            "expected_keywords": ["latency", "int8", "45ms"],
            "gold_answer": "Khi latency vượt 100ms user chuyển sang int8 và latency giảm còn khoảng 45ms.",
        },
    ],
}


def _env_first(*keys: str, default: str | None = None) -> str | None:
    for key in keys:
        value = os.getenv(key)
        if value is not None and value.strip():
            return value.strip()
    return default


def _to_float(value: str | None, default: float) -> float:
    if value is None:
        return default
    try:
        return float(value)
    except ValueError:
        return default


def _to_int(value: str | None, default: int) -> int:
    if value is None:
        return default
    try:
        return int(value)
    except ValueError:
        return default


def _normalize_text(text: str) -> str:
    return re.sub(r"\s+", " ", text.lower()).strip()


def _build_chat_url(base_url: str) -> str:
    trimmed = base_url.rstrip("/")
    if trimmed.endswith("/chat/completions"):
        return trimmed
    if trimmed.endswith("/v1"):
        return f"{trimmed}/chat/completions"
    return f"{trimmed}/v1/chat/completions"


def resolve_eval_llm_config() -> EvalLLMConfig:
    eval_model = _env_first("COGMEM_API_EVAL_LLM_MODEL", default=None)
    eval_base_url = _env_first("COGMEM_API_EVAL_LLM_BASE_URL", default=None)

    if eval_model is None or eval_base_url is None:
        raise ValueError(
            "Judge LLM must be configured independently from retain LLM. "
            "Set both COGMEM_API_EVAL_LLM_MODEL and COGMEM_API_EVAL_LLM_BASE_URL env vars. "
            "Judge LLM should be >= 7B (e.g. Qwen3-7B). "
            f"Got: COGMEM_API_EVAL_LLM_MODEL={eval_model}, COGMEM_API_EVAL_LLM_BASE_URL={eval_base_url}"
        )

    provider = _env_first("COGMEM_API_EVAL_LLM_PROVIDER", default="openai")
    api_key = _env_first("COGMEM_API_EVAL_LLM_API_KEY", default="ollama")
    timeout_seconds = _to_float(_env_first("COGMEM_API_EVAL_LLM_TIMEOUT", default="600"), default=600.0)
    max_completion_tokens = _to_int(_env_first("COGMEM_API_EVAL_MAX_COMPLETION_TOKENS", default="13000"), default=13000)

    return EvalLLMConfig(
        provider=provider or "openai",
        model=eval_model,
        api_key=api_key or "ollama",
        base_url=eval_base_url,
        timeout_seconds=max(1.0, timeout_seconds),
        max_completion_tokens=max(64, max_completion_tokens),
    )


def resolve_api_base_url(cli_value: str | None = None) -> str:
    if cli_value:
        return cli_value.rstrip("/")
    return (_env_first("COGMEM_API_EVAL_LLM_BASE_URL", default="http://localhost:8888") or "http://localhost:8888").rstrip("/")


def post_json(url: str, payload: JsonDict, timeout_seconds: float) -> JsonDict:
    response = requests.post(url, json=payload, timeout=timeout_seconds)
    response.raise_for_status()
    return response.json()


def call_openai_chat(
    llm_config: EvalLLMConfig,
    messages: list[dict[str, str]],
    max_completion_tokens: int | None = None,
) -> str:
    sys_preview = next(
        (m["content"][:60] for m in messages if m.get("role") == "system"), ""
    )
    logger.debug(
        "LLM call model=%s max_tokens=%s system=%.60s",
        llm_config.model,
        max_completion_tokens,
        sys_preview,
    )
    payload: JsonDict = {
        "model": llm_config.model,
        "messages": messages,
        "temperature": 0.1,
    }
    if max_completion_tokens is not None:
        payload["max_completion_tokens"] = max_completion_tokens

    headers = {"Content-Type": "application/json"}
    if llm_config.api_key:
        headers["Authorization"] = f"Bearer {llm_config.api_key}"

    response = requests.post(
        _build_chat_url(llm_config.base_url),
        json=payload,
        headers=headers,
        timeout=llm_config.timeout_seconds,
    )
    response.raise_for_status()
    response_json = response.json()
    choices = response_json.get("choices") or []
    if not choices:
        logger.warning("LLM returned no choices. Response: %.300s", response_json)
        return ""
    return str((choices[0].get("message") or {}).get("content") or "")


def _make_benchmark_fixture(path: str, source: str) -> JsonDict:
    with open(path, encoding="utf-8") as f:
        data = json.load(f)

    all_turns: list[str] = []
    questions: list[JsonDict] = []
    fixture_sessions: list[tuple[str, list[str]]] = []
    seen_session_ids: set[str] = set()

    if source == "longmemeval":
        type_map = {
            "multi-session": "multi-session",
            "knowledge-update": "knowledge-update",
            "temporal-reasoning": "temporal",
            "abstention": "abstention",
            "prospective": "prospective",
            "single-session-preference": "preference",
            "single-session-user": "single-session",
        }
        for item in data:
            category = type_map.get(item.get("question_type", ""), item.get("question_type", "unknown"))
            sessions_raw = item.get("haystack_sessions", [])
            haystack_ids = item.get("haystack_session_ids", [])
            sessions_with_ids: list[tuple[str, list[str]]] = []
            for sess_idx, sess in enumerate(sessions_raw):
                sess_id = haystack_ids[sess_idx] if sess_idx < len(haystack_ids) else f"session_{sess_idx + 1}"
                sess_turns = []
                if isinstance(sess, list):
                    for t in sess:
                        content = t.get("content") if isinstance(t, dict) else str(t) if isinstance(t, str) else ""
                        if content:
                            sess_turns.append(content)
                elif isinstance(sess, dict):
                    c = sess.get("content", "")
                    if c:
                        sess_turns.append(c)
                elif isinstance(sess, str) and sess:
                    sess_turns.append(sess)
                if sess_turns:
                    sessions_with_ids.append((sess_id, sess_turns))
            flat_turns = [t for _, t in sessions_with_ids for t in t]
            all_turns.extend(flat_turns)
            questions.append({
                "id": str(item.get("question_id", "")),
                "query": item.get("question", ""),
                "gold_answer": item.get("answer", ""),
                "gold_session_ids": item.get("answer_session_ids", []),
                "category": category,
                "turns": flat_turns,
                "_sessions": sessions_with_ids,
            })

    elif source == "locomo":
        cat_map = {1: "single-hop", 2: "multi-hop", 3: "temporal", 4: "preference", 5: "causal"}
        qa_counter = 0
        for conv in data:
            conversation = conv.get("conversation", {})
            sessions_with_ids: list[tuple[str, list[str]]] = []
            if isinstance(conversation, dict):
                for key in sorted(conversation.keys()):
                    if key.endswith("_date_time"):
                        continue
                    if key in ("speaker_a", "speaker_b"):
                        continue
                    val = conversation[key]
                    sess_id = None
                    if key.startswith("session_"):
                        n = key.split("_")[1]
                        sess_id = f"D{n}"
                    elif key.startswith("D"):
                        sess_id = key
                    if sess_id is None:
                        continue
                    sess_turns = []
                    if isinstance(val, list):
                        for t in val:
                            content = t.get("text") if isinstance(t, dict) else ""
                            if content:
                                sess_turns.append(content)
                    elif isinstance(val, str) and val:
                        sess_turns.append(val)
                    if sess_turns:
                        sessions_with_ids.append((sess_id, sess_turns))
            elif isinstance(conversation, list):
                sess_turns = []
                for t in conversation:
                    content = t.get("text") if isinstance(t, dict) else str(t) if isinstance(t, str) else ""
                    if content:
                        sess_turns.append(content)
                if sess_turns:
                    sessions_with_ids.append(("D1", sess_turns))
            elif isinstance(conversation, str) and conversation:
                sessions_with_ids.append(("D1", [conversation]))
            flat_turns = [t for _, t in sessions_with_ids for t in t]
            all_turns.extend(flat_turns)

            for qa in conv.get("qa", []):
                qa_counter += 1
                cat_int = qa.get("category", 0)
                evidence_list = qa.get("evidence", [])
                gold_session_ids = []
                for ev in evidence_list:
                    ev_str = str(ev)
                    if ":" in ev_str:
                        doc_part = ev_str.split(":")[0]
                        if doc_part:
                            gold_session_ids.append(doc_part)
                    elif ev_str:
                        gold_session_ids.append(ev_str)
                questions.append({
                    "id": f"locomo_q{qa_counter}",
                    "query": qa.get("question", ""),
                    "gold_answer": qa.get("answer", ""),
                    "gold_session_ids": gold_session_ids,
                    "category": cat_map.get(cat_int, f"category_{cat_int}"),
                    "turns": flat_turns,
                    "_sessions": sessions_with_ids,
                })

    for q_sessions in (q.get("_sessions", []) for q in questions):
        for sess_id, sess_turns in q_sessions:
            if sess_id not in seen_session_ids:
                fixture_sessions.append((sess_id, sess_turns))
                seen_session_ids.add(sess_id)

    return {"name": f"{source}_benchmark", "turns": all_turns, "questions": questions, "_sessions": fixture_sessions}


def get_fixture(name: str, fixture_path: str | None = None) -> JsonDict:
    if name == "short":
        return SHORT_DIALOGUE_FIXTURE
    if name == "longmemeval":
        path = fixture_path or str(Path(__file__).parent.parent / "data" / "longmemeval_s_distilled_small.json")
        return _make_benchmark_fixture(path, "longmemeval")
    if name == "locomo":
        path = fixture_path or str(Path(__file__).parent.parent / "data" / "locomo_distilled.json")
        return _make_benchmark_fixture(path, "locomo")
    raise ValueError(f"Unsupported fixture: {name}")


def build_recall_payload(profile: AblationProfile, query: str) -> JsonDict:
    payload: JsonDict = {
        "query": query,
        "types": list(profile.recall_fact_types),
        "budget": "mid",
        "max_tokens": 1024,
        "trace": True,
        "adaptive_router": profile.adaptive_router_enabled,
        "graph_retriever": "bfs" if profile.sum_activation_enabled else "link_expansion",
    }
    return payload


def _keyword_recall_metrics(expected_keywords: list[str] | None, recall_text: str) -> JsonDict:
    if not expected_keywords:
        return {"matched_keywords": [], "keyword_total": 0, "keyword_coverage": 0.0, "strict_hit": False}
    normalized_text = _normalize_text(recall_text)
    matched = [keyword for keyword in expected_keywords if _normalize_text(keyword) in normalized_text]
    coverage = float(len(matched)) / float(len(expected_keywords) or 1)
    return {
        "matched_keywords": matched,
        "keyword_total": len(expected_keywords),
        "keyword_coverage": coverage,
        "strict_hit": len(matched) == len(expected_keywords),
    }


def _safe_parse_json(text: str) -> JsonDict | None:
    stripped = text.strip()
    if not stripped:
        return None
    # Strip <think>...</think> blocks emitted by reasoning models (R1, minimax, etc.)
    stripped = re.sub(r"<think>.*?</think>", "", stripped, flags=re.DOTALL).strip()
    # Strip markdown code fences (```json ... ``` or ``` ... ```)
    if stripped.startswith("```"):
        stripped = re.sub(r"^```(?:json)?\s*", "", stripped).strip()
        stripped = re.sub(r"\s*```\s*$", "", stripped).strip()
    try:
        parsed = json.loads(stripped)
    except json.JSONDecodeError:
        return None
    if isinstance(parsed, dict):
        return parsed
    return None


def retain_fixture(
    api_base_url: str,
    bank_id: str,
    fixture: JsonDict,
    *,
    post_json_fn: Callable[[str, JsonDict, float], JsonDict],
    timeout_seconds: float,
) -> JsonDict:
    sessions = fixture.get("_sessions")
    if sessions:
        items = []
        for session_id, turns in sessions:
            for turn_content in turns:
                items.append({"content": turn_content, "document_id": session_id})
    else:
        items = [{"content": turn} for turn in fixture["turns"]]
    return post_json_fn(
        f"{api_base_url}/v1/default/banks/{bank_id}/memories",
        {"items": items, "async": False},
        timeout_seconds,
    )


def _build_recall_at_k(
    recall_results: list[JsonDict],
    gold_keywords: list[str] | None,
    k: int,
) -> JsonDict:
    if not gold_keywords:
        return {"recall_at_k": None, "precision_at_k": None}
    top_k = recall_results[:k]
    top_k_text = " ".join(str(r.get("text", "") or "") for r in top_k).lower()
    normalized_top_k = _normalize_text(top_k_text)
    recalled = sum(1 for kw in gold_keywords if _normalize_text(kw) in normalized_top_k)
    recall = recalled / len(gold_keywords)
    precision = recalled / (k * len(gold_keywords)) if k > 0 else 0.0
    return {"recall_at_k": recall, "precision_at_k": precision, "recalled_keywords": recalled, "total_gold_keywords": len(gold_keywords)}


def _build_session_recall_at_k(
    recall_results: list[JsonDict],
    gold_session_ids: list[str] | None,
    k: int,
) -> JsonDict:
    if not gold_session_ids:
        return {"recall_at_k": None, "precision_at_k": None}
    gold_set = set(gold_session_ids)
    top_k = recall_results[:k]
    matched = [r.get("document_id") for r in top_k if r.get("document_id") in gold_set]
    recall = 1.0 if matched else 0.0
    precision = len(matched) / k if k > 0 else 0.0
    return {"recall_at_k": recall, "precision_at_k": precision, "matched_session_count": len(matched), "total_gold_sessions": len(gold_session_ids)}


def _per_category_stats(
    questions: list[JsonDict],
    per_question: list[JsonDict],
    is_full_pipeline: bool,
) -> dict[str, JsonDict]:
    cat_stats: dict[str, dict] = {}
    for q, pq in zip(questions, per_question):
        cat = q.get("category", "unknown")
        if cat not in cat_stats:
            cat_stats[cat] = {"correct": 0, "total": 0, "score_sum": 0.0, "recall_cov_sum": 0.0, "recall_strict": 0}
        cat_stats[cat]["total"] += 1
        cat_stats[cat]["recall_cov_sum"] += float(pq["recall_metrics"]["keyword_coverage"])
        cat_stats[cat]["recall_strict"] += 1 if pq["recall_metrics"]["strict_hit"] else 0
        if is_full_pipeline:
            cat_stats[cat]["correct"] += 1 if pq["judge"]["correct"] else 0
            cat_stats[cat]["score_sum"] += float(pq["judge"]["score"])

    result = {}
    for cat, stats in cat_stats.items():
        t = stats["total"]
        entry: JsonDict = {
            "count": t,
            "recall_keyword_accuracy": stats["recall_cov_sum"] / t,
            "recall_strict_accuracy": float(stats["recall_strict"]) / t,
        }
        if is_full_pipeline:
            entry["judge_accuracy"] = float(stats["correct"]) / t
            entry["judge_score_mean"] = stats["score_sum"] / t
        result[cat] = entry
    return result


def run_recall_only_pipeline(
    api_base_url: str,
    bank_id: str,
    profile: AblationProfile,
    fixture: JsonDict,
    *,
    skip_retain: bool,
    timeout_seconds: float,
    post_json_fn: Callable[[str, JsonDict, float], JsonDict] = post_json,
) -> JsonDict:
    started_at = time.time()

    retain_result: JsonDict | None = None
    if not skip_retain:
        retain_result = retain_fixture(
            api_base_url,
            bank_id,
            fixture,
            post_json_fn=post_json_fn,
            timeout_seconds=timeout_seconds,
        )

    per_question: list[JsonDict] = []
    strict_hits = 0
    coverage_sum = 0.0
    reranker_used = False

    for question in fixture["questions"]:
        recall_payload = build_recall_payload(profile, question["query"])
        recall_json = post_json_fn(
            f"{api_base_url}/v1/default/banks/{bank_id}/memories/recall",
            recall_payload,
            timeout_seconds,
        )

        results = recall_json.get("results") or []
        if not reranker_used:
            reranker_used = any(float(r.get("cross_encoder_score", 0)) > 0 for r in results)
        joined_text = "\n".join(str(item.get("text") or "") for item in results)
        metrics = _keyword_recall_metrics(question.get("expected_keywords"), joined_text)
        strict_hits += 1 if metrics["strict_hit"] else 0
        coverage_sum += float(metrics["keyword_coverage"])
        gold_kw = question.get("expected_keywords")
        gold_sids = question.get("gold_session_ids")
        recall_at_5 = _build_recall_at_k(results, gold_kw, 5)
        recall_at_10 = _build_recall_at_k(results, gold_kw, 10)
        session_recall_at_5 = _build_session_recall_at_k(results, gold_sids, 5)
        session_recall_at_10 = _build_session_recall_at_k(results, gold_sids, 10)

        per_question.append(
            {
                "question_id": question["id"],
                "query": question["query"],
                "category": question.get("category"),
                "expected_keywords": question.get("expected_keywords"),
                "gold_session_ids": gold_sids,
                "recall_result_count": len(results),
                "recall_metrics": metrics,
                "recall_at_5": recall_at_5,
                "recall_at_10": recall_at_10,
                "session_recall_at_5": session_recall_at_5,
                "session_recall_at_10": session_recall_at_10,
            }
        )

    total_questions = len(fixture["questions"])
    per_cat = _per_category_stats(fixture["questions"], per_question, is_full_pipeline=False)
    recall_at_5_vals = [pq["recall_at_5"]["recall_at_k"] for pq in per_question if pq["recall_at_5"]["recall_at_k"] is not None]
    recall_at_10_vals = [pq["recall_at_10"]["recall_at_k"] for pq in per_question if pq["recall_at_10"]["recall_at_k"] is not None]
    sess_recall_at_5_vals = [pq["session_recall_at_5"]["recall_at_k"] for pq in per_question if pq["session_recall_at_5"]["recall_at_k"] is not None]
    sess_recall_at_10_vals = [pq["session_recall_at_10"]["recall_at_k"] for pq in per_question if pq["session_recall_at_10"]["recall_at_k"] is not None]
    return {
        "pipeline": "recall_only",
        "profile": asdict(profile),
        "fixture": fixture["name"],
        "bank_id": bank_id,
        "ablation_hooks": {
            "enabled_networks": list(profile.enabled_networks),
            "adaptive_router_enabled": profile.adaptive_router_enabled,
            "sum_activation_enabled": profile.sum_activation_enabled,
            "recall_fact_types": list(profile.recall_fact_types),
        },
        "reranker_used": reranker_used,
        "retain": retain_result,
        "metrics": {
            "question_count": total_questions,
            "recall_keyword_accuracy": coverage_sum / float(total_questions or 1),
            "recall_strict_accuracy": float(strict_hits) / float(total_questions or 1),
            "recall_at_5_mean": sum(recall_at_5_vals) / len(recall_at_5_vals) if recall_at_5_vals else None,
            "recall_at_10_mean": sum(recall_at_10_vals) / len(recall_at_10_vals) if recall_at_10_vals else None,
            "session_recall_at_5_mean": sum(sess_recall_at_5_vals) / len(sess_recall_at_5_vals) if sess_recall_at_5_vals else None,
            "session_recall_at_10_mean": sum(sess_recall_at_10_vals) / len(sess_recall_at_10_vals) if sess_recall_at_10_vals else None,
            "duration_seconds": time.time() - started_at,
        },
        "per_category_metrics": per_cat,
        "questions": per_question,
    }


def _build_generation_prompt(query: str, recall_results: list[JsonDict]) -> str:
    evidence = []
    for idx, result in enumerate(recall_results, start=1):
        snippet = result.get("raw_snippet") or result.get("text", "")
        evidence.append(f"[{idx}] {snippet}")
    evidence_block = "\n".join(evidence) if evidence else "[No evidence]"
    return (
        "Answer the question using ONLY the recall evidence below.\n"
        "- Cite evidence by index, e.g. [1] or [2].\n"
        "- If the evidence does not contain the answer, say explicitly that the information is not available.\n"
        "- Do not fabricate facts not present in the evidence.\n"
        "- Match the language of the question.\n\n"
        f"Question: {query}\n\n"
        f"Recall Evidence:\n{evidence_block}\n"
    )


def _judge_system_prompt(category: str | None) -> str:
    cat = (category or "").lower()

    if cat in ("temporal", "temporal-reasoning"):
        return (
            "You are an evaluation judge for a memory system.\n"
            "I will give you a question, a correct answer, and a model response.\n"
            "Set correct=true if the response contains the correct answer or equivalent.\n"
            "Do NOT penalize off-by-one errors for counts of days/weeks/months "
            "(e.g. 18 days vs 19 days is still correct).\n"
            "Set correct=false if the response contains only a subset of required information.\n"
            'Return strict JSON: {"correct": bool, "score": float 0..1, "reason": string}'
        )

    if cat == "knowledge-update":
        return (
            "You are an evaluation judge for a memory system.\n"
            "I will give you a question, a correct answer, and a model response.\n"
            "Set correct=true if the response contains the correct (updated) answer.\n"
            "If the response mentions outdated information alongside the updated answer, it is still correct.\n"
            'Return strict JSON: {"correct": bool, "score": float 0..1, "reason": string}'
        )

    if cat in ("preference", "single-session-preference"):
        return (
            "You are an evaluation judge for a memory system.\n"
            "I will give you a question about user preferences, a desired response, and a model response.\n"
            "Set correct=true if the model response satisfies the desired response.\n"
            "The model does not need to reflect every point — it is correct as long as it "
            "recalls and correctly uses the user's personal information.\n"
            'Return strict JSON: {"correct": bool, "score": float 0..1, "reason": string}'
        )

    if cat == "abstention":
        return (
            "You are an evaluation judge for a memory system.\n"
            "I will give you a question, a correct answer, and a model response.\n"
            "If the gold answer indicates the information was not mentioned "
            "(e.g. 'You did not mention this'), and the model says it cannot answer or does not know, "
            "set correct=true. Set correct=false if the model fabricates an answer.\n"
            'Return strict JSON: {"correct": bool, "score": float 0..1, "reason": string}'
        )

    # Default: single-session, multi-session, single-hop, multi-hop, causal, prospective, unknown
    return (
        "You are an evaluation judge for a memory recall system.\n"
        "Your task: label the model's answer as correct or incorrect.\n"
        "You will be given a question, a gold (ground truth) answer, and a generated answer.\n"
        "Rules:\n"
        "- Set correct=true if the generated answer contains or is equivalent to the gold answer.\n"
        "- Set correct=true if it contains all intermediate steps needed to reach the gold answer.\n"
        "- Set correct=false if it contains only a SUBSET of required information.\n"
        "- The generated answer may be longer — be generous: if it touches the same topic as the gold, count as correct.\n"
        "- For time questions: if it refers to the same date/period (even different format), count as correct.\n"
        'Return strict JSON: {"correct": bool, "score": float 0..1, "reason": string}'
    )


def _judge_answer(
    llm_config: EvalLLMConfig,
    question: str,
    gold_answer: str,
    predicted_answer: str,
    *,
    category: str | None = None,
    llm_call_fn: Callable[[EvalLLMConfig, list[dict[str, str]], int | None], str],
) -> JsonDict:
    judge_prompt = _judge_system_prompt(category)
    user_prompt = (
        f"Question: {question}\n"
        f"Gold Answer: {gold_answer}\n"
        f"Predicted Answer: {predicted_answer}\n"
        "Return JSON only."
    )
    raw = llm_call_fn(
        llm_config,
        [{"role": "system", "content": judge_prompt}, {"role": "user", "content": user_prompt}],
        40000,
    )
    parsed = _safe_parse_json(raw)
    if not parsed:
        logger.warning("Judge LLM output could not be parsed as JSON. raw=%.500s", raw)
        return {
            "correct": False,
            "score": 0.0,
            "reason": "judge_output_not_json",
            "raw": raw,
        }

    score = parsed.get("score", 0.0)
    try:
        numeric_score = float(score)
    except (TypeError, ValueError):
        numeric_score = 0.0

    return {
        "correct": bool(parsed.get("correct", False)),
        "score": max(0.0, min(1.0, numeric_score)),
        "reason": str(parsed.get("reason", "")),
        "raw": raw,
    }


def run_full_pipeline(
    api_base_url: str,
    bank_id: str,
    profile: AblationProfile,
    fixture: JsonDict,
    llm_config: EvalLLMConfig,
    *,
    skip_retain: bool,
    timeout_seconds: float,
    post_json_fn: Callable[[str, JsonDict, float], JsonDict] = post_json,
    llm_call_fn: Callable[[EvalLLMConfig, list[dict[str, str]], int | None], str] = call_openai_chat,
) -> JsonDict:
    started_at = time.time()

    retain_result: JsonDict | None = None
    if not skip_retain:
        retain_result = retain_fixture(
            api_base_url,
            bank_id,
            fixture,
            post_json_fn=post_json_fn,
            timeout_seconds=timeout_seconds,
        )

    per_question: list[JsonDict] = []
    strict_hits = 0
    coverage_sum = 0.0
    judge_correct_count = 0
    judge_score_sum = 0.0
    reranker_used = False

    for question in fixture["questions"]:
        recall_payload = build_recall_payload(profile, question["query"])
        recall_json = post_json_fn(
            f"{api_base_url}/v1/default/banks/{bank_id}/memories/recall",
            recall_payload,
            timeout_seconds,
        )

        results = recall_json.get("results") or []
        if not reranker_used:
            reranker_used = any(float(r.get("cross_encoder_score", 0)) > 0 for r in results)
        joined_text = "\n".join(str(item.get("text") or "") for item in results)
        recall_metrics = _keyword_recall_metrics(question.get("expected_keywords"), joined_text)
        strict_hits += 1 if recall_metrics["strict_hit"] else 0
        coverage_sum += float(recall_metrics["keyword_coverage"])
        gold_kw = question.get("expected_keywords")
        gold_sids = question.get("gold_session_ids")
        recall_at_5 = _build_recall_at_k(results, gold_kw, 5)
        recall_at_10 = _build_recall_at_k(results, gold_kw, 10)
        session_recall_at_5 = _build_session_recall_at_k(results, gold_sids, 5)
        session_recall_at_10 = _build_session_recall_at_k(results, gold_sids, 10)

        generation_prompt = _build_generation_prompt(question["query"], results)
        generated_answer = llm_call_fn(
            llm_config,
            [
                {"role": "system", "content": "You are a memory assistant. Answer questions based strictly on provided evidence. Be concise and accurate."},
                {"role": "user", "content": generation_prompt},
            ],
            llm_config.max_completion_tokens,
        )

        judge = _judge_answer(
            llm_config,
            question=question["query"],
            gold_answer=question["gold_answer"],
            predicted_answer=generated_answer,
            category=question.get("category"),
            llm_call_fn=llm_call_fn,
        )

        judge_correct_count += 1 if judge["correct"] else 0
        judge_score_sum += float(judge["score"])

        per_question.append(
            {
                "question_id": question["id"],
                "query": question["query"],
                "category": question.get("category"),
                "gold_answer": question["gold_answer"],
                "gold_session_ids": gold_sids,
                "generated_answer": generated_answer,
                "recall_result_count": len(results),
                "recall_metrics": recall_metrics,
                "recall_at_5": recall_at_5,
                "recall_at_10": recall_at_10,
                "session_recall_at_5": session_recall_at_5,
                "session_recall_at_10": session_recall_at_10,
                "judge": judge,
            }
        )

    total_questions = len(fixture["questions"])
    per_cat = _per_category_stats(fixture["questions"], per_question, is_full_pipeline=True)
    recall_at_5_vals = [pq["recall_at_5"]["recall_at_k"] for pq in per_question if pq["recall_at_5"]["recall_at_k"] is not None]
    recall_at_10_vals = [pq["recall_at_10"]["recall_at_k"] for pq in per_question if pq["recall_at_10"]["recall_at_k"] is not None]
    sess_recall_at_5_vals = [pq["session_recall_at_5"]["recall_at_k"] for pq in per_question if pq["session_recall_at_5"]["recall_at_k"] is not None]
    sess_recall_at_10_vals = [pq["session_recall_at_10"]["recall_at_k"] for pq in per_question if pq["session_recall_at_10"]["recall_at_k"] is not None]
    return {
        "pipeline": "full_e2e",
        "profile": asdict(profile),
        "fixture": fixture["name"],
        "bank_id": bank_id,
        "ablation_hooks": {
            "enabled_networks": list(profile.enabled_networks),
            "adaptive_router_enabled": profile.adaptive_router_enabled,
            "sum_activation_enabled": profile.sum_activation_enabled,
            "recall_fact_types": list(profile.recall_fact_types),
        },
        "llm_config": asdict(llm_config),
        "reranker_used": reranker_used,
        "retain": retain_result,
        "metrics": {
            "question_count": total_questions,
            "recall_keyword_accuracy": coverage_sum / float(total_questions or 1),
            "recall_strict_accuracy": float(strict_hits) / float(total_questions or 1),
            "judge_accuracy": float(judge_correct_count) / float(total_questions or 1),
            "judge_score_mean": judge_score_sum / float(total_questions or 1),
            "recall_at_5_mean": sum(recall_at_5_vals) / len(recall_at_5_vals) if recall_at_5_vals else None,
            "recall_at_10_mean": sum(recall_at_10_vals) / len(recall_at_10_vals) if recall_at_10_vals else None,
            "session_recall_at_5_mean": sum(sess_recall_at_5_vals) / len(sess_recall_at_5_vals) if sess_recall_at_5_vals else None,
            "session_recall_at_10_mean": sum(sess_recall_at_10_vals) / len(sess_recall_at_10_vals) if sess_recall_at_10_vals else None,
            "duration_seconds": time.time() - started_at,
        },
        "judge_accuracy_per_category": per_cat,
        "questions": per_question,
    }


def run_pipeline(
    pipeline: str,
    api_base_url: str,
    bank_id: str,
    profile_id: str,
    fixture_name: str,
    *,
    skip_retain: bool,
    timeout_seconds: float,
    post_json_fn: Callable[[str, JsonDict, float], JsonDict] = post_json,
    llm_call_fn: Callable[[EvalLLMConfig, list[dict[str, str]], int | None], str] = call_openai_chat,
    fixture_path: str | None = None,
    fixture_override: JsonDict | None = None,
) -> JsonDict:
    if profile_id not in ABLATION_PROFILES:
        raise ValueError(f"Unknown profile: {profile_id}")

    profile = ABLATION_PROFILES[profile_id]
    fixture = fixture_override if fixture_override is not None else get_fixture(fixture_name, fixture_path=fixture_path)

    if pipeline == "recall":
        return run_recall_only_pipeline(
            api_base_url,
            bank_id,
            profile,
            fixture,
            skip_retain=skip_retain,
            timeout_seconds=timeout_seconds,
            post_json_fn=post_json_fn,
        )

    if pipeline == "full":
        llm_config = resolve_eval_llm_config()
        return run_full_pipeline(
            api_base_url,
            bank_id,
            profile,
            fixture,
            llm_config,
            skip_retain=skip_retain,
            timeout_seconds=timeout_seconds,
            post_json_fn=post_json_fn,
            llm_call_fn=llm_call_fn,
        )

    raise ValueError(f"Unsupported pipeline: {pipeline}")


def _benchmark_item_as_fixture(fixture: JsonDict, idx: int) -> JsonDict:
    """Return a single-conversation mini-fixture from a benchmark fixture."""
    questions = fixture["questions"]
    if idx >= len(questions):
        raise IndexError(f"conv_index {idx} out of range (0..{len(questions) - 1})")
    q = questions[idx]
    sessions = q.get("_sessions", [])
    return {
        "name": fixture["name"],
        "turns": [t for _, sess_turns in sessions for t in sess_turns],
        "questions": [q],
        "_sessions": sessions,
    }


def _aggregate_checkpoints(ckpt_files: list[Path], profile_id: str, pipeline: str) -> JsonDict:
    """Merge per-conversation checkpoint files into one aggregate result."""
    all_results = [json.loads(f.read_text(encoding="utf-8")) for f in ckpt_files]
    all_per_question: list[JsonDict] = []
    for r in all_results:
        all_per_question.extend(r.get("questions", []))

    profile = ABLATION_PROFILES[profile_id]
    is_full = pipeline == "full"
    total = len(all_per_question)

    coverage_sum = sum(float(q["recall_metrics"]["keyword_coverage"]) for q in all_per_question)
    strict_hits = sum(1 for q in all_per_question if q["recall_metrics"]["strict_hit"])
    recall_at_5_vals = [q["recall_at_5"]["recall_at_k"] for q in all_per_question if q["recall_at_5"]["recall_at_k"] is not None]
    recall_at_10_vals = [q["recall_at_10"]["recall_at_k"] for q in all_per_question if q["recall_at_10"]["recall_at_k"] is not None]
    sess5_vals = [v for v in ((q.get("session_recall_at_5") or {}).get("recall_at_k") for q in all_per_question) if v is not None]
    sess10_vals = [v for v in ((q.get("session_recall_at_10") or {}).get("recall_at_k") for q in all_per_question) if v is not None]

    metrics: JsonDict = {
        "question_count": total,
        "conversation_count": len(all_results),
        "recall_keyword_accuracy": coverage_sum / (total or 1),
        "recall_strict_accuracy": float(strict_hits) / (total or 1),
        "recall_at_5_mean": sum(recall_at_5_vals) / len(recall_at_5_vals) if recall_at_5_vals else None,
        "recall_at_10_mean": sum(recall_at_10_vals) / len(recall_at_10_vals) if recall_at_10_vals else None,
        "session_recall_at_5_mean": sum(sess5_vals) / len(sess5_vals) if sess5_vals else None,
        "session_recall_at_10_mean": sum(sess10_vals) / len(sess10_vals) if sess10_vals else None,
        "duration_seconds": sum(r.get("metrics", {}).get("duration_seconds", 0.0) for r in all_results),
    }

    if is_full:
        judge_correct = sum(1 for q in all_per_question if (q.get("judge") or {}).get("correct"))
        judge_score_sum = sum(float((q.get("judge") or {}).get("score", 0.0)) for q in all_per_question)
        metrics["judge_accuracy"] = float(judge_correct) / (total or 1)
        metrics["judge_score_mean"] = judge_score_sum / (total or 1)

    per_cat = _per_category_stats(all_per_question, all_per_question, is_full)

    result: JsonDict = {
        "pipeline": "full_e2e" if is_full else "recall_only",
        "profile": asdict(profile),
        "fixture": all_results[0]["fixture"] if all_results else "benchmark",
        "aggregated_from_checkpoints": len(ckpt_files),
        "ablation_hooks": {
            "enabled_networks": list(profile.enabled_networks),
            "adaptive_router_enabled": profile.adaptive_router_enabled,
            "sum_activation_enabled": profile.sum_activation_enabled,
            "recall_fact_types": list(profile.recall_fact_types),
        },
        "metrics": metrics,
        "questions": all_per_question,
    }
    if is_full:
        result["judge_accuracy_per_category"] = per_cat
    else:
        result["per_category_metrics"] = per_cat
    return result


def save_eval_result(result: JsonDict, output_dir: Path) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    stamp = int(time.time() * 1000)  # millisecond precision to avoid collisions
    profile_id = str(result["profile"]["profile_id"])
    pipeline = str(result["pipeline"])
    file_path = output_dir / f"{profile_id}_{pipeline}_{stamp}.json"
    file_path.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    return file_path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="CogMem T6.3 evaluation harness")
    parser.add_argument("--pipeline", choices=["recall", "full", "both"], default="both")
    parser.add_argument("--profile", choices=sorted(ABLATION_PROFILES.keys()), default="E1")
    parser.add_argument("--fixture", choices=["short", "longmemeval", "locomo"], default="short")
    parser.add_argument("--fixture-path", default=None, help="Custom path to benchmark fixture JSON")
    parser.add_argument("--base-url", default=None, help="CogMem API base URL, example: http://localhost:8888")
    parser.add_argument("--bank-id", default=None)
    parser.add_argument("--skip-retain", action="store_true")
    parser.add_argument("--output-dir", default="logs/eval")
    parser.add_argument("--api-timeout", type=float, default=120.0)
    parser.add_argument(
        "--conv-index", type=int, default=None,
        help="Benchmark only: process only this conversation index (0-based) and save a checkpoint.",
    )
    parser.add_argument(
        "--checkpoint-dir", default=None,
        help="Benchmark only: directory for per-conversation checkpoints (default: {output-dir}/checkpoints).",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    api_base_url = resolve_api_base_url(args.base_url)

    bank_id_base = args.bank_id or f"COGMEM_EVAL_{args.profile.lower()}_{uuid.uuid4().hex[:8]}"
    output_dir = Path(args.output_dir)
    checkpoint_dir = Path(args.checkpoint_dir) if args.checkpoint_dir else output_dir / "checkpoints"
    pipelines = ["recall", "full"] if args.pipeline == "both" else [args.pipeline]

    if args.fixture in ("longmemeval", "locomo"):
        fixture = get_fixture(args.fixture, fixture_path=args.fixture_path)
        total_items = len(fixture["questions"])
        indices = [args.conv_index] if args.conv_index is not None else list(range(total_items))

        for idx in indices:
            for pipeline in pipelines:
                ckpt_path = checkpoint_dir / f"{args.profile}_{pipeline}_c{idx:03d}.json"
                if ckpt_path.exists():
                    print(f"[{pipeline}] conv={idx}/{total_items - 1} SKIPPED (checkpoint exists)")
                    continue
                conv_bank_id = f"{bank_id_base}_c{idx:03d}"
                mini = _benchmark_item_as_fixture(fixture, idx)
                result = run_pipeline(
                    pipeline=pipeline,
                    api_base_url=api_base_url,
                    bank_id=conv_bank_id,
                    profile_id=args.profile,
                    fixture_name=args.fixture,
                    skip_retain=args.skip_retain,
                    timeout_seconds=max(1.0, args.api_timeout),
                    fixture_override=mini,
                )
                checkpoint_dir.mkdir(parents=True, exist_ok=True)
                ckpt_path.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
                q0 = result["questions"][0] if result["questions"] else {}
                sess5 = (q0.get("session_recall_at_5") or {}).get("recall_at_k")
                print(
                    f"[{pipeline}] conv={idx}/{total_items - 1} "
                    f"recall_kw={result['metrics'].get('recall_keyword_accuracy', 0.0):.3f} "
                    f"sess_rec@5={'null' if sess5 is None else f'{sess5:.1f}'} "
                    f"ckpt={ckpt_path.as_posix()}"
                )

        if args.conv_index is None:
            for pipeline in pipelines:
                ckpt_files = sorted(checkpoint_dir.glob(f"{args.profile}_{pipeline}_c*.json"))
                if len(ckpt_files) == total_items:
                    agg = _aggregate_checkpoints(ckpt_files, args.profile, pipeline)
                    path = save_eval_result(agg, output_dir)
                    print(f"[{pipeline}] AGGREGATED {len(ckpt_files)} convs → {path.as_posix()}")
                else:
                    print(f"[{pipeline}] {len(ckpt_files)}/{total_items} checkpoints — run remaining to aggregate.")
        return

    written: list[Path] = []
    for pipeline in pipelines:
        result = run_pipeline(
            pipeline=pipeline,
            api_base_url=api_base_url,
            bank_id=bank_id_base,
            profile_id=args.profile,
            fixture_name=args.fixture,
            skip_retain=args.skip_retain,
            timeout_seconds=max(1.0, args.api_timeout),
            fixture_path=args.fixture_path,
        )
        file_path = save_eval_result(result, output_dir)
        written.append(file_path)
        print(
            f"[{pipeline}] profile={args.profile} recall_acc={result['metrics'].get('recall_keyword_accuracy', 0.0):.3f} "
            f"written={file_path.as_posix()}"
        )

    print("Completed T6.3 harness run.")
    for path in written:
        print(path.as_posix())


if __name__ == "__main__":
    main()
