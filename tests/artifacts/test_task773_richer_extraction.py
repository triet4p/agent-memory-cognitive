"""Task 773: Richer fact extraction (What+Why+Entity).

Verifies:
1. Prompt has "under 80 words" (not "under 40 words")
2. Prompt has why instruction for experience/intention
3. Prompt has "entities MUST NOT be empty" for experience/action_effect
"""

import sys


def test_prompt_80_words():
    path = "cogmem_api/engine/retain/fact_extraction.py"
    with open(path, "r", encoding="utf-8") as f:
        source = f.read()

    assert '"what": core statement, under 80 words' in source, (
        'Prompt must have "under 80 words" for what field'
    )
    assert '"under 40 words"' not in source, (
        'Prompt must NOT have "under 40 words" — replaced with 80 words'
    )


def test_prompt_why_experience_intention():
    path = "cogmem_api/engine/retain/fact_extraction.py"
    with open(path, "r", encoding="utf-8") as f:
        source = f.read()

    assert 'Include "why"' in source or '"why"' in source, (
        'Prompt must have instruction about "why" field for experience/intention'
    )
    assert "why" in source.lower(), (
        'Prompt must mention "why" in context of experience/intention'
    )


def test_prompt_entities_must_not_be_empty():
    path = "cogmem_api/engine/retain/fact_extraction.py"
    with open(path, "r", encoding="utf-8") as f:
        source = f.read()

    assert "MUST NOT be empty" in source, (
        'entities field must have "MUST NOT be empty" instruction for experience/action_effect'
    )


if __name__ == "__main__":
    test_prompt_80_words()
    test_prompt_why_experience_intention()
    test_prompt_entities_must_not_be_empty()
    print("3/3 PASS")
    sys.exit(0)