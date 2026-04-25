"""Task 756: Bug fixes 7.1 (FK upsert), 7.2 (bool coercion), 7.3 (null keyword metrics)."""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from scripts.eval_cogmem import (
    _keyword_recall_metrics,
    _judge_answer,
    _per_category_stats,
    EvalLLMConfig,
)


# --- 7.3: null keyword metrics ---

def test_keyword_metrics_no_keywords_returns_none():
    m = _keyword_recall_metrics(None, "some text")
    assert m["keyword_coverage"] is None
    assert m["strict_hit"] is None
    assert m["keyword_total"] == 0
    assert m["matched_keywords"] == []


def test_keyword_metrics_empty_list_returns_none():
    m = _keyword_recall_metrics([], "some text")
    assert m["keyword_coverage"] is None
    assert m["strict_hit"] is None


def test_keyword_metrics_with_keywords_computes_float():
    m = _keyword_recall_metrics(["cat", "dog"], "I have a cat")
    assert m["keyword_coverage"] == 0.5
    assert m["strict_hit"] is False


def test_keyword_metrics_full_match():
    m = _keyword_recall_metrics(["hello", "world"], "hello world")
    assert m["keyword_coverage"] == 1.0
    assert m["strict_hit"] is True


def test_per_category_stats_null_coverage_skipped():
    questions = [{"category": "multi-session"}, {"category": "multi-session"}]
    per_question = [
        {"recall_metrics": {"keyword_coverage": None, "strict_hit": None}, "judge": {"correct": True, "score": 1.0}},
        {"recall_metrics": {"keyword_coverage": None, "strict_hit": None}, "judge": {"correct": False, "score": 0.0}},
    ]
    result = _per_category_stats(questions, per_question, is_full_pipeline=True)
    cat = result["multi-session"]
    assert cat["recall_keyword_accuracy"] is None
    assert cat["recall_strict_accuracy"] is None
    assert cat["judge_accuracy"] == 0.5


def test_per_category_stats_mixed_null_and_value():
    questions = [{"category": "temporal"}, {"category": "temporal"}]
    per_question = [
        {"recall_metrics": {"keyword_coverage": 0.8, "strict_hit": True}, "judge": {"correct": True, "score": 0.9}},
        {"recall_metrics": {"keyword_coverage": None, "strict_hit": None}, "judge": {"correct": True, "score": 1.0}},
    ]
    result = _per_category_stats(questions, per_question, is_full_pipeline=True)
    cat = result["temporal"]
    assert cat["recall_keyword_accuracy"] == 0.8
    assert cat["recall_strict_accuracy"] == 1.0


# --- 7.2: bool coercion ---

def test_judge_answer_string_false_coerced():
    cfg = EvalLLMConfig(provider="openai", base_url="unused", api_key="unused", model="unused", timeout_seconds=10, max_completion_tokens=100)

    def fake_llm(config, messages, max_tokens):
        return '{"correct": "false", "score": 0.1, "reason": "nope"}'

    result = _judge_answer(cfg, question="q", gold_answer="a", predicted_answer="b", llm_call_fn=fake_llm)
    assert result["correct"] is False


def test_judge_answer_string_true_coerced():
    cfg = EvalLLMConfig(provider="openai", base_url="unused", api_key="unused", model="unused", timeout_seconds=10, max_completion_tokens=100)

    def fake_llm(config, messages, max_tokens):
        return '{"correct": "true", "score": 0.9, "reason": "yes"}'

    result = _judge_answer(cfg, question="q", gold_answer="a", predicted_answer="b", llm_call_fn=fake_llm)
    assert result["correct"] is True


def test_judge_answer_bool_true_unchanged():
    cfg = EvalLLMConfig(provider="openai", base_url="unused", api_key="unused", model="unused", timeout_seconds=10, max_completion_tokens=100)

    def fake_llm(config, messages, max_tokens):
        return '{"correct": true, "score": 1.0, "reason": "perfect"}'

    result = _judge_answer(cfg, question="q", gold_answer="a", predicted_answer="b", llm_call_fn=fake_llm)
    assert result["correct"] is True


if __name__ == "__main__":
    tests = [v for k, v in list(globals().items()) if k.startswith("test_")]
    passed = failed = 0
    for fn in tests:
        try:
            fn()
            print(f"  PASS  {fn.__name__}")
            passed += 1
        except Exception as exc:
            print(f"  FAIL  {fn.__name__}: {exc}")
            failed += 1
    print(f"\n{passed} passed, {failed} failed")
    sys.exit(1 if failed else 0)
