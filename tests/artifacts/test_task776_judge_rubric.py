"""Task 776: Fix judge scoring — score rubric for count/quantity.

Verifies:
1. Default judge prompt has explicit score rubric (0.0-1.0 ranges)
2. Default judge prompt has "count/quantity" rule (score <= 0.3 for wrong number)
3. "be generous" language removed from default prompt
"""

import re
import sys


def test_judge_has_score_rubric():
    path = "cogmem_api/engine/eval_helpers.py"
    with open(path, "r", encoding="utf-8") as f:
        source = f.read()

    match = re.search(
        r'# Default:.*?\n\s*return \((.+?)\n\s*\)',
        source,
        re.DOTALL,
    )
    assert match, "Could not find default judge prompt in eval_helpers.py"
    default_text = match.group(1)

    assert "0.3-0.6" in default_text, (
        "Default judge prompt must include score range 0.3-0.6 "
        "(partially correct — right topic but wrong count)"
    )
    assert "1.0: correct and complete" in default_text, (
        "Default judge prompt must have explicit 1.0 score description"
    )


def test_judge_count_rule():
    path = "cogmem_api/engine/eval_helpers.py"
    with open(path, "r", encoding="utf-8") as f:
        source = f.read()

    match = re.search(
        r'# Default:.*?\n\s*return \((.+?)\n\s*\)',
        source,
        re.DOTALL,
    )
    default_text = match.group(1)

    assert "count" in default_text.lower(), (
        "Default judge prompt must have explicit rule for count/quantity questions"
    )
    assert "<=" in default_text and "0.3" in default_text, (
        "Default judge prompt must have 'score <= 0.3' for wrong counts"
    )


def test_generous_removed():
    path = "cogmem_api/engine/eval_helpers.py"
    with open(path, "r", encoding="utf-8") as f:
        source = f.read()

    assert "generous" not in source.lower(), (
        '"generous" language must be removed from eval_helpers.py — '
        "it contradicts correct=false for subset"
    )


if __name__ == "__main__":
    test_judge_has_score_rubric()
    test_judge_count_rule()
    test_generous_removed()
    print("3/3 PASS")
    sys.exit(0)
