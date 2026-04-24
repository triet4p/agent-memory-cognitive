"""Task 752: S22.4 — Reranker active detection.

Verifies:
- reranker_used = False when all cross_encoder_scores are 0 or missing
- reranker_used = True when any cross_encoder_score > 0
- reranker_used flag is included in both recall_only and full_e2e pipeline returns
"""

from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))


def _detect_reranker_used(results):
    return any(float(r.get("cross_encoder_score", 0)) > 0 for r in results)


def test_no_reranker_when_scores_zero():
    results = [
        {"id": "1", "text": "result one", "cross_encoder_score": 0.0},
        {"id": "2", "text": "result two", "cross_encoder_score": 0.0},
    ]
    assert _detect_reranker_used(results) is False


def test_no_reranker_when_scores_missing():
    results = [
        {"id": "1", "text": "result one"},
        {"id": "2", "text": "result two"},
    ]
    assert _detect_reranker_used(results) is False


def test_reranker_active_when_any_score_positive():
    results = [
        {"id": "1", "text": "result one", "cross_encoder_score": 0.0},
        {"id": "2", "text": "result two", "cross_encoder_score": 0.75},
        {"id": "3", "text": "result three", "cross_encoder_score": 0.0},
    ]
    assert _detect_reranker_used(results) is True


def test_reranker_active_first_result():
    results = [
        {"id": "1", "text": "result one", "cross_encoder_score": 0.5},
        {"id": "2", "text": "result two", "cross_encoder_score": 0.0},
    ]
    assert _detect_reranker_used(results) is True


def test_reranker_active_with_float_conversion():
    results = [
        {"id": "1", "text": "result one", "cross_encoder_score": "0.8"},
        {"id": "2", "text": "result two", "cross_encoder_score": 0.0},
    ]
    assert _detect_reranker_used(results) is True


def test_reranker_used_in_recall_only_return():
    from scripts.eval_cogmem import SHORT_DIALOGUE_FIXTURE, ABLATION_PROFILES

    profile = ABLATION_PROFILES["E1"]
    fixture = SHORT_DIALOGUE_FIXTURE

    def fake_post(url, payload, timeout):
        return {"results": [
            {"id": "1", "text": "result one", "cross_encoder_score": 0.0},
            {"id": "2", "text": "result two", "cross_encoder_score": 0.0},
        ]}

    from scripts.eval_cogmem import run_recall_only_pipeline
    result = run_recall_only_pipeline(
        api_base_url="http://localhost:8888",
        bank_id="test-bank",
        profile=profile,
        fixture=fixture,
        skip_retain=True,
        timeout_seconds=30.0,
        post_json_fn=fake_post,
    )
    assert "reranker_used" in result
    assert result["reranker_used"] is False


def test_reranker_used_in_full_e2e_return():
    from scripts.eval_cogmem import SHORT_DIALOGUE_FIXTURE, ABLATION_PROFILES, EvalLLMConfig

    profile = ABLATION_PROFILES["E1"]
    fixture = SHORT_DIALOGUE_FIXTURE
    llm_config = EvalLLMConfig(
        provider="openai",
        model="test",
        api_key="test",
        base_url="http://test/v1",
        timeout_seconds=30.0,
        max_completion_tokens=128,
    )

    def fake_post(url, payload, timeout):
        return {"results": [
            {"id": "1", "text": "result one", "cross_encoder_score": 0.6},
            {"id": "2", "text": "result two", "cross_encoder_score": 0.0},
        ]}

    def fake_llm_call(config, messages, tokens):
        return '{"answer": "test"}'

    from scripts.eval_cogmem import run_full_pipeline
    result = run_full_pipeline(
        api_base_url="http://localhost:8888",
        bank_id="test-bank",
        profile=profile,
        fixture=fixture,
        llm_config=llm_config,
        skip_retain=True,
        timeout_seconds=30.0,
        post_json_fn=fake_post,
        llm_call_fn=fake_llm_call,
    )
    assert "reranker_used" in result
    assert result["reranker_used"] is True


if __name__ == "__main__":
    print("Task 752 reranker active detection tests")
    test_no_reranker_when_scores_zero()
    print("  test_no_reranker_when_scores_zero PASSED")
    test_no_reranker_when_scores_missing()
    print("  test_no_reranker_when_scores_missing PASSED")
    test_reranker_active_when_any_score_positive()
    print("  test_reranker_active_when_any_score_positive PASSED")
    test_reranker_active_first_result()
    print("  test_reranker_active_first_result PASSED")
    test_reranker_active_with_float_conversion()
    print("  test_reranker_active_with_float_conversion PASSED")
    test_reranker_used_in_recall_only_return()
    print("  test_reranker_used_in_recall_only_return PASSED")
    test_reranker_used_in_full_e2e_return()
    print("  test_reranker_used_in_full_e2e_return PASSED")
    print("Task 752 reranker active detection passed.")