"""Task 735 — Artifact: Verify fixes for 3 failing retain tests.

Checks (offline, no real LLM needed):
1. DIALOGUE in test_dialogue_onboarding.py contains "Bob"
2. fact_extraction.py prompt contains "fulfilled" intention example
3. fact_extraction.py prompt contains rule for multiple action_effect facts
"""

from __future__ import annotations

import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))


def test_onboarding_dialogue_has_bob() -> None:
    path = _REPO_ROOT / "tests/retain/test_dialogue_onboarding.py"
    text = path.read_text(encoding="utf-8")
    assert "I'm Bob" in text or "I am Bob" in text, (
        "DIALOGUE in test_dialogue_onboarding.py must mention Bob by name"
    )
    print("OK  DIALOGUE contains Bob's name")


def test_prompt_intention_fulfilled_example() -> None:
    path = _REPO_ROOT / "cogmem_api/engine/retain/fact_extraction.py"
    text = path.read_text(encoding="utf-8")
    assert '"intention_status":"fulfilled"' in text or '"intention_status": "fulfilled"' in text, (
        "fact_extraction.py prompt must include a 'fulfilled' intention example"
    )
    assert "If already completed" in text or "already completed" in text, (
        "fact_extraction.py prompt must explain when to use 'fulfilled'"
    )
    print("OK  intention prompt has 'fulfilled' example and rule")


def test_prompt_action_effect_multiple_rule() -> None:
    path = _REPO_ROOT / "cogmem_api/engine/retain/fact_extraction.py"
    text = path.read_text(encoding="utf-8")
    assert "ONE separate action_effect fact" in text or "one action_effect" in text.lower(), (
        "fact_extraction.py prompt must instruct to create separate facts per causal relationship"
    )
    # Count action_effect examples (each has "devalue_sensitive")
    count = text.count('"devalue_sensitive"')
    assert count >= 2, f"Expected at least 2 action_effect examples in prompt, found {count}"
    print("OK  action_effect prompt has multiple-fact rule and 2+ examples")


def main() -> None:
    test_onboarding_dialogue_has_bob()
    test_prompt_intention_fulfilled_example()
    test_prompt_action_effect_multiple_rule()
    print("\nAll task-735 artifact checks passed.")


if __name__ == "__main__":
    main()
