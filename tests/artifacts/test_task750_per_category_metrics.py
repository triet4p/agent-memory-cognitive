"""Task 750: S22.2 — Per-category accuracy breakdown.

Verifies:
- _per_category_stats() aggregates correctly across categories
- recall_keyword_accuracy and recall_strict_accuracy computed per category
- judge_accuracy and judge_score_mean added when is_full_pipeline=True
- missing category defaults to "unknown"
"""

from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.eval_cogmem import _per_category_stats


def test_recall_only_two_categories():
    questions = [
        {"id": "q1", "category": "preference", "expected_keywords": ["coffee", "tea"]},
        {"id": "q2", "category": "preference", "expected_keywords": ["coffee"]},
        {"id": "q3", "category": "temporal", "expected_keywords": ["monday", "tuesday"]},
        {"id": "q4", "category": "temporal", "expected_keywords": ["monday"]},
    ]
    per_question = [
        {"recall_metrics": {"keyword_coverage": 1.0, "strict_hit": True}},
        {"recall_metrics": {"keyword_coverage": 0.5, "strict_hit": False}},
        {"recall_metrics": {"keyword_coverage": 0.0, "strict_hit": False}},
        {"recall_metrics": {"keyword_coverage": 1.0, "strict_hit": True}},
    ]
    stats = _per_category_stats(questions, per_question, is_full_pipeline=False)

    assert "preference" in stats
    assert "temporal" in stats
    assert stats["preference"]["count"] == 2
    assert stats["preference"]["recall_keyword_accuracy"] == (1.0 + 0.5) / 2
    assert stats["preference"]["recall_strict_accuracy"] == 1.0 / 2.0
    assert "judge_accuracy" not in stats["preference"]

    assert stats["temporal"]["count"] == 2
    assert stats["temporal"]["recall_keyword_accuracy"] == (0.0 + 1.0) / 2
    assert stats["temporal"]["recall_strict_accuracy"] == 1.0 / 2.0


def test_full_pipeline_adds_judge_fields():
    questions = [
        {"id": "q1", "category": "preference"},
        {"id": "q2", "category": "preference"},
    ]
    per_question = [
        {"recall_metrics": {"keyword_coverage": 1.0, "strict_hit": True}, "judge": {"correct": True, "score": 0.9}},
        {"recall_metrics": {"keyword_coverage": 0.5, "strict_hit": False}, "judge": {"correct": False, "score": 0.3}},
    ]
    stats = _per_category_stats(questions, per_question, is_full_pipeline=True)

    assert stats["preference"]["judge_accuracy"] == 1.0 / 2.0
    assert stats["preference"]["judge_score_mean"] == (0.9 + 0.3) / 2.0


def test_missing_category_defaults_to_unknown():
    questions = [
        {"id": "q1"},  # no category
        {"id": "q2", "category": "known"},
    ]
    per_question = [
        {"recall_metrics": {"keyword_coverage": 1.0, "strict_hit": True}},
        {"recall_metrics": {"keyword_coverage": 0.5, "strict_hit": False}},
    ]
    stats = _per_category_stats(questions, per_question, is_full_pipeline=False)

    assert "unknown" in stats
    assert stats["unknown"]["count"] == 1
    assert stats["known"]["count"] == 1


if __name__ == "__main__":
    print("Task 750 per-category metrics tests")
    test_recall_only_two_categories()
    print("  test_recall_only_two_categories PASSED")
    test_full_pipeline_adds_judge_fields()
    print("  test_full_pipeline_adds_judge_fields PASSED")
    test_missing_category_defaults_to_unknown()
    print("  test_missing_category_defaults_to_unknown PASSED")
    print("Task 750 per-category metrics passed.")