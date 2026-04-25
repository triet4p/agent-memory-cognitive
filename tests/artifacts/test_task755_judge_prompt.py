"""Task 755: Category-specific judge prompts — unit tests (no LLM required)."""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from scripts.eval_cogmem import _judge_system_prompt


def test_default_prompt_contains_generous_and_subset():
    p = _judge_system_prompt(None)
    assert "generous" in p, "Default prompt must encourage generous grading"
    assert "SUBSET" in p.upper() or "subset" in p, "Default prompt must mention subset rule"


def test_unknown_category_uses_default():
    p = _judge_system_prompt("unknown")
    assert "generous" in p


def test_temporal_prompt_contains_off_by_one():
    p = _judge_system_prompt("temporal")
    assert "off-by-one" in p or "off by one" in p.lower()


def test_temporal_reasoning_alias():
    assert _judge_system_prompt("temporal-reasoning") == _judge_system_prompt("temporal")


def test_knowledge_update_prompt():
    p = _judge_system_prompt("knowledge-update")
    assert "updated" in p.lower()
    assert "outdated" in p.lower() or "previous" in p.lower() or "alongside" in p.lower()


def test_abstention_prompt():
    p = _judge_system_prompt("abstention")
    assert "did not mention" in p or "not mentioned" in p.lower()
    assert "fabricates" in p.lower() or "fabricate" in p.lower()


def test_preference_prompt():
    p = _judge_system_prompt("preference")
    assert "personal information" in p.lower() or "personal" in p.lower()


def test_preference_alias():
    assert _judge_system_prompt("single-session-preference") == _judge_system_prompt("preference")


def test_all_prompts_contain_json_format():
    for cat in [None, "temporal", "knowledge-update", "preference", "abstention",
                "single-session", "multi-session", "single-hop", "causal"]:
        p = _judge_system_prompt(cat)
        assert '"correct"' in p and '"score"' in p and '"reason"' in p, \
            f"Prompt for category={cat!r} missing JSON format spec"


if __name__ == "__main__":
    tests = [v for k, v in list(globals().items()) if k.startswith("test_")]
    passed = failed = 0
    for fn in tests:
        try:
            fn()
            print(f"  PASS  {fn.__name__}")
            passed += 1
        except Exception as exc:
            print(f"  FAIL  {fn.__name__}: {exc}")
            failed += 1
    print(f"\n{passed} passed, {failed} failed")
    sys.exit(1 if failed else 0)
