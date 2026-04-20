"""Task 737 — Artifact: Verify fixes for v2 failing retain tests.

Checks (offline, no real LLM needed):
1. llm_wrapper.py has total_tokens fallback (inp + out)
2. fact_extraction.py prompt has completion-signal markers for fulfilled intention
3. fact_extraction.py has _infer_fulfilled_from_context helper
4. fact_extraction.py has action_effect last-resort triplet fallback ("N/A")
"""

from __future__ import annotations

import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))


def test_llm_wrapper_total_tokens_fallback() -> None:
    path = _REPO_ROOT / "cogmem_api/engine/llm_wrapper.py"
    text = path.read_text(encoding="utf-8")
    assert "_inp + _out" in text or "inp + out" in text, (
        "llm_wrapper.py must compute total_tokens as inp+out when provider omits it"
    )
    print("OK  llm_wrapper: total_tokens fallback present")


def test_prompt_intention_completion_signals() -> None:
    path = _REPO_ROOT / "cogmem_api/engine/retain/fact_extraction.py"
    text = path.read_text(encoding="utf-8")
    assert "finished" in text and "fulfilled" in text, (
        "Prompt must mention 'finished' as a completion signal for fulfilled intention"
    )
    assert "planning" in text and "fulfilled" in text and "abandoned" in text, (
        "Prompt must enumerate all 3 intention statuses with guidance"
    )
    print("OK  intention prompt: completion signals present")


def test_code_infer_fulfilled_from_context() -> None:
    path = _REPO_ROOT / "cogmem_api/engine/retain/fact_extraction.py"
    text = path.read_text(encoding="utf-8")
    assert "_infer_fulfilled_from_context" in text, (
        "fact_extraction.py must define _infer_fulfilled_from_context()"
    )
    assert "_FULFILLED_SIGNALS" in text, (
        "fact_extraction.py must define _FULFILLED_SIGNALS frozenset"
    )
    assert "_PAST_INTENTION_MARKERS" in text, (
        "fact_extraction.py must define _PAST_INTENTION_MARKERS frozenset"
    )
    print("OK  code: _infer_fulfilled_from_context and frozensets present")


def test_action_effect_triplet_fallback() -> None:
    path = _REPO_ROOT / "cogmem_api/engine/retain/fact_extraction.py"
    text = path.read_text(encoding="utf-8")
    assert 'precondition = "N/A"' in text or "precondition or" in text, (
        "fact_extraction.py must have last-resort fallback for missing precondition"
    )
    assert 'outcome = "N/A"' in text or "outcome or" in text, (
        "fact_extraction.py must have last-resort fallback for missing outcome"
    )
    print("OK  action_effect: last-resort triplet fallback present")


def main() -> None:
    test_llm_wrapper_total_tokens_fallback()
    test_prompt_intention_completion_signals()
    test_code_infer_fulfilled_from_context()
    test_action_effect_triplet_fallback()
    print("\nAll task-737 artifact checks passed.")


if __name__ == "__main__":
    main()
