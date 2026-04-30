"""Judge prompt builder — extracted from eval_helpers.py for centralization.

Used by cogmem_api HTTP endpoint (/judge).
"""

from __future__ import annotations


def build_judge_system_prompt(category: str | None) -> str:
    """Build system prompt for judge endpoint (LLM-as-judge).

    Args:
        category: Question category (temporal, knowledge-update, preference, etc.)

    Returns:
        System prompt string for judge LLM
    """
    cat = (category or "").lower()

    if cat in ("temporal", "temporal-reasoning"):
        return (
            "You are an evaluation judge for a memory system.\n"
            "I will give you a question, a correct answer, and a model response.\n"
            "Score rubric (0.0-1.0):\n"
            "- 1.0: correct and complete\n"
            "- 0.7-0.9: correct but slightly rephrased or minor detail missing\n"
            "- 0.3-0.6: partially correct — right topic but missing key facts, wrong count, or hedged answer\n"
            "- 0.0-0.2: wrong, fabricated, or completely missing the answer\n"
            "Do NOT penalize off-by-one errors for counts of days/weeks/months "
            "(e.g. 18 days vs 19 days is still correct).\n"
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

    return (
        "You are an evaluation judge for a memory recall system.\n"
        "Your task: label the model's answer as correct or incorrect.\n"
        "You will be given a question, a gold (ground truth) answer, and a generated answer.\n"
        "Score rubric (0.0-1.0):\n"
        "- 1.0: correct and complete\n"
        "- 0.7-0.9: correct but slightly rephrased or minor detail missing\n"
        "- 0.3-0.6: partially correct — right topic but missing key facts, wrong count, or hedged answer\n"
        "- 0.0-0.2: wrong, fabricated, or completely missing the answer\n"
        "For count/quantity questions: if the number is wrong, score <= 0.3 even if the topic is right.\n"
        'Return strict JSON: {"correct": bool, "score": float 0..1, "reason": string}'
    )


def parse_judge_response(raw: str) -> dict:
    """Parse judge LLM JSON output with graceful fallback.

    Args:
        raw: Raw string output from judge LLM

    Returns:
        Parsed dict with correct/score/reason/raw fields
    """
    import json
    import re

    import logging as _logging
    _logging.getLogger(__name__).warning("parse_judge_response raw=%r", raw[:500] if raw else raw)

    text = raw.strip()

    # Strip <think>...</think> blocks emitted by reasoning models
    text = re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL).strip()

    if text.startswith("```"):
        text = text.split("\n", 1)[1] if "\n" in text else text[3:]
        if text.endswith("```"):
            text = text[:-3]
        text = text.strip()

    try:
        parsed = json.loads(text)
    except json.JSONDecodeError:
        cleaned = re.sub(r"[\x00-\x1f\x7f]", " ", text)
        try:
            parsed = json.loads(cleaned)
        except json.JSONDecodeError:
            from json_repair import repair_json
            parsed = json.loads(repair_json(cleaned))

    if isinstance(parsed, list):
        parsed = parsed[0] if parsed else {}

    score = parsed.get("score", 0.0)
    try:
        numeric_score = float(score)
    except (TypeError, ValueError):
        numeric_score = 0.0

    correct_val = parsed.get("correct", False)
    if isinstance(correct_val, str):
        correct_val = correct_val.lower() in ("true", "1", "yes")

    return {
        "correct": bool(correct_val),
        "score": numeric_score,
        "reason": str(parsed.get("reason", "")),
        "raw": raw,
    }