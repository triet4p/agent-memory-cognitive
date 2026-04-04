from __future__ import annotations

import argparse
import json
import os
import re
import time
import uuid
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Callable

import requests


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
    provider = _env_first(
        "COGMEM_EVAL_LLM_PROVIDER",
        "COGMEM_API_LLM_PROVIDER",
        default="openai",
    )
    model = _env_first(
        "COGMEM_EVAL_LLM_MODEL",
        "COGMEM_API_LLM_MODEL",
        default="ministral3-3b",
    )
    base_url = _env_first(
        "COGMEM_EVAL_LLM_BASE_URL",
        "COGMEM_API_LLM_BASE_URL",
        default="http://localhost:11434/v1",
    )
    api_key = _env_first(
        "COGMEM_EVAL_LLM_API_KEY",
        "COGMEM_API_LLM_API_KEY",
        default="ollama",
    )
    timeout_seconds = _to_float(
        _env_first(
            "COGMEM_EVAL_LLM_TIMEOUT",
            "COGMEM_API_LLM_TIMEOUT",
            default="600",
        ),
        default=600.0,
    )
    max_completion_tokens = _to_int(
        _env_first(
            "COGMEM_EVAL_MAX_COMPLETION_TOKENS",
            "COGMEM_API_RETAIN_MAX_COMPLETION_TOKENS",
            default="13000",
        ),
        default=13000,
    )

    return EvalLLMConfig(
        provider=provider or "openai",
        model=model or "ministral3-3b",
        api_key=api_key or "ollama",
        base_url=base_url or "http://localhost:11434/v1",
        timeout_seconds=max(1.0, timeout_seconds),
        max_completion_tokens=max(64, max_completion_tokens),
    )


def resolve_api_base_url(cli_value: str | None = None) -> str:
    if cli_value:
        return cli_value.rstrip("/")
    return (_env_first("COGMEM_EVAL_BASE_URL", default="http://localhost:8888") or "http://localhost:8888").rstrip("/")


def post_json(url: str, payload: JsonDict, timeout_seconds: float) -> JsonDict:
    response = requests.post(url, json=payload, timeout=timeout_seconds)
    response.raise_for_status()
    return response.json()


def call_openai_chat(
    llm_config: EvalLLMConfig,
    messages: list[dict[str, str]],
    max_completion_tokens: int | None = None,
) -> str:
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
        return ""
    return str((choices[0].get("message") or {}).get("content") or "")


def get_fixture(name: str) -> JsonDict:
    if name != "short":
        raise ValueError(f"Unsupported fixture: {name}")
    return SHORT_DIALOGUE_FIXTURE


def build_recall_payload(profile: AblationProfile, query: str) -> JsonDict:
    payload: JsonDict = {
        "query": query,
        "types": list(profile.recall_fact_types),
        "budget": "mid",
        "max_tokens": 1024,
        "trace": True,
    }
    return payload


def _keyword_recall_metrics(expected_keywords: list[str], recall_text: str) -> JsonDict:
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
    if stripped.startswith("```"):
        stripped = stripped.split("\n", 1)[1] if "\n" in stripped else stripped[3:]
        if stripped.endswith("```"):
            stripped = stripped[:-3]
        stripped = stripped.strip()
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
    items = [{"content": turn} for turn in fixture["turns"]]
    return post_json_fn(
        f"{api_base_url}/v1/default/banks/{bank_id}/memories",
        {"items": items, "async": False},
        timeout_seconds,
    )


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

    for question in fixture["questions"]:
        recall_payload = build_recall_payload(profile, question["query"])
        recall_json = post_json_fn(
            f"{api_base_url}/v1/default/banks/{bank_id}/memories/recall",
            recall_payload,
            timeout_seconds,
        )

        results = recall_json.get("results") or []
        joined_text = "\n".join(str(item.get("text") or "") for item in results)
        metrics = _keyword_recall_metrics(question["expected_keywords"], joined_text)
        strict_hits += 1 if metrics["strict_hit"] else 0
        coverage_sum += float(metrics["keyword_coverage"])

        per_question.append(
            {
                "question_id": question["id"],
                "query": question["query"],
                "expected_keywords": question["expected_keywords"],
                "recall_result_count": len(results),
                "recall_metrics": metrics,
            }
        )

    total_questions = len(fixture["questions"])
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
        "retain": retain_result,
        "metrics": {
            "question_count": total_questions,
            "recall_keyword_accuracy": coverage_sum / float(total_questions or 1),
            "recall_strict_accuracy": float(strict_hits) / float(total_questions or 1),
            "duration_seconds": time.time() - started_at,
        },
        "questions": per_question,
    }


def _build_generation_prompt(query: str, recall_results: list[JsonDict]) -> str:
    evidence = []
    for idx, result in enumerate(recall_results, start=1):
        evidence.append(f"[{idx}] {result.get('text', '')}")
    evidence_block = "\n".join(evidence) if evidence else "[No evidence]"
    return (
        "Trả lời câu hỏi dựa trên bằng chứng recall bên dưới. "
        "Nếu thiếu bằng chứng, hãy nói rõ là chưa đủ thông tin.\n\n"
        f"Question: {query}\n"
        f"Recall Evidence:\n{evidence_block}\n"
    )


def _judge_answer(
    llm_config: EvalLLMConfig,
    question: str,
    gold_answer: str,
    predicted_answer: str,
    *,
    llm_call_fn: Callable[[EvalLLMConfig, list[dict[str, str]], int | None], str],
) -> JsonDict:
    judge_prompt = (
        "You are an evaluation judge. Compare predicted answer with gold answer. "
        "Return strict JSON with keys: correct (bool), score (float 0..1), reason (string)."
    )
    user_prompt = (
        f"Question: {question}\n"
        f"Gold Answer: {gold_answer}\n"
        f"Predicted Answer: {predicted_answer}\n"
        "Return JSON only."
    )
    raw = llm_call_fn(
        llm_config,
        [{"role": "system", "content": judge_prompt}, {"role": "user", "content": user_prompt}],
        512,
    )
    parsed = _safe_parse_json(raw)
    if not parsed:
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

    for question in fixture["questions"]:
        recall_payload = build_recall_payload(profile, question["query"])
        recall_json = post_json_fn(
            f"{api_base_url}/v1/default/banks/{bank_id}/memories/recall",
            recall_payload,
            timeout_seconds,
        )

        results = recall_json.get("results") or []
        joined_text = "\n".join(str(item.get("text") or "") for item in results)
        recall_metrics = _keyword_recall_metrics(question["expected_keywords"], joined_text)
        strict_hits += 1 if recall_metrics["strict_hit"] else 0
        coverage_sum += float(recall_metrics["keyword_coverage"])

        generation_prompt = _build_generation_prompt(question["query"], results)
        generated_answer = llm_call_fn(
            llm_config,
            [
                {"role": "system", "content": "You are a memory assistant. Answer in Vietnamese."},
                {"role": "user", "content": generation_prompt},
            ],
            llm_config.max_completion_tokens,
        )

        judge = _judge_answer(
            llm_config,
            question=question["query"],
            gold_answer=question["gold_answer"],
            predicted_answer=generated_answer,
            llm_call_fn=llm_call_fn,
        )

        judge_correct_count += 1 if judge["correct"] else 0
        judge_score_sum += float(judge["score"])

        per_question.append(
            {
                "question_id": question["id"],
                "query": question["query"],
                "gold_answer": question["gold_answer"],
                "generated_answer": generated_answer,
                "recall_result_count": len(results),
                "recall_metrics": recall_metrics,
                "judge": judge,
            }
        )

    total_questions = len(fixture["questions"])
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
        "retain": retain_result,
        "metrics": {
            "question_count": total_questions,
            "recall_keyword_accuracy": coverage_sum / float(total_questions or 1),
            "recall_strict_accuracy": float(strict_hits) / float(total_questions or 1),
            "judge_accuracy": float(judge_correct_count) / float(total_questions or 1),
            "judge_score_mean": judge_score_sum / float(total_questions or 1),
            "duration_seconds": time.time() - started_at,
        },
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
) -> JsonDict:
    if profile_id not in ABLATION_PROFILES:
        raise ValueError(f"Unknown profile: {profile_id}")

    profile = ABLATION_PROFILES[profile_id]
    fixture = get_fixture(fixture_name)

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


def save_eval_result(result: JsonDict, output_dir: Path) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    stamp = int(time.time())
    profile_id = str(result["profile"]["profile_id"])
    pipeline = str(result["pipeline"])
    file_path = output_dir / f"{profile_id}_{pipeline}_{stamp}.json"
    file_path.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    return file_path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="CogMem T6.3 evaluation harness")
    parser.add_argument("--pipeline", choices=["recall", "full", "both"], default="both")
    parser.add_argument("--profile", choices=sorted(ABLATION_PROFILES.keys()), default="E1")
    parser.add_argument("--fixture", choices=["short"], default="short")
    parser.add_argument("--base-url", default=None, help="CogMem API base URL, example: http://localhost:8888")
    parser.add_argument("--bank-id", default=None)
    parser.add_argument("--skip-retain", action="store_true")
    parser.add_argument("--output-dir", default="logs/eval")
    parser.add_argument("--api-timeout", type=float, default=120.0)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    api_base_url = resolve_api_base_url(args.base_url)

    bank_id = args.bank_id
    if not bank_id:
        bank_id = f"cogmem_eval_{args.profile.lower()}_{uuid.uuid4().hex[:8]}"

    output_dir = Path(args.output_dir)
    pipelines = ["recall", "full"] if args.pipeline == "both" else [args.pipeline]

    written: list[Path] = []
    for pipeline in pipelines:
        result = run_pipeline(
            pipeline=pipeline,
            api_base_url=api_base_url,
            bank_id=bank_id,
            profile_id=args.profile,
            fixture_name=args.fixture,
            skip_retain=args.skip_retain,
            timeout_seconds=max(1.0, args.api_timeout),
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
