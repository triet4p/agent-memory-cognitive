"""Sprint S29 Wave-2A artifact test — R-1, R-2, G-1..G-4, C-1.

Run:  uv run python -m tests.artifacts.test_task_s29_wave2a
All checks are static (no server required).
"""
from __future__ import annotations

import inspect
import sys

# ──────────────────────────────────────────────────────────────────────────────
# R-1: Preference pattern expansion (conversational signals)
# ──────────────────────────────────────────────────────────────────────────────
def test_r1_preference_expansion():
    from cogmem_api.engine.query_analyzer import classify_query_type

    # These 4 must now be 'preference'
    assert classify_query_type("Do you have any tips for using Suica in Tokyo?") == "preference", \
        "c030 must be preference"
    assert classify_query_type("Do you have helpful tips for packing electronics like a portable power bank?") == "preference", \
        "c031 must be preference"
    assert classify_query_type("I was wondering if you could remind me what I usually like to bake.") == "preference", \
        "c032 must be preference"
    assert classify_query_type("I'm thinking of inviting some friends for a bake-off any tips on what to bake?") == "preference", \
        "c033 must be preference"

    # No regression on existing patterns
    assert classify_query_type("What is my favourite coffee?") == "preference", \
        "classic preference must still work"
    assert classify_query_type("How many model kits have I bought?") == "multi_hop", \
        "multi_hop must not be reclassified"
    assert classify_query_type("Why is my cat sneezing?") == "causal", \
        "causal must not be reclassified"
    assert classify_query_type("What happened yesterday?") == "temporal", \
        "temporal must not be reclassified"

    print("R-1 PASS: preference pattern expanded, 4 queries reclassified, no regression")


# ──────────────────────────────────────────────────────────────────────────────
# R-2: Temporal anchor priority over multi_hop
# ──────────────────────────────────────────────────────────────────────────────
def test_r2_temporal_anchor():
    from cogmem_api.engine.query_analyzer import classify_query_type

    # c019 must now be temporal
    assert classify_query_type("How many days ago did I attend a baking class?") == "temporal", \
        "c019 must be temporal (ago anchor overrides multi_hop)"

    # No regression: multi_hop without temporal anchor stays multi_hop
    assert classify_query_type("How many model kits have I built?") == "multi_hop", \
        "multi_hop without temporal anchor must not change"
    assert classify_query_type("How many high-priority projects have I been involved in?") == "multi_hop", \
        "multi_hop without temporal anchor must not change"

    # Temporal without multi_hop stays temporal
    assert classify_query_type("What did I do last week?") == "temporal", \
        "pure temporal must not change"

    print("R-2 PASS: c019 reclassified temporal, no regression")


# ──────────────────────────────────────────────────────────────────────────────
# G-1..G-4: Generation instructions in generate.py
# ──────────────────────────────────────────────────────────────────────────────
def test_g1_persona_separation():
    from cogmem_api.prompts.eval.generate import build_generation_prompt
    prompt = build_generation_prompt("test", [{"text": "x", "document_id": "y"}], session_date_map={"y": "2024-01-01"})
    assert "examine subject/possessive cues" in prompt, "G-1: persona instruction missing"
    assert "sister's wedding" in prompt, "G-1: example missing"
    print("G-1 PASS: persona-separation instruction present")


def test_g2_scale_variant():
    from cogmem_api.prompts.eval.generate import build_generation_prompt
    prompt = build_generation_prompt("test", [{"text": "x", "document_id": "y"}], session_date_map={"y": "2024-01-01"})
    assert "scale/version variants of the same named product" in prompt, "G-2: scale variant instruction missing"
    assert "1/72 F-15 Eagle" in prompt, "G-2: example missing"
    print("G-2 PASS: scale-variant collapsing instruction present")


def test_g3_day_arithmetic():
    from cogmem_api.prompts.eval.generate import build_generation_prompt
    prompt = build_generation_prompt("test", [{"text": "x", "document_id": "y"}], session_date_map={"y": "2024-01-01"})
    assert "query_date - session_date in days" in prompt, "G-3: day-arithmetic instruction missing"
    assert "Show the arithmetic step-by-step" in prompt, "G-3: arithmetic process missing"
    print("G-3 PASS: day-arithmetic guidance present")


def test_g4_entity_aliasing():
    from cogmem_api.prompts.eval.generate import build_generation_prompt
    prompt = build_generation_prompt("test", [{"text": "x", "document_id": "y"}], session_date_map={"y": "2024-01-01"})
    assert "flea market find" in prompt, "G-4: acquisition context example missing"
    assert "painting of a sunset" in prompt, "G-4: visual description example missing"
    assert "UNLESS contradicted" in prompt, "G-4: fallback rule missing"
    # Old text must be replaced
    assert "recalled memory describes an item by" in prompt, "G-4 new text not found"
    print("G-4 PASS: entity-aliasing instruction strengthened")


# ──────────────────────────────────────────────────────────────────────────────
# C-1: Multi-channel-strong CE floor in memory_engine.py
# ──────────────────────────────────────────────────────────────────────────────
def test_c1_ce_floor_present():
    import cogmem_api.engine.memory_engine as me_mod
    src = inspect.getsource(me_mod)
    assert "_CONSENSUS_FLOOR_RANK" in src, "C-1: _CONSENSUS_FLOOR_RANK not found"
    assert "top_k if top_k is not None else 15" in src, \
        "C-1: floor rank must use top_k parameter, not hardcoded 15"
    assert "semantic_rank" in src and "bm25_rank" in src and "graph_rank" in src, \
        "C-1: channel rank checks not found"
    assert "combined_score < _threshold" in src, \
        "C-1: score promotion condition not found"
    print("C-1 PASS: CE floor uses top_k param (no hardcoded 15)")


# ──────────────────────────────────────────────────────────────────────────────
# Run all
# ──────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    tests = [
        ("R-1", test_r1_preference_expansion),
        ("R-2", test_r2_temporal_anchor),
        ("G-1", test_g1_persona_separation),
        ("G-2", test_g2_scale_variant),
        ("G-3", test_g3_day_arithmetic),
        ("G-4", test_g4_entity_aliasing),
        ("C-1", test_c1_ce_floor_present),
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
        print(f"RESULT: {len(tests)}/{len(tests)} PASS — Wave 2A gates PASS")
        sys.exit(0)
