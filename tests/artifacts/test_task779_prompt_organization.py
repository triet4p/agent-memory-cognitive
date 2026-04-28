"""Artifact test for Task 779 — Prompt centralization.

Verifies:
1. All prompts reachable via cogmem_api.prompts.*
2. eval_helpers.py no longer contains prompt template strings
3. pass1.build_pass1_prompt exists and works
4. pass2.build_pass2_prompt exists and works
5. PASS2_ALLOWED_FACT_TYPES is exported
6. generate.build_generation_prompt exists
7. judge.build_judge_system_prompt exists
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))


def test_prompts_reachable_via_toplevel():
    try:
        from cogmem_api.prompts import build_pass1_prompt, build_pass2_prompt, PASS2_ALLOWED_FACT_TYPES
        from cogmem_api.prompts import build_generation_prompt, build_judge_system_prompt
        actual_type = type(PASS2_ALLOWED_FACT_TYPES)
        print(f"  PASS2_ALLOWED_FACT_TYPES type: {actual_type}, value: {PASS2_ALLOWED_FACT_TYPES}")
        assert callable(build_pass1_prompt)
        assert callable(build_pass2_prompt)
        assert callable(build_generation_prompt)
        assert callable(build_judge_system_prompt)
        assert isinstance(PASS2_ALLOWED_FACT_TYPES, (frozenset, set)), f"Expected frozenset/set, got {actual_type}"
        print("PASS: All prompts reachable via cogmem_api.prompts.*")
    except Exception as exc:
        print(f"  ERROR: {type(exc).__name__}: {exc}")
        raise


def test_pass1_module_exists():
    from cogmem_api.prompts.retain import pass1
    assert hasattr(pass1, "build_pass1_prompt")
    assert hasattr(pass1, "_BASE_PROMPT")
    assert hasattr(pass1, "_CONCISE_MODE")
    print("PASS: pass1 module exists with correct exports")


def test_pass2_module_exists():
    from cogmem_api.prompts.retain import pass2
    assert hasattr(pass2, "build_pass2_prompt")
    assert hasattr(pass2, "_PASS2_PROMPT")
    assert hasattr(pass2, "PASS2_ALLOWED_FACT_TYPES")
    assert pass2.PASS2_ALLOWED_FACT_TYPES == frozenset({"experience", "habit", "intention", "opinion"})
    print("PASS: pass2 module exists with correct exports")


def test_shared_module_exists():
    from cogmem_api.prompts.retain import shared
    assert hasattr(shared, "sanitize_temporal_fact")
    print("PASS: shared module exists")


def test_eval_modules_exist():
    from cogmem_api.prompts.eval import generate, judge
    assert hasattr(generate, "build_generation_prompt")
    assert hasattr(judge, "build_judge_system_prompt")
    assert hasattr(judge, "parse_judge_response")
    print("PASS: eval modules exist")


def test_build_pass1_prompt_returns_tuple():
    from cogmem_api.prompts.retain import pass1
    class MockConfig:
        retain_extraction_mode = "concise"
        retain_mission = None
        retain_custom_instructions = None

    prompt, mode = pass1.build_pass1_prompt(MockConfig())
    assert isinstance(prompt, str)
    assert len(prompt) > 100
    assert mode == "concise"
    print("PASS: build_pass1_prompt returns (prompt_str, mode)")


def test_build_pass2_prompt_returns_string():
    from cogmem_api.prompts.retain import pass2
    prompt = pass2.build_pass2_prompt()
    assert isinstance(prompt, str)
    assert len(prompt) > 100
    assert "Pass 2" in prompt
    print("PASS: build_pass2_prompt returns string")


def test_eval_helpers_no_prompt_strings():
    from cogmem_api.engine import eval_helpers
    import inspect
    source = inspect.getsource(eval_helpers)
    assert "You are an evaluation judge" not in source
    assert "Answer the question using ONLY" not in source
    assert "Score rubric" not in source
    print("PASS: eval_helpers.py no longer contains prompt template strings")


def test_eval_helpers_still_has_functions():
    from cogmem_api.engine import eval_helpers
    assert hasattr(eval_helpers, "build_generation_prompt")
    assert hasattr(eval_helpers, "build_judge_system_prompt")
    assert hasattr(eval_helpers, "parse_judge_response")
    print("PASS: eval_helpers still exports functions (backward compat)")


def main():
    tests = [
        test_prompts_reachable_via_toplevel,
        test_pass1_module_exists,
        test_pass2_module_exists,
        test_shared_module_exists,
        test_eval_modules_exist,
        test_build_pass1_prompt_returns_tuple,
        test_build_pass2_prompt_returns_string,
        test_eval_helpers_no_prompt_strings,
        test_eval_helpers_still_has_functions,
    ]
    passed = 0
    for test in tests:
        try:
            result = test()
            if result is False:
                print(f"  FAILED: {test.__name__}")
            else:
                passed += 1
        except Exception as exc:
            print(f"  ERROR: {test.__name__} -> {exc}")

    total = len(tests)
    print(f"\n{passed}/{total} PASS")
    return passed == total


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)