"""S35-T8E artifact: verify 3-bank LoCoMo checkpoint completeness.

This test intentionally does not evaluate correctness or use judge fields. It
only checks that the 0..93 T8E probe produced complete, readable checkpoint
files with generated answers.

Run: uv run python tests/artifacts/test_task_s35_t8e_3bank_checkpoints.py
"""

from __future__ import annotations

import json
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
CHECKPOINT_DIR = REPO_ROOT / "experiments" / "v20_t8e_3bank" / "checkpoints"


def test_all_3bank_checkpoints_exist() -> None:
    missing = [
        idx for idx in range(94)
        if not (CHECKPOINT_DIR / f"E7_full_c{idx:03d}.json").exists()
    ]
    assert missing == [], f"missing checkpoints: {missing}"
    print("[ok] all 94 checkpoints exist")


def test_checkpoints_have_generated_answers() -> None:
    empty = []
    for idx in range(94):
        path = CHECKPOINT_DIR / f"E7_full_c{idx:03d}.json"
        data = json.loads(path.read_text(encoding="utf-8"))
        questions = data.get("questions") or []
        if len(questions) != 1:
            empty.append((idx, "question_count"))
            continue
        answer = str(questions[0].get("generated_answer") or "").strip()
        if not answer:
            empty.append((idx, "generated_answer"))
    assert empty == [], f"empty/malformed checkpoints: {empty}"
    print("[ok] all checkpoints have generated answers")


def main() -> int:
    test_all_3bank_checkpoints_exist()
    test_checkpoints_have_generated_answers()
    print("\nS35-T8E 3-bank checkpoints PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
