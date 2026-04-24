"""Task 746: S21.1 — LongMemEval-S distilled adapter.

Verifies:
- _make_benchmark_fixture() reads longmemeval_s_distilled_small.json
- Returns valid fixture with {"name", "turns", "questions"}
- Each question has {"id", "query", "gold_answer", "category", "turns"}
- Maps question_type to category labels
"""

from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.eval_cogmem import get_fixture


def test_longmemeval_fixture():
    fixture = get_fixture("longmemeval")
    assert fixture["name"] == "longmemeval_benchmark"
    assert len(fixture["turns"]) > 0, "should have concatenated turns"
    assert len(fixture["questions"]) == 12, f"expected 12 questions, got {len(fixture['questions'])}"

    required_keys = {"id", "query", "gold_answer", "category", "turns"}
    for q in fixture["questions"]:
        assert required_keys.issubset(q.keys()), f"Missing keys in question: {q}"
        assert isinstance(q["turns"], list), f"turns should be list, got {type(q['turns'])}"
        assert len(q["turns"]) > 0, f"each question should have turns, {q['id']} has empty turns"


def test_longmemeval_category_mapping():
    fixture = get_fixture("longmemeval")
    categories = {q["category"] for q in fixture["questions"]}
    assert len(categories) >= 3, f"expected multiple categories, got: {categories}"
    print(f"  Categories: {categories}")


def main() -> None:
    test_longmemeval_fixture()
    test_longmemeval_category_mapping()
    print("Task 746 LME adapter gate passed.")


if __name__ == "__main__":
    main()
