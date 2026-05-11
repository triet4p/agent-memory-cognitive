"""Sprint S28 Wave-1 artifact test — R1, R3, R4, G1, G2.

Run:  uv run python -m tests.artifacts.test_task_s28_wave1
All checks are static (no server required).
"""
from __future__ import annotations

import re
import sys

# ──────────────────────────────────────────────────────────────────────────────
# R3: Causal pattern expansion
# ──────────────────────────────────────────────────────────────────────────────
def test_r3_causal_pattern():
    from cogmem_api.engine.query_analyzer import classify_query_type

    assert classify_query_type("I've been sneezing. Do you think it might be my living room?") == "causal", \
        "c029 query must now be classified as causal"
    assert classify_query_type("Could it be that the cat is causing the dust?") == "causal"
    # Ensure no regressions on multi_hop queries
    assert classify_query_type("How many model kits have I worked on or bought?") == "multi_hop", \
        "multi_hop queries must not be reclassified"
    assert classify_query_type("What is my favourite coffee?") == "preference", \
        "preference queries must not be reclassified"
    print("R3 PASS: causal pattern expansion correct, no false positives")


# ──────────────────────────────────────────────────────────────────────────────
# R1: BFSGraphRetriever adaptive per_source_limit + firing_quota
# ──────────────────────────────────────────────────────────────────────────────
def test_r1_bfs_adaptive():
    from cogmem_api.engine.search.graph_retrieval import BFSGraphRetriever

    default = BFSGraphRetriever()
    assert default.per_source_limit == 20, "default per_source_limit should be 20"
    assert default.firing_quota == 2, "default firing_quota should be 2"

    wide = BFSGraphRetriever(per_source_limit=25, firing_quota=3)
    assert wide.per_source_limit == 25
    assert wide.firing_quota == 3
    print("R1 PASS: BFSGraphRetriever accepts per_source_limit and firing_quota")


def test_r1_adaptive_in_retrieval():
    """Verify retrieve_all_fact_types_parallel creates a wider retriever for multi_hop."""
    import inspect
    import cogmem_api.engine.search.retrieval as ret_mod
    src = inspect.getsource(ret_mod.retrieve_all_fact_types_parallel)
    assert "multi_hop" in src and "per_source_limit=25" in src, \
        "retrieve_all_fact_types_parallel must branch on multi_hop with per_source_limit=25"
    assert "firing_quota=3" in src, \
        "retrieve_all_fact_types_parallel must set firing_quota=3 for multi_hop"
    print("R1 PASS: adaptive branch in retrieve_all_fact_types_parallel")


# ──────────────────────────────────────────────────────────────────────────────
# R4: Singleton session penalty
# ──────────────────────────────────────────────────────────────────────────────
def test_r4_singleton_penalty():
    import inspect
    import cogmem_api.engine.memory_engine as me_mod
    src = inspect.getsource(me_mod.MemoryEngine.recall_async)
    assert "_SINGLETON_PENALTY" in src, "recall_async must contain _SINGLETON_PENALTY"
    assert "0.85" in src, "singleton penalty factor must be 0.85"
    print("R4 PASS: singleton session penalty present in recall_async")


# ──────────────────────────────────────────────────────────────────────────────
# G1: Session temporal ordering in generation prompt
# ──────────────────────────────────────────────────────────────────────────────
def test_g1_session_ordering():
    from cogmem_api.prompts.eval.generate import build_generation_prompt

    evidence = [
        {"text": "User needs 125 stars for Gold.", "document_id": "sess_old"},
        {"text": "User needs 120 stars to reach Gold.", "document_id": "sess_new"},
    ]
    session_date_map = {"sess_old": "2023-03-01", "sess_new": "2023-08-15"}
    prompt = build_generation_prompt("How many stars for Gold?", evidence, session_date_map=session_date_map)

    assert "Session 1/2" in prompt, "older session must be labeled Session 1/2"
    assert "Session 2/2" in prompt, "newer session must be labeled Session 2/2"
    assert "more recent" in prompt, "newer session must be labeled 'more recent'"
    assert "older" in prompt, "older session must be labeled 'older'"
    print("G1 PASS: session ordering labels present in generated prompt")


def test_g1_session_ordering_instruction():
    from cogmem_api.prompts.eval.generate import build_generation_prompt

    prompt = build_generation_prompt("q", [], session_date_map={"s": "2024-01-01"})
    assert "Session N/N (more recent)" in prompt or "more recent" in prompt.lower(), \
        "prompt instructions must reference session ordering"
    print("G1 PASS: session ordering instruction in prompt")


# ──────────────────────────────────────────────────────────────────────────────
# G2: Generation prompt improvements
# ──────────────────────────────────────────────────────────────────────────────
def test_g2_prompt_improvements():
    from cogmem_api.prompts.eval.generate import build_generation_prompt

    prompt = build_generation_prompt("q", [])
    # c023: entity flexibility
    assert "flea market" in prompt or "different name" in prompt.lower() or "context clues" in prompt, \
        "G2 c023: entity-flexibility instruction missing"
    # c030: enumerate all
    assert "enumerate ALL" in prompt or "enumerate all" in prompt.lower(), \
        "G2 c030: enumerate-all instruction missing"
    # c032: prioritize top-ranked
    assert "most relevant first" in prompt or "top-ranked" in prompt.lower(), \
        "G2 c032: prioritize top-ranked instruction missing"
    print("G2 PASS: all three prompt improvements present")


# ──────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    failures = []
    for name, fn in list(globals().items()):
        if name.startswith("test_"):
            try:
                fn()
            except Exception as exc:
                failures.append((name, exc))
                print(f"FAIL {name}: {exc}")

    if failures:
        print(f"\n{len(failures)} test(s) failed.")
        sys.exit(1)
    else:
        print("\nAll S28 Wave-1 artifact tests PASSED.")
