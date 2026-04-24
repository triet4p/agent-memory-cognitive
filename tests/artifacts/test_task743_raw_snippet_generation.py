"""Task 743: S20.1 raw_snippet injection into generation context.

Verifies:
- _build_generation_prompt() uses raw_snippet when available, falls back to text
- Facts with specific numbers (e.g. "40%", "45ms") appear in evidence when raw_snippet is present
"""

from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.eval_cogmem import _build_generation_prompt, _normalize_text


def test_raw_snippet_used_when_present():
    recall_results = [
        {
            "id": "1",
            "text": "User chuyển từ VCCorp sang DI tháng 4/2024",
            "raw_snippet": "Hôm nay mình vừa nghỉ việc ở VCCorp rồi. Buồn lắm vì team cũ rất thân. Mình nhận offer từ DI với mức lương cao hơn 40%. Sẽ bắt đầu từ 1/4.",
            "fact_type": "experience",
        },
        {
            "id": "2",
            "text": "Khi latency vượt 100ms user chuyển sang int8",
            "raw_snippet": None,
            "fact_type": "action_effect",
        },
    ]
    prompt = _build_generation_prompt("Mức lương khi chuyển sang DI cao hơn bao nhiêu?", recall_results)

    assert "40%" in prompt, "raw_snippet with specific number must appear in prompt"
    assert "[1]" in prompt
    assert "[2]" in prompt


def test_raw_snippet_fallback_to_text():
    recall_results = [
        {
            "id": "3",
            "text": "User có kế hoạch học Rust trước Q3",
            "raw_snippet": None,
            "fact_type": "intention",
        },
    ]
    prompt = _build_generation_prompt("User đang plan học gì?", recall_results)

    assert "User có kế hoạch học Rust trước Q3" in prompt
    assert "[1]" in prompt


def test_mixed_raw_snippet_and_text():
    recall_results = [
        {
            "id": "1",
            "text": "User chuyển từ VCCorp sang DI",
            "raw_snippet": "offer từ DI với mức lương cao hơn 40%",
            "fact_type": "experience",
        },
        {
            "id": "2",
            "text": "User chuyển sang int8 khi latency cao",
            "raw_snippet": None,
            "fact_type": "action_effect",
        },
    ]
    prompt = _build_generation_prompt("Mức lương cao hơn bao nhiêu?", recall_results)

    assert "40%" in prompt, "Specific detail from raw_snippet must be in prompt"
    assert "User chuyển sang int8 khi latency cao" in prompt, "Fallback text must appear when no raw_snippet"


def test_raw_snippet_verification_keywords():
    recall_results = [
        {
            "id": "1",
            "text": "User có kế hoạch học Rust trước Q3, deadline cuối tháng 9",
            "raw_snippet": "Deadline là cuối tháng 9. Khi latency vượt 100ms thì mình thường chuyển sang int8 và latency giảm còn khoảng 45ms.",
            "fact_type": "intention",
        },
    ]
    prompt = _build_generation_prompt("Khi latency cao thì user làm gì và kết quả ra sao?", recall_results)

    assert "45ms" in prompt, "Specific numeric detail from raw_snippet must appear in prompt"
    assert "100ms" in prompt, "Precondition detail from raw_snippet must appear in prompt"
    assert "int8" in _normalize_text(prompt), "Action detail from raw_snippet must appear in prompt"


def main() -> None:
    test_raw_snippet_used_when_present()
    test_raw_snippet_fallback_to_text()
    test_mixed_raw_snippet_and_text()
    test_raw_snippet_verification_keywords()
    print("Task 743 raw_snippet injection gate passed.")


if __name__ == "__main__":
    main()
