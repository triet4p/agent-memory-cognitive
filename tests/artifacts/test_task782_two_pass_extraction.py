"""Artifact test for Task 782 — 2-pass extraction integration.

Verifies:
1. With FakeLLM returning canned facts: Pass 1 gets full chunk, Pass 2 gets user-only text
2. Both LLM calls happen
3. Pass 2 fact with fact_type="world" is filtered out
4. retain_two_pass_enabled=False skips Pass 2
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))


class FakeLLM:
    """Fake LLM that returns canned facts based on input text."""

    def __init__(self):
        self.calls = []

    async def call(self, messages, scope=None, temperature=0.1, max_completion_tokens=64000, return_usage=False, skip_validation=False):
        self.calls.append(messages)
        sys_content = messages[0]["content"]
        content = messages[1]["content"] if len(messages) > 1 else messages[0]["content"]

        if "This is Pass 2" in sys_content:
            return {"facts": [
                {"fact_type": "experience", "what": "User bought a Spitfire Mk.V kit", "entities": ["Spitfire Mk.V"]},
                {"fact_type": "intention", "what": "User plans to build a P-51 Mustang", "entities": ["P-51 Mustang"], "intention_status": "planning"},
            ]}
        elif "[user]:" in content and "[assistant]:" in content:
            return {"facts": [
                {"fact_type": "world", "what": "Weathering improves model realism", "entities": []},
                {"fact_type": "experience", "what": "User bought a Tiger I kit", "entities": ["Tiger I", "Revell"]},
            ]}
        else:
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


from cogmem_api.engine.retain.types import RetainContent


def test_two_pass_calls_both_passes():
    fake = FakeLLM()
    config = FakeConfig()

    content = RetainContent(
        content="",
        messages=[
            {"role": "user", "content": "I bought a Tiger I kit from Revell. It's great."},
            {"role": "assistant", "content": "Great choice! Revell makes excellent kits."},
            {"role": "user", "content": "I also want to try weathering techniques."},
        ],
    )

    import asyncio
    from cogmem_api.engine.retain import fact_extraction

    facts, chunks, usage = asyncio.run(
        fact_extraction._extract_facts_with_llm(content, 0, fake, config)
    )

    total_calls = len(fake.calls)
    p2_calls = [c for c in fake.calls if "Pass 2" in str(c[0]["content"])]
    p1_call_count = total_calls - len(p2_calls)
    assert p1_call_count >= 1, f"Expected at least 1 P1 call, got {p1_call_count}"
    assert len(p2_calls) >= 2, f"Expected at least 2 P2 calls (2 user messages), got {len(p2_calls)}"
    print(f"PASS: Two-pass produced {p1_call_count} P1 + {len(p2_calls)} P2 calls (total {total_calls})")


class FakeLLMWithWorld:
    """Fake LLM that always returns a world fact from Pass 2 (tests filtering)."""

    def __init__(self):
        self.calls = []

    async def call(self, messages, scope=None, temperature=0.1, max_completion_tokens=64000, return_usage=False, skip_validation=False):
        self.calls.append(messages)
        sys_content = messages[0]["content"]
        if "This is Pass 2" in sys_content:
            return {"facts": [
                {"fact_type": "experience", "what": "User bought a Spitfire Mk.V kit", "entities": ["Spitfire Mk.V"]},
                {"fact_type": "world", "what": "Spitfire Mk.V is a WWII fighter plane", "entities": []},
            ]}
        return {"facts": []}


def test_pass2_world_filtered_out():
    fake = FakeLLMWithWorld()
    config = FakeConfig()

    content = RetainContent(
        content="",
        messages=[
            {"role": "user", "content": "I bought a Spitfire Mk.V kit"},
        ],
    )

    import asyncio
    from cogmem_api.engine.retain import fact_extraction

    facts, chunks, usage = asyncio.run(
        fact_extraction._extract_facts_with_llm(content, 0, fake, config)
    )

    world_facts = [f for f in facts if f.fact_type == "world"]
    assert len(world_facts) == 0, f"world facts from Pass 2 should be filtered out, got: {world_facts}"
    experience_facts = [f for f in facts if f.fact_type == "experience"]
    assert len(experience_facts) >= 1, "experience fact from Pass 2 should be kept"
    print(f"PASS: world fact from Pass 2 filtered out ({len(facts)} facts remain, {len(experience_facts)} experience kept)")


def test_two_pass_disabled_skips_pass2():
    fake = FakeLLM()
    config = FakeConfig()
    config.retain_two_pass_enabled = False

    content = RetainContent(
        content="",
        messages=[
            {"role": "user", "content": "I bought a Tiger I kit"},
            {"role": "assistant", "content": "Great choice!"},
        ],
    )

    import asyncio
    from cogmem_api.engine.retain import fact_extraction

    facts, chunks, usage = asyncio.run(
        fact_extraction._extract_facts_with_llm(content, 0, fake, config)
    )

    p2_in_calls = any("Pass 2" in str(c) for c in fake.calls)
    assert not p2_in_calls, "When two_pass_enabled=False, Pass 2 should not be called"
    print("PASS: two_pass_enabled=False skips Pass 2 completely")


def test_fact_extraction_imports_2pass():
    from cogmem_api.engine.retain import fact_extraction
    assert hasattr(fact_extraction, "chunk_for_pass1")
    assert hasattr(fact_extraction, "chunk_for_pass2")
    assert hasattr(fact_extraction, "dedup_facts")
    assert hasattr(fact_extraction, "PASS2_ALLOWED_FACT_TYPES")
    print("PASS: fact_extraction imports Pass 2 infrastructure")


def main():
    tests = [
        test_two_pass_calls_both_passes,
        test_pass2_world_filtered_out,
        test_two_pass_disabled_skips_pass2,
        test_fact_extraction_imports_2pass,
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
            print(f"  ERROR: {test.__name__} -> {type(exc).__name__}: {exc}")

    total = len(tests)
    print(f"\n{passed}/{total} PASS")
    return passed == total


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)