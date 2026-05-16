"""Sprint S29 T-2 artifact test — entity blocklist extension.

Run:  uv run python tests/artifacts/test_s29_t2_entity_blocklist.py
"""
from __future__ import annotations

import sys


def test_blocklist_extended():
    """Check that _ENTITY_BLOCKLIST has the new generic nouns."""
    from cogmem_api.engine.retain.entity_processing import _ENTITY_BLOCKLIST

    for word in ("wedding", "project", "team", "class", "meeting", "birthday", "dinner", "trip", "cake", "model kit"):
        assert word in _ENTITY_BLOCKLIST, f"'{word}' missing from _ENTITY_BLOCKLIST"
    print(f"T-2 PASS: _ENTITY_BLOCKLIST extended with {len(_ENTITY_BLOCKLIST)} entries")


def test_blocked_generic_nouns():
    """Generic nouns alone should be blocked."""
    from cogmem_api.engine.retain.entity_processing import _is_allowed_entity

    for word in ("wedding", "project", "team", "class", "meeting", "birthday", "dinner", "trip", "cake", "model kit"):
        assert not _is_allowed_entity(word), f"'{word}' should be blocked"
    print("T-2 PASS: all generic nouns blocked by _is_allowed_entity")


def test_proper_nouns_allowed():
    """Proper nouns and modified entities should still be allowed."""
    from cogmem_api.engine.retain.entity_processing import _is_allowed_entity

    allowed = [
        "Rachel's wedding",
        "Project Alpha",
        "Team Bravo",
        "Tamiya 1/48 Spitfire Mk.V",
        "Luna",
        "Jen",
        "TripIt",
        "Memrise",
        "Suica",
        "Tokyo Tower",
        "New York City",
        "Alice",
    ]
    for entity in allowed:
        assert _is_allowed_entity(entity), f"'{entity}' should be allowed"
    print("T-2 PASS: all proper/modified entities allowed")


def test_pronouns_still_blocked():
    """Original blocklist entries still blocked."""
    from cogmem_api.engine.retain.entity_processing import _is_allowed_entity

    for word in ("user", "the user", "i", "me", "my", "we", "our"):
        assert not _is_allowed_entity(word), f"'{word}' should still be blocked"
    print("T-2 PASS: pronoun blocklist unchanged")


def test_link_creation_imports():
    """link_creation.py correctly imports _is_allowed_entity."""
    from cogmem_api.engine.retain.link_creation import create_cross_bank_structural_links_batch

    assert callable(create_cross_bank_structural_links_batch), "link_creation.py imports OK"
    print("T-2 PASS: link_creation.py imports _is_allowed_entity")


if __name__ == "__main__":
    tests = [
        ("blocklist-extended", test_blocklist_extended),
        ("blocked-generic", test_blocked_generic_nouns),
        ("proper-allowed", test_proper_nouns_allowed),
        ("pronouns-blocked", test_pronouns_still_blocked),
        ("link-creation-import", test_link_creation_imports),
    ]

    failures = 0
    for name, fn in tests:
        try:
            fn()
        except Exception as e:
            print(f"FAIL T-2/{name}: {e}")
            failures += 1

    print()
    if failures:
        print(f"RESULT: {len(tests) - failures}/{len(tests)} PASS, {failures} FAIL")
        sys.exit(1)
    else:
        print(f"RESULT: {len(tests)}/{len(tests)} PASS — T-2 entity blocklist gates PASS")
        sys.exit(0)
