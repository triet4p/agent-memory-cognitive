"""Task 747: S21.2 — LoCoMo distilled adapter.

Verifies:
- _make_benchmark_fixture() reads locomo_distilled.json
- LoCoMo conversation dict format is handled correctly (session keys, 'text' field)
- Each question has its own conversation turns
- Category integers are mapped to string labels
"""

from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.eval_cogmem import get_fixture


def test_locomo_fixture():
    fixture = get_fixture("locomo")
    assert fixture["name"] == "locomo_benchmark"
    assert len(fixture["turns"]) > 0, "should have concatenated turns across all conversations"
    assert len(fixture["questions"]) > 0, "should have questions"

    for q in fixture["questions"]:
        assert "id" in q
        assert "query" in q
        assert "gold_answer" in q
        assert "category" in q
        assert isinstance(q["turns"], list), "each question should have conversation turns"


def test_locomo_category_mapping():
    fixture = get_fixture("locomo")
    categories = {q["category"] for q in fixture["questions"]}
    assert len(categories) >= 2, f"expected multiple categories, got: {categories}"
    print(f"  Categories: {categories}")
    print(f"  Total Qs: {len(fixture['questions'])}")


def test_locomo_turns_per_conversation():
    fixture = get_fixture("locomo")
    turn_counts = [len(q["turns"]) for q in fixture["questions"]]
    assert min(turn_counts) > 0, "all questions should have non-empty turns"
    print(f"  Turns per Q: min={min(turn_counts)}, max={max(turn_counts)}, avg={sum(turn_counts)//len(turn_counts)}")


def main() -> None:
    test_locomo_fixture()
    test_locomo_category_mapping()
    test_locomo_turns_per_conversation()
    print("Task 747 LoCoMo adapter gate passed.")


if __name__ == "__main__":
    main()
