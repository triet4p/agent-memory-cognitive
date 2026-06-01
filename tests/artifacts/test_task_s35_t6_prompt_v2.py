"""S35-T6 artifact: prompt v2 dispatch + content guarantees.

Offline tests for the new build_generation_prompt_v2 + env dispatch:
  - Legacy default unchanged (S29-S34 byte-identical reproduction).
  - v2 has tightened dedup criterion (no 'shared attributes' wording from legacy).
  - v2 inlines raw_snippet under each MEMORY when include_snippets=True.
  - v2 omits separate REFERENCES block (consolidated into MEMORIES inline).
  - env dispatch in eval_helpers.build_generation_prompt routes correctly.

Run: uv run python tests/artifacts/test_task_s35_t6_prompt_v2.py
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from cogmem_api.engine import eval_helpers
from cogmem_api.prompts.eval.generate import (
    build_generation_prompt,
    build_generation_prompt_v2,
)


EVIDENCE = [
    {
        "text": "John won a basketball game by buzzer-beater",
        "raw_snippet": "[john]: Last week we won against the Bears with a buzzer-beater, 78-77.",
        "document_id": "D2",
    },
    {
        "text": "John won a basketball game vs top team",
        "raw_snippet": "[john]: In May 2026 we won against the top team in our division.",
        "document_id": "D6",
    },
]
QUERY = "How many games has John mentioned winning?"


def test_legacy_unchanged_no_env() -> None:
    os.environ.pop("COGMEM_API_GENERATE_PROMPT_VARIANT", None)
    p_legacy_direct = build_generation_prompt(QUERY, EVIDENCE, include_snippets=False)
    p_via_dispatch = eval_helpers.build_generation_prompt(QUERY, EVIDENCE, include_snippets=False)
    assert p_legacy_direct == p_via_dispatch
    # Legacy hallmark: the long mega-paragraph on knowledge-update HARD RULE
    assert "HARD RULE" in p_via_dispatch
    # Legacy hallmark: the "shared attributes (size, type, location, context)" criterion
    assert "shared attributes" in p_via_dispatch
    print("[ok] env unset -> dispatch returns legacy (HARD RULE + shared-attributes wording present)")


def test_legacy_explicit_env() -> None:
    os.environ["COGMEM_API_GENERATE_PROMPT_VARIANT"] = "legacy"
    try:
        p = eval_helpers.build_generation_prompt(QUERY, EVIDENCE, include_snippets=False)
        assert "HARD RULE" in p and "shared attributes" in p
        print("[ok] env=legacy -> legacy prompt")
    finally:
        os.environ.pop("COGMEM_API_GENERATE_PROMPT_VARIANT", None)


def test_v2_via_env_dispatch() -> None:
    os.environ["COGMEM_API_GENERATE_PROMPT_VARIANT"] = "v2"
    try:
        p = eval_helpers.build_generation_prompt(QUERY, EVIDENCE, include_snippets=False)
        # v2 must NOT contain legacy's mega paragraphs
        assert "HARD RULE" not in p, "v2 should drop legacy HARD RULE mega paragraph"
        assert "shared attributes" not in p, "v2 should drop legacy dedup criterion"
        # v2 must contain its tighter dedup language
        assert "explicit identifier" in p, "v2 should require explicit identifier for dedup"
        assert "Similar events at different dates" in p, "v2 should mark distinct events as distinct"
        print("[ok] env=v2 -> v2 prompt (tighter dedup, no HARD RULE)")
    finally:
        os.environ.pop("COGMEM_API_GENERATE_PROMPT_VARIANT", None)


def test_v2_inline_snippet_when_enabled() -> None:
    """v2 inlines verbatim source under each MEMORY (no separate REFERENCES block)."""
    p = build_generation_prompt_v2(QUERY, EVIDENCE, include_snippets=True)
    # Each fact's text appears
    assert "John won a basketball game by buzzer-beater" in p
    # Verbatim snippet appears inline under it
    assert "buzzer-beater, 78-77" in p, "raw_snippet content should be surfaced inline"
    assert 'src: "' in p, "v2 inline snippet format src: \"...\" should be present"
    # No separate REFERENCES block (consolidated into MEMORIES)
    assert "REFERENCES" not in p, "v2 should NOT have a separate REFERENCES block"
    print("[ok] v2 with include_snippets=True -> verbatim source inlined as src: \"...\"")


def test_v2_no_snippet_when_disabled() -> None:
    """v2 with include_snippets=False (S35 current default) → tighter-dedup rule still active,
    but no src: line (graceful fallback)."""
    p = build_generation_prompt_v2(QUERY, EVIDENCE, include_snippets=False)
    assert 'src: "' not in p
    assert "buzzer-beater, 78-77" not in p  # snippet content NOT leaked
    # Still have tightened dedup criterion
    assert "explicit identifier" in p
    print("[ok] v2 with include_snippets=False -> no src: line, but tighter dedup still applied")


def test_v2_legacy_signature_parity() -> None:
    """Both builders must accept identical kwargs for drop-in dispatch."""
    common = dict(
        query=QUERY, evidence=EVIDENCE,
        question_date="2026-05-30",
        session_date_map={"D2": "2026-05-22", "D6": "2026-05-28"},
        include_snippets=True,
    )
    p_legacy = build_generation_prompt(**common)
    p_v2 = build_generation_prompt_v2(**common)
    assert p_legacy != p_v2  # must be distinct prompts
    # Both should contain session-ordinal info from session_date_map
    assert "Session 1/2" in p_legacy and "Session 2/2" in p_legacy
    assert "Session 1/2" in p_v2 and "Session 2/2" in p_v2
    print("[ok] both builders share signature; produce distinct prompts; both honor session_date_map")


def test_v2_default_safe() -> None:
    """If env is garbage, dispatch falls back to legacy (safe default)."""
    for bad in ("invalid", "", "V2", "V2 ", " legacy "):  # case-insensitive normalize
        os.environ["COGMEM_API_GENERATE_PROMPT_VARIANT"] = bad
        try:
            p = eval_helpers.build_generation_prompt(QUERY, EVIDENCE, include_snippets=False)
            if bad.strip().lower() == "v2":
                assert "explicit identifier" in p, f"env={bad!r} should route to v2"
            else:
                assert "HARD RULE" in p, f"env={bad!r} should fall back to legacy, got v2-shaped"
        finally:
            os.environ.pop("COGMEM_API_GENERATE_PROMPT_VARIANT", None)
    print("[ok] env normalize: case-insensitive 'v2' routes to v2; anything else -> legacy")


def main() -> int:
    test_legacy_unchanged_no_env()
    test_legacy_explicit_env()
    test_v2_via_env_dispatch()
    test_v2_inline_snippet_when_enabled()
    test_v2_no_snippet_when_disabled()
    test_v2_legacy_signature_parity()
    test_v2_default_safe()
    print("\nS35-T6 PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
