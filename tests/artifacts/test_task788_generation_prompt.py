"""
Task 788: Fix generation prompt — MEMORIES + REFERENCES format.

Verifies build_generation_prompt:
1. Uses 'text' as MEMORIES (short, extracted facts)
2. Raw snippets: P1 multi-turn → assistant turns stripped, P2 user-only → kept as-is
3. First-person pronouns (I, I'm, my, me...) replaced with 'the user'/'the user's'
4. MEMORIES block comes before REFERENCES block
5. Items without raw_snippet don't appear in REFERENCES
6. QUESTION is prominently framed with === separator
7. REFERENCES section has explicit rules against answering embedded questions

Run:
    uv run python tests/artifacts/test_task788_generation_prompt.py
"""

from __future__ import annotations

import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from cogmem_api.prompts.eval.generate import (
    _clean_reference,
    _extract_user_turns,
    _to_third_person,
    build_generation_prompt,
)


# ---------------------------------------------------------------------------
# Unit tests for helper functions
# ---------------------------------------------------------------------------

def test_extract_user_turns_p2_passthrough():
    """P2 snippets (no markers) pass through unchanged."""
    snippet = "I'm looking for tips on photo-etching for my B-29 kit. Just got it at a model show."
    assert _extract_user_turns(snippet) == snippet
    print("  test_extract_user_turns_p2_passthrough: PASS")


def test_extract_user_turns_strips_assistant():
    """P1 snippets: assistant turns are stripped, only user text remains."""
    snippet = (
        "[user]: I'm looking for tips on photo-etching. "
        "By the way, I just got a B-29 kit at a model show. "
        "[assistant]: Great! Here are the steps: 1) Use a hold-and-fold tool... "
        "2) Apply a small amount of super glue... "
        "[user]: What about using Vallejo acrylics with the PE parts? "
        "[assistant]: Vallejo acrylics work well with PE. Apply primer first..."
    )
    result = _extract_user_turns(snippet)
    assert "[assistant]:" not in result, "assistant turns must be stripped"
    assert "[user]:" not in result, "[user]: markers must be stripped"
    assert "B-29 kit at a model show" in result, "first user turn content must be preserved"
    assert "Vallejo acrylics" in result, "second user turn content must be preserved"
    assert "hold-and-fold tool" not in result, "assistant content must be removed"
    assert "Apply primer first" not in result, "assistant content must be removed"
    print("  test_extract_user_turns_strips_assistant: PASS")


def test_to_third_person_basic():
    """I'm, I've, I'd, I'll, my, me are replaced; bare I is intentionally left alone."""
    cases = [
        ("I'm looking for tips", "the user is looking for tips"),
        ("I've been working on this", "the user has been working on this"),
        ("my model kit", "the user's model kit"),
        ("help me with this", "help the user with this"),
        ("I'd like to try photo-etching", "the user would like to try photo-etching"),
        ("I'll start tomorrow", "the user will start tomorrow"),
    ]
    for original, expected in cases:
        result = _to_third_person(original)
        assert result == expected, f"'{original}' => '{result}', expected '{expected}'"
    # Bare "I" is NOT replaced — avoids false positives on Roman numerals ("Tiger I")
    assert _to_third_person("I just got this kit") == "I just got this kit"
    assert _to_third_person("Tiger I diorama") == "Tiger I diorama"
    print("  test_to_third_person_basic: PASS")


def test_to_third_person_no_false_positives():
    """Words containing 'me', 'my', 'I' as substrings are not altered."""
    cases = [
        "implement this feature",  # 'me' inside 'implement'
        "some models",             # 'me' inside 'some'
        "timeline",                # 'me' inside 'timeline'
    ]
    for text in cases:
        result = _to_third_person(text)
        assert result == text, f"'{text}' was incorrectly modified to '{result}'"
    print("  test_to_third_person_no_false_positives: PASS")


def test_clean_reference_combines_both():
    """_clean_reference strips assistant turns AND replaces first-person pronouns."""
    snippet = (
        "[user]: I just got my B-29 kit at a model show. "
        "[assistant]: Great! Here's how to assemble it: step 1..."
    )
    result = _clean_reference(snippet)
    assert "[assistant]:" not in result
    assert "the user just got" in result or "the user" in result
    assert "the user's B-29 kit" in result or "the user" in result
    assert "step 1" not in result
    print("  test_clean_reference_combines_both: PASS")


# ---------------------------------------------------------------------------
# Integration tests for build_generation_prompt
# ---------------------------------------------------------------------------

def test_memories_references_structure():
    """MEMORIES uses text; REFERENCES uses cleaned raw_snippet; order preserved."""
    evidence = [
        {
            "text": "User purchased a 1/72 scale B-29 bomber model kit",
            "raw_snippet": "I'm looking for tips on photo-etching for my new 1/72 scale B-29 bomber kit.",
        },
        {
            "text": "User finished a 1/48 Revell F-15 Eagle model kit | When: late April",
            "raw_snippet": None,
        },
        {
            "text": "User started 1/16 Tiger I diorama",
            "raw_snippet": (
                "[user]: I'm working on a Tiger I diorama. How do I create water effects? "
                "[assistant]: Great choice! Use clear resin, layer by layer..."
            ),
        },
    ]
    prompt = build_generation_prompt("How many model kits have I worked on or bought?", evidence)

    assert "MEMORIES" in prompt
    assert "REFERENCES" in prompt
    assert "[1] User purchased a 1/72 scale B-29 bomber model kit" in prompt
    assert "[2] User finished a 1/48 Revell F-15 Eagle model kit" in prompt
    assert "[2-ref]" not in prompt, "no snippet → no entry in REFERENCES"
    assert "[1-ref]" in prompt
    assert "[3-ref]" in prompt
    assert prompt.index("MEMORIES") < prompt.index("REFERENCES")

    # Pronoun replacement in references — I'm → "the user is"
    assert "the user is" in prompt  # "I'm" in snippet[0] → "the user is"
    assert "I'm" not in prompt.split("REFERENCES")[1], "I'm must be replaced in REFERENCES"

    # Assistant content stripped from [3-ref]
    ref_block = prompt.split("REFERENCES")[1]
    assert "clear resin, layer by layer" not in ref_block, "assistant text must not appear in REFERENCES"
    assert "Tiger I diorama" in ref_block, "Roman numeral I must not be replaced"

    print("  test_memories_references_structure: PASS")


def test_question_emphasis():
    """Question is wrapped in === separators."""
    prompt = build_generation_prompt("How many model kits?", [{"text": "fact", "raw_snippet": None}])
    assert "QUESTION TO ANSWER: How many model kits?" in prompt
    assert "=" * 10 in prompt  # separator present
    print("  test_question_emphasis: PASS")


def test_references_rules_present():
    """REFERENCES block must include explicit rules about not answering embedded questions."""
    evidence = [{"text": "some fact", "raw_snippet": "I found a kit at the hobby store."}]
    prompt = build_generation_prompt("What kits do I own?", evidence)
    ref_section = prompt[prompt.index("REFERENCES"):]
    assert "Do NOT answer" in ref_section or "do NOT answer" in ref_section
    assert "the user" in ref_section  # rules mention 'the user'
    print("  test_references_rules_present: PASS")


def test_no_fabrication_instruction():
    """Prompt must instruct partial-evidence enumeration."""
    prompt = build_generation_prompt("Q?", [{"text": "partial fact", "raw_snippet": None}])
    assert "list may be incomplete" in prompt
    print("  test_no_fabrication_instruction: PASS")


def test_empty_evidence():
    """Empty evidence list → [No memories], no REFERENCES block."""
    prompt = build_generation_prompt("What did I buy?", [])
    assert "[No memories]" in prompt
    assert "REFERENCES (conversation excerpts" not in prompt
    print("  test_empty_evidence: PASS")


def test_only_text_no_snippets():
    """All items have text but no raw_snippet → no REFERENCES block body."""
    evidence = [
        {"text": "User prefers FastAPI", "raw_snippet": None},
        {"text": "User uses Python 3.12", "raw_snippet": None},
    ]
    prompt = build_generation_prompt("What stack do I use?", evidence)
    assert "[1] User prefers FastAPI" in prompt
    assert "[2] User uses Python 3.12" in prompt
    assert "[1-ref]" not in prompt
    assert "REFERENCES (conversation excerpts" not in prompt
    print("  test_only_text_no_snippets: PASS")


def main():
    print("Task 788: Generation prompt — MEMORIES + REFERENCES format")
    print("=" * 60)
    print("-- Helper unit tests --")
    test_extract_user_turns_p2_passthrough()
    test_extract_user_turns_strips_assistant()
    test_to_third_person_basic()
    test_to_third_person_no_false_positives()
    test_clean_reference_combines_both()
    print("-- Prompt integration tests --")
    test_memories_references_structure()
    test_question_emphasis()
    test_references_rules_present()
    test_no_fabrication_instruction()
    test_empty_evidence()
    test_only_text_no_snippets()
    print()
    print("ALL TESTS PASSED")


if __name__ == "__main__":
    main()
