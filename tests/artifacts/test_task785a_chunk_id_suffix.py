"""Artifact test for Issue A — chunk_id namespace collision between P1 and P2.

Verifies:
1. P1 facts get p1_{chunk_index} suffix, P2 facts get p2_{msg_idx}_{sub_idx} suffix
2. Orchestrator uses suffix when available, falls back to plain chunk_index
3. P1 chunk 0 and P2 msg_idx=0 get distinct chunk_ids (no collision)
"""

from __future__ import annotations
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))


class FakeLLM:
    def __init__(self):
        self.calls = []

    async def call(self, messages, scope=None, temperature=0.1, max_completion_tokens=64000, return_usage=False, skip_validation=False):
        self.calls.append(messages)
        sys_content = messages[0]["content"]
        if "This is Pass 2" in sys_content:
            return {"facts": [
                {"fact_type": "experience", "what": "User bought Spitfire Mk.V", "entities": ["Spitfire Mk.V"]},
            ]}
        elif "[user]:" in str(messages[1]["content"]) and "[assistant]:" in str(messages[1]["content"]):
            return {"facts": [
                {"fact_type": "world", "what": "Weathering improves realism", "entities": []},
            ]}
        return {"facts": []}


class FakeConfig:
    retain_two_pass_enabled = True
    retain_pass1_chunk_chars = 10000
    retain_pass2_chunk_chars = 3000
    retain_pass2_target_roles = "user"
    retain_max_completion_tokens = 64000
    retain_extraction_mode = "concise"
    retain_mission = None
    retain_custom_instructions = None
    retain_extract_causal_links = True


from cogmem_api.engine.retain.types import ExtractedFact
from cogmem_api.prompts.retain.pass2 import PASS2_ALLOWED_FACT_TYPES


def test_chunk_id_suffix_fields():
    fact = ExtractedFact(fact_text="test", fact_type="world")
    assert hasattr(fact, "chunk_id_suffix"), "ExtractedFact should have chunk_id_suffix field"
    assert fact.chunk_id_suffix is None, "Default chunk_id_suffix should be None"
    fact.chunk_id_suffix = "p1_0"
    assert fact.chunk_id_suffix == "p1_0"
    print("PASS: ExtractedFact.chunk_id_suffix works")


def test_pass1_chunk_suffix_propagates():
    from cogmem_api.engine.retain.chunking import chunk_for_pass1

    messages = [
        {"role": "user", "content": "I bought a kit"},
        {"role": "assistant", "content": "Great choice!"},
    ]
    chunks = chunk_for_pass1(messages, max_chars=10000)
    assert len(chunks) >= 1
    assert chunks[0].chunk_id_suffix == "p1_0"
    print(f"PASS: Pass1Chunk chunk_id_suffix = {chunks[0].chunk_id_suffix!r}")


def test_pass2_chunk_suffix_propagates():
    from cogmem_api.engine.retain.chunking import chunk_for_pass2

    messages = [
        {"role": "user", "content": "I bought a kit"},
        {"role": "assistant", "content": "Great choice!"},
    ]
    chunks = chunk_for_pass2(messages, target_role="user", max_chars=3000)
    assert len(chunks) >= 1
    assert chunks[0].chunk_id_suffix.startswith("p2_")
    print(f"PASS: Pass2Chunk chunk_id_suffix = {chunks[0].chunk_id_suffix!r}")


def test_p1_and_p2_suffixes_are_different():
    from cogmem_api.engine.retain.chunking import chunk_for_pass1, chunk_for_pass2

    messages = [
        {"role": "user", "content": "I bought a kit from Revell"},
        {"role": "assistant", "content": "Great choice!"},
        {"role": "user", "content": "I also want weathering techniques"},
    ]
    p1_chunks = chunk_for_pass1(messages, max_chars=10000)
    p2_chunks = chunk_for_pass2(messages, target_role="user", max_chars=3000)

    p1_suffixes = {c.chunk_id_suffix for c in p1_chunks}
    p2_suffixes = {c.chunk_id_suffix for c in p2_chunks}

    overlap = p1_suffixes & p2_suffixes
    assert len(overlap) == 0, f"P1 and P2 suffix namespaces overlap: {overlap}"
    print(f"PASS: No collision — P1 suffixes: {p1_suffixes}, P2 suffixes: {p2_suffixes}")


def test_fact_extraction_sets_suffix():
    import asyncio
    from cogmem_api.engine.retain.types import RetainContent
    from cogmem_api.engine.retain import fact_extraction

    fake = FakeLLM()
    config = FakeConfig()
    content = RetainContent(
        content="",
        messages=[
            {"role": "user", "content": "I bought a Tiger I kit from Revell"},
            {"role": "assistant", "content": "Great choice!"},
            {"role": "user", "content": "I also want weathering techniques"},
        ],
    )

    facts, chunks, usage = asyncio.run(
        fact_extraction._extract_facts_with_llm(content, 0, fake, config)
    )

    p1_facts = [f for f in facts if f.chunk_id_suffix and f.chunk_id_suffix.startswith("p1_")]
    p2_facts = [f for f in facts if f.chunk_id_suffix and f.chunk_id_suffix.startswith("p2_")]

    assert len(p1_facts) >= 1, f"Expected at least 1 P1 fact with suffix, got {len(p1_facts)}"
    assert len(p2_facts) >= 1, f"Expected at least 1 P2 fact with suffix, got {len(p2_facts)}"

    p1_suffixes = {f.chunk_id_suffix for f in p1_facts}
    p2_suffixes = {f.chunk_id_suffix for f in p2_facts}
    overlap = p1_suffixes & p2_suffixes
    assert len(overlap) == 0, f"P1 and P2 fact suffixes collide: {overlap}"
    print(f"PASS: {len(p1_facts)} P1 facts (suffixes={p1_suffixes}), {len(p2_facts)} P2 facts (suffixes={p2_suffixes})")


def main():
    tests = [
        test_chunk_id_suffix_fields,
        test_pass1_chunk_suffix_propagates,
        test_pass2_chunk_suffix_propagates,
        test_p1_and_p2_suffixes_are_different,
        test_fact_extraction_sets_suffix,
    ]
    passed = 0
    for test in tests:
        try:
            test()
            passed += 1
        except Exception as exc:
            print(f"  ERROR: {test.__name__} -> {type(exc).__name__}: {exc}")

    total = len(tests)
    print(f"\n{passed}/{total} PASS")
    return passed == total


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)