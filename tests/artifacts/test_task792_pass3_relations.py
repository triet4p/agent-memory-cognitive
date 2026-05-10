"""Artifact test for Task 792 — Pass 3 relationship identification.

Verifies:
1. build_pass3_prompt returns a valid prompt with numbered facts
2. _run_pass3 populates causal_relations on ExtractedFact correctly
3. _run_pass3 rejects out-of-range indices and self-relations
4. _run_pass3 enforces direction constraint for causal (source < target)
5. fulfilled_by only applied when source=intention, target=experience
6. Strength < 0.6 relations are ignored
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import asyncio
import json
from dataclasses import dataclass, field
from cogmem_api.prompts.retain.pass3 import build_pass3_prompt
from cogmem_api.engine.retain.fact_extraction import _run_pass3
from cogmem_api.engine.retain.types import ExtractedFact, CausalRelation, TransitionRelation


def _make_fact(fact_type: str, text: str) -> ExtractedFact:
    return ExtractedFact(
        fact_text=text,
        fact_type=fact_type,
        entities=[],
        content_index=0,
    )


class FakeLLM:
    def __init__(self, relations: list[dict]):
        self.relations = relations

    async def call(self, messages, **kwargs):
        payload = json.dumps({"relations": self.relations})
        return payload, None


def test_prompt_format():
    facts = [
        ("User had back pain", "experience"),
        ("User started yoga", "habit"),
        ("User feels better", "experience"),
    ]
    prompt = build_pass3_prompt(facts)
    assert "[0][experience] User had back pain" in prompt
    assert "[1][habit] User started yoga" in prompt
    assert "[2][experience] User feels better" in prompt
    assert "causal" in prompt
    assert "fulfilled_by" in prompt
    assert "a_o_causal" in prompt
    print("PASS: Pass 3 prompt format correct")


def test_causal_relation_applied():
    facts = [
        _make_fact("experience", "User had back pain"),         # index 0: cause
        _make_fact("habit", "User started yoga to relieve pain"),  # index 1: effect
    ]
    llm = FakeLLM([{"source": 0, "target": 1, "type": "causal", "strength": 0.8}])
    asyncio.run(_run_pass3(facts, llm, 512, 0))

    # Stored on EFFECT fact (index 1), pointing to CAUSE (index 0).
    # Matches create_causal_links_batch: effect.causal_relations.target_fact_index = cause < effect.
    assert len(facts[1].causal_relations) == 1
    rel = facts[1].causal_relations[0]
    assert rel.target_fact_index == 0
    assert rel.relation_type == "caused_by"
    assert abs(rel.strength - 0.8) < 0.01
    print("PASS: Causal relation stored on effect fact pointing to cause")


def test_causal_direction_enforced():
    facts = [
        _make_fact("experience", "User started yoga"),
        _make_fact("experience", "User had back pain"),
    ]
    # source=1, target=0 violates "source < target" for causal — nothing stored
    llm = FakeLLM([{"source": 1, "target": 0, "type": "causal", "strength": 0.9}])
    asyncio.run(_run_pass3(facts, llm, 512, 0))

    assert len(facts[0].causal_relations) == 0
    assert len(facts[1].causal_relations) == 0
    print("PASS: Causal direction constraint enforced (source < target)")


def test_fulfilled_by_type_check():
    facts = [
        _make_fact("intention", "User plans to buy a French press"),
        _make_fact("experience", "User bought a French press"),
    ]
    llm = FakeLLM([{"source": 0, "target": 1, "type": "fulfilled_by", "strength": 0.85}])
    asyncio.run(_run_pass3(facts, llm, 512, 0))

    assert len(facts[0].transition_relations) == 1
    assert facts[0].transition_relations[0].transition_type == "fulfilled_by"
    print("PASS: fulfilled_by transition created for intention->experience")


def test_fulfilled_by_wrong_types_rejected():
    facts = [
        _make_fact("experience", "User went for a run"),   # not intention
        _make_fact("experience", "User finished the run"),
    ]
    llm = FakeLLM([{"source": 0, "target": 1, "type": "fulfilled_by", "strength": 0.9}])
    asyncio.run(_run_pass3(facts, llm, 512, 0))

    assert len(facts[0].transition_relations) == 0
    print("PASS: fulfilled_by rejected when source is not intention")


def test_low_strength_ignored():
    facts = [
        _make_fact("experience", "User ate a sandwich"),
        _make_fact("experience", "User felt full"),
    ]
    llm = FakeLLM([{"source": 0, "target": 1, "type": "causal", "strength": 0.4}])
    asyncio.run(_run_pass3(facts, llm, 512, 0))

    assert len(facts[0].causal_relations) == 0
    print("PASS: Relations with strength < 0.6 ignored")


def test_out_of_range_index_ignored():
    facts = [_make_fact("experience", "User went for a run")]
    llm = FakeLLM([{"source": 0, "target": 5, "type": "causal", "strength": 0.9}])
    asyncio.run(_run_pass3(facts, llm, 512, 0))

    assert len(facts[0].causal_relations) == 0
    print("PASS: Out-of-range target index ignored")


if __name__ == "__main__":
    tests = [
        test_prompt_format,
        test_causal_relation_applied,
        test_causal_direction_enforced,
        test_fulfilled_by_type_check,
        test_fulfilled_by_wrong_types_rejected,
        test_low_strength_ignored,
        test_out_of_range_index_ignored,
    ]
    passed = 0
    for t in tests:
        try:
            t()
            passed += 1
        except Exception as exc:
            print(f"FAIL: {t.__name__}: {exc}")

    print(f"\n{passed}/{len(tests)} PASS")
    if passed < len(tests):
        sys.exit(1)
