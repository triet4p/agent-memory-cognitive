"""Task 751: S22.3 — Recall@k and Precision@k.

Verifies:
- _build_recall_at_k() returns None when gold_keywords is None/empty
- recall_at_k and precision_at_k computed correctly
- works with k larger than result count (handles short lists)
- recalled_keywords and total_gold_keywords returned
"""

from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.eval_cogmem import _build_recall_at_k


def test_none_gold_keywords_returns_none():
    result = _build_recall_at_k([{"text": "coffee is great"}], None, k=5)
    assert result["recall_at_k"] is None
    assert result["precision_at_k"] is None


def test_empty_gold_keywords_returns_none():
    result = _build_recall_at_k([{"text": "coffee is great"}], [], k=5)
    assert result["recall_at_k"] is None


def test_full_recall_at_5():
    results = [
        {"text": "Alice drinks coffee every morning"},
        {"text": "Bob prefers tea"},
        {"text": "Charlie likes coffee"},
        {"text": "Diana exercises on Monday"},
        {"text": "Eve works from home"},
    ]
    gold = ["coffee", "morning", "Monday"]
    result = _build_recall_at_k(results, gold, k=5)
    assert result["recall_at_k"] == 1.0
    assert result["precision_at_k"] == 3.0 / (5 * 3.0)
    assert result["recalled_keywords"] == 3
    assert result["total_gold_keywords"] == 3


def test_partial_recall_at_3():
    results = [
        {"text": "Alice drinks coffee every morning"},
        {"text": "Bob prefers tea"},
        {"text": "Charlie likes chocolate"},
    ]
    gold = ["coffee", "morning", "Monday"]
    result = _build_recall_at_k(results, gold, k=3)
    assert result["recall_at_k"] == 2.0 / 3.0
    assert result["precision_at_k"] == 2.0 / (3 * 3.0)
    assert result["recalled_keywords"] == 2
    assert result["total_gold_keywords"] == 3


def test_k_larger_than_results():
    results = [
        {"text": "Alice drinks coffee"},
    ]
    gold = ["coffee", "tea"]
    result = _build_recall_at_k(results, gold, k=10)
    assert result["recall_at_k"] == 1.0 / 2.0
    assert result["precision_at_k"] == 1.0 / (10 * 2.0)


def test_case_insensitive_matching():
    results = [
        {"text": "COFFEE is great"},
        {"text": "Tea is fine"},
    ]
    gold = ["coffee", "tea"]
    result = _build_recall_at_k(results, gold, k=2)
    assert result["recall_at_k"] == 1.0
    assert result["precision_at_k"] == 2.0 / (2 * 2.0)


def test_normalization_removes_punctuation():
    results = [
        {"text": "coffee,"},
        {"text": "morning!"},
    ]
    gold = ["coffee", "morning"]
    result = _build_recall_at_k(results, gold, k=2)
    assert result["recall_at_k"] == 1.0


if __name__ == "__main__":
    print("Task 751 recall@k tests")
    test_none_gold_keywords_returns_none()
    print("  test_none_gold_keywords_returns_none PASSED")
    test_empty_gold_keywords_returns_none()
    print("  test_empty_gold_keywords_returns_none PASSED")
    test_full_recall_at_5()
    print("  test_full_recall_at_5 PASSED")
    test_partial_recall_at_3()
    print("  test_partial_recall_at_3 PASSED")
    test_k_larger_than_results()
    print("  test_k_larger_than_results PASSED")
    test_case_insensitive_matching()
    print("  test_case_insensitive_matching PASSED")
    test_normalization_removes_punctuation()
    print("  test_normalization_removes_punctuation PASSED")
    print("Task 751 recall@k passed.")