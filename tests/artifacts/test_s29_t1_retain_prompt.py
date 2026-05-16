"""Sprint S29 T-1 artifact test — retain prompt extraction guidelines.

Run:  uv run python tests/artifacts/test_s29_t1_retain_prompt.py
"""
from __future__ import annotations

import sys


def test_pass1_has_extraction_checklist():
    from cogmem_api.prompts.retain.pass1 import build_pass1_prompt

    class FakeConfig:
        retain_extraction_mode = "concise"
        retain_mission = None
        retain_custom_instructions = None

    prompt, mode = build_pass1_prompt(FakeConfig())
    pl = prompt.lower()
    assert "extraction checklist" in pl, "Pass 1: extraction checklist heading missing"
    assert "named pets, people, products, apps, places" in pl, "Pass 1: named entity guideline missing"
    assert "purchases/acquisitions" in pl, "Pass 1: purchase guideline missing"
    assert "numeric values in user utterances" in pl, "Pass 1: numeric values guideline missing"
    assert "recent user actions" in pl, "Pass 1: user actions guideline missing"
    assert "assistant recommendations of specific named tools" in pl, "Pass 1: assistant recommendations guideline missing"
    assert "luna" in pl, "Pass 1: Luna example missing"
    assert "memrise" in pl, "Pass 1: Memrise example missing"
    assert "power bank" in pl, "Pass 1: power bank example missing"
    assert "took me 10 hours" in pl, "Pass 1: 10 hours example missing"
    print("T-1 PASS: pass1.py extraction checklist present with all 5 guidelines + examples")


def test_pass2_has_extraction_checklist():
    from cogmem_api.prompts.retain.pass2 import build_pass2_prompt

    prompt = build_pass2_prompt()
    assert "PERSONAL EXTRACTION CHECKLIST" in prompt, "Pass 2: checklist heading missing"
    assert "Named pets, people, products, apps, places" in prompt, "Pass 2: named entity guideline missing"
    assert "purchases/acquisitions" in prompt, "Pass 2: purchase guideline missing"
    assert "numeric values" in prompt, "Pass 2: numeric values guideline missing"
    assert "Recent user actions" in prompt, "Pass 2: user actions guideline missing"
    assert "specific apps/products" in prompt, "Pass 2: apps/products guideline missing"
    print("T-1 PASS: pass2.py extraction checklist present with all 5 guidelines")


if __name__ == "__main__":
    tests = [
        ("T-1-pass1", test_pass1_has_extraction_checklist),
        ("T-1-pass2", test_pass2_has_extraction_checklist),
    ]

    failures = 0
    for name, fn in tests:
        try:
            fn()
        except Exception as e:
            print(f"FAIL {name}: {e}")
            failures += 1

    print()
    if failures:
        print(f"RESULT: {len(tests) - failures}/{len(tests)} PASS, {failures} FAIL")
        sys.exit(1)
    else:
        print(f"RESULT: {len(tests)}/{len(tests)} PASS — T-1 retain prompt gates PASS")
        sys.exit(0)
