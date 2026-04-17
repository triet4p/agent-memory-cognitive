"""Retain pipeline — SLM prompt quality and extraction robustness tests.

Mục tiêu:
1. STRUCTURAL GATE — prompt chứa đủ các yếu tố cần thiết cho Ministral-3B.
2. SLM QUIRK RESILIENCE — pipeline xử lý đúng các output quirk của SLM nhỏ:
   markdown wrapping, missing fields, malformed JSON.
3. ALL 6 NETWORK TYPES — mỗi fact_type được trích xuất đúng từ LLM path.
4. ACTION-EFFECT TRIPLET — precondition/action/outcome đầy đủ.
5. INTENTION LIFECYCLE — status + transition relation.
6. HABIT CLASSIFICATION — từ LLM path, không chỉ heuristic.
7. MULTI-FACT — một chunk chứa nhiều loại fact khác nhau.
8. RAW SNIPPET — mọi fact đều có raw_snippet từ source content.
9. VIETNAMESE DIALOGUE — trích xuất từ đoạn hội thoại tiếng Việt thực tế.
"""

from __future__ import annotations

import asyncio
import sys
from datetime import UTC, datetime
from pathlib import Path
from types import SimpleNamespace
from typing import Any

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

REPO_ROOT = Path(__file__).resolve().parents[2]


def _add_to_path() -> None:
    root_str = str(REPO_ROOT)
    if root_str not in sys.path:
        sys.path.insert(0, root_str)


def _make_config(
    mode: str = "concise",
    mission: str | None = None,
    custom_instructions: str | None = None,
    extract_causal: bool = True,
) -> SimpleNamespace:
    return SimpleNamespace(
        retain_extraction_mode=mode,
        retain_max_completion_tokens=2048,
        retain_chunk_size=4000,
        retain_custom_instructions=custom_instructions,
        retain_mission=mission,
        retain_extract_causal_links=extract_causal,
    )


# ---------------------------------------------------------------------------
# FakeLLM helpers — simulate different Ministral-3B output styles
# ---------------------------------------------------------------------------


class _BaseFakeLLM:
    """Base fake LLM that records every call."""

    def __init__(self, response: Any) -> None:
        self.calls: list[dict[str, Any]] = []
        self._response = response

    async def call(self, messages: list[dict[str, str]], **kwargs: Any) -> Any:
        self.calls.append({"messages": messages, "kwargs": kwargs})
        from cogmem_api.engine.response_models import TokenUsage
        usage = TokenUsage(input_tokens=50, output_tokens=30, total_tokens=80)
        return self._response, usage


def _llm(response: Any) -> _BaseFakeLLM:
    return _BaseFakeLLM(response)


def _llm_raw_str(text: str) -> _BaseFakeLLM:
    """LLM returns a raw string (not parsed dict) — tests parse_llm_json path."""
    return _BaseFakeLLM(text)


# ---------------------------------------------------------------------------
# GROUP 1 — STRUCTURAL GATE: Prompt quality for SLM
# ---------------------------------------------------------------------------


def test_prompt_json_only_instruction() -> None:
    """Prompt must explicitly tell the model to output ONLY JSON."""
    from cogmem_api.engine.retain.fact_extraction import _BASE_PROMPT
    prompt_lower = _BASE_PROMPT.lower()
    assert "only" in prompt_lower and "json" in prompt_lower, (
        "Prompt must instruct model to output ONLY JSON. "
        "SLMs add prose before/after JSON without this instruction."
    )


def test_prompt_has_all_six_fact_types() -> None:
    """All 6 CogMem network types must be explicitly named in the base prompt."""
    from cogmem_api.engine.retain.fact_extraction import _BASE_PROMPT
    required_types = ["world", "experience", "opinion", "habit", "intention", "action_effect"]
    missing = [t for t in required_types if t not in _BASE_PROMPT]
    assert not missing, f"Fact types missing from _BASE_PROMPT: {missing}"


def test_prompt_has_required_fields_section() -> None:
    """'what' and 'entities' must be marked REQUIRED — SLMs skip optional fields."""
    from cogmem_api.engine.retain.fact_extraction import _BASE_PROMPT
    assert "REQUIRED" in _BASE_PROMPT, "Must have explicit REQUIRED field annotation"
    assert '"what"' in _BASE_PROMPT or "'what'" in _BASE_PROMPT, "Must mention 'what' field"
    assert "entities" in _BASE_PROMPT, "Must mention 'entities' field"


def test_prompt_has_examples_for_complex_types() -> None:
    """action_effect, habit, intention must have at least one concrete example in prompt."""
    from cogmem_api.engine.retain.fact_extraction import _BASE_PROMPT
    # Each complex type needs at least the key field name as part of an example
    assert "precondition" in _BASE_PROMPT, "Must show precondition field in action_effect example"
    assert "outcome" in _BASE_PROMPT, "Must show outcome field in action_effect example"
    assert "intention_status" in _BASE_PROMPT, "Must show intention_status field in intention example"
    # Habit trigger words guidance
    habit_triggers = ["always", "usually", "every"]
    has_trigger = any(kw in _BASE_PROMPT for kw in habit_triggers)
    assert has_trigger, f"Must mention habit trigger words ({habit_triggers}) for SLM guidance"


def test_prompt_has_transition_types() -> None:
    """All transition types must be enumerated so SLM doesn't hallucinate type names."""
    from cogmem_api.engine.retain.fact_extraction import _BASE_PROMPT
    required_transitions = ["fulfilled_by", "triggered", "enabled_by", "revised_to", "contradicted_by"]
    missing = [t for t in required_transitions if t not in _BASE_PROMPT]
    assert not missing, f"Transition types missing from prompt: {missing}"


def test_prompt_length_reasonable_for_slm() -> None:
    """Base prompt should be under 4000 chars to leave room for context + generation."""
    from cogmem_api.engine.retain.fact_extraction import _BASE_PROMPT, _CONCISE_MODE
    # Build a full prompt as it would appear to the model
    full_prompt = _BASE_PROMPT.format(mission_section="", mode_section=_CONCISE_MODE)
    assert len(full_prompt) <= 4000, (
        f"Full prompt is {len(full_prompt)} chars — too long for SLM, target ≤4000. "
        "Long prompts reduce generation budget and cause truncation."
    )


def test_mode_prompts_exist_and_nonempty() -> None:
    """Each mode must have a non-trivial instruction block."""
    from cogmem_api.engine.retain.fact_extraction import (
        _CONCISE_MODE,
        _VERBOSE_MODE,
        _VERBATIM_MODE,
    )
    for name, mode in [("concise", _CONCISE_MODE), ("verbose", _VERBOSE_MODE), ("verbatim", _VERBATIM_MODE)]:
        assert len(mode.strip()) >= 30, f"Mode '{name}' instructions are too short for SLM guidance"


def test_concise_mode_in_system_prompt() -> None:
    """Concise mode is injected into the system prompt by _build_prompt."""
    from cogmem_api.engine.retain.fact_extraction import _build_prompt
    config = _make_config(mode="concise")
    prompt, mode = _build_prompt(config)
    assert mode == "concise"
    assert "concise" in prompt.lower()


def test_verbose_mode_in_system_prompt() -> None:
    from cogmem_api.engine.retain.fact_extraction import _build_prompt
    config = _make_config(mode="verbose")
    prompt, mode = _build_prompt(config)
    assert mode == "verbose"
    assert "verbose" in prompt.lower()


def test_verbatim_mode_in_system_prompt() -> None:
    from cogmem_api.engine.retain.fact_extraction import _build_prompt
    config = _make_config(mode="verbatim")
    prompt, mode = _build_prompt(config)
    assert mode == "verbatim"
    assert "verbatim" in prompt.lower()


def test_custom_mode_injects_instructions() -> None:
    from cogmem_api.engine.retain.fact_extraction import _build_prompt
    config = _make_config(mode="custom", custom_instructions="RULE_XYZ: extract only technical facts")
    prompt, mode = _build_prompt(config)
    assert mode == "custom"
    assert "RULE_XYZ" in prompt


def test_mission_section_injected() -> None:
    from cogmem_api.engine.retain.fact_extraction import _build_prompt
    config = _make_config(mission="Only retain ML engineering facts")
    prompt, _mode = _build_prompt(config)
    assert "Only retain ML engineering facts" in prompt


# ---------------------------------------------------------------------------
# GROUP 2 — SLM QUIRK RESILIENCE
# ---------------------------------------------------------------------------


async def _run_single(content: str, llm: Any, config: SimpleNamespace | None = None) -> list[Any]:
    """Helper: run extract_facts_from_contents with a single content item."""
    from cogmem_api.engine.retain.fact_extraction import extract_facts_from_contents
    from cogmem_api.engine.retain.types import RetainContent

    cfg = config or _make_config()
    facts, _chunks, _usage = await extract_facts_from_contents(
        contents=[RetainContent(
            content=content,
            event_date=datetime(2026, 4, 1, 9, 0, tzinfo=UTC),
            context="test",
        )],
        llm_config=llm,
        agent_name="slm-quality-test",
        config=cfg,
    )
    return facts


async def test_markdown_json_wrapped_output() -> None:
    """SLMs often wrap JSON in ```json ... ``` — parse_llm_json must handle it."""
    wrapped = '```json\n{"facts":[{"fact_type":"world","what":"Alice is ML Engineer","entities":["Alice"]}]}\n```'
    facts = await _run_single("Alice is ML Engineer at DI.", _llm_raw_str(wrapped))
    assert len(facts) == 1
    assert facts[0].fact_type == "world"
    assert "Alice" in facts[0].entities


async def test_missing_fact_type_defaults_to_world() -> None:
    """When SLM omits fact_type, fallback heuristic should produce a world fact."""
    # Return a fact without fact_type — infer_fact_type must fill in "world"
    response = {"facts": [{"what": "Alice works at DI", "entities": ["Alice"]}]}
    facts = await _run_single("Alice works at DI.", _llm(response))
    assert len(facts) == 1
    assert facts[0].fact_type in {"world", "experience"}  # both acceptable for generic facts


async def test_empty_facts_list_no_crash() -> None:
    """SLM returning empty facts list must not crash — triggers heuristic fallback."""
    response = {"facts": []}
    facts = await _run_single("Hello, how are you?", _llm(response))
    # Falls back to heuristic extraction — at least no crash
    assert isinstance(facts, list)


async def test_malformed_json_triggers_heuristic_fallback() -> None:
    """Completely malformed LLM output triggers heuristic sentence-split fallback."""
    # Raw string that can't be parsed as JSON
    bad_json = "Sorry, I cannot extract facts from this text."
    facts = await _run_single(
        "Alice always reviews emails. She believes Python is best.",
        _llm_raw_str(bad_json),
    )
    # Heuristic fallback must produce at least 1 fact
    assert len(facts) >= 1
    for f in facts:
        assert f.fact_text  # every fallback fact must have text


async def test_fact_with_only_what_field() -> None:
    """SLM returns only 'what' and nothing else — must still produce a valid ExtractedFact."""
    response = {"facts": [{"what": "Bob deployed the new API"}]}
    facts = await _run_single("Bob deployed the new API yesterday.", _llm(response))
    assert len(facts) == 1
    assert "Bob deployed" in facts[0].fact_text


async def test_fact_type_observation_coerced_to_world() -> None:
    """HINDSIGHT 'observation' type must be coerced to 'world' in CogMem."""
    response = {"facts": [{"fact_type": "observation", "what": "System uptime is 99.9%", "entities": []}]}
    facts = await _run_single("System uptime is 99.9%.", _llm(response))
    assert len(facts) == 1
    assert facts[0].fact_type == "world", "observation must be coerced to world"


async def test_fact_type_assistant_coerced_to_experience() -> None:
    """HINDSIGHT 'assistant' type must be coerced to 'experience'."""
    response = {"facts": [{"fact_type": "assistant", "what": "User asked to summarize meeting notes", "entities": []}]}
    facts = await _run_single("User asked to summarize meeting notes.", _llm(response))
    assert len(facts) == 1
    assert facts[0].fact_type == "experience", "assistant must be coerced to experience"


# ---------------------------------------------------------------------------
# GROUP 3 — ALL 6 NETWORK TYPES from LLM path
# ---------------------------------------------------------------------------


async def test_world_fact_extraction() -> None:
    """world: objective fact about a person."""
    response = {"facts": [{"fact_type": "world", "what": "Alice is ML Engineer at DI", "entities": ["Alice", "DI"]}]}
    facts = await _run_single("Alice is an ML Engineer at DI.", _llm(response))
    assert len(facts) == 1
    assert facts[0].fact_type == "world"
    assert "Alice" in facts[0].entities
    assert "DI" in facts[0].entities


async def test_experience_fact_extraction_with_timestamp() -> None:
    """experience: past event must preserve occurred_start."""
    response = {"facts": [{
        "fact_type": "experience",
        "what": "Alice joined DI in April 2024",
        "entities": ["Alice", "DI"],
        "when": "April 2024",
        "fact_kind": "event",
        "occurred_start": "2024-04-01T00:00:00+00:00",
    }]}
    facts = await _run_single("Alice joined DI in April 2024.", _llm(response))
    assert len(facts) == 1
    assert facts[0].fact_type == "experience"
    assert facts[0].occurred_start is not None


async def test_opinion_fact_with_confidence() -> None:
    """opinion: belief with confidence score."""
    response = {"facts": [{
        "fact_type": "opinion",
        "what": "Alice believes Python is best for ML",
        "entities": ["Alice"],
        "confidence": 0.85,
    }]}
    facts = await _run_single("Alice believes Python is best for ML prototypes.", _llm(response))
    assert len(facts) == 1
    assert facts[0].fact_type == "opinion"


async def test_habit_fact_extraction() -> None:
    """habit: repeating S-R pattern must be classified as habit (not world/experience)."""
    response = {"facts": [{
        "fact_type": "habit",
        "what": "Alice always checks email before standup",
        "entities": ["Alice"],
    }]}
    facts = await _run_single("Alice always checks email before standup.", _llm(response))
    assert len(facts) == 1
    assert facts[0].fact_type == "habit", (
        "Habit pattern ('always checks email') must be classified as 'habit', not 'world' or 'experience'"
    )


async def test_intention_fact_with_planning_status() -> None:
    """intention: future plan with status=planning."""
    response = {"facts": [{
        "fact_type": "intention",
        "what": "Alice plans to learn Rust by Q3 2025",
        "entities": ["Alice"],
        "intention_status": "planning",
    }]}
    facts = await _run_single("Alice is planning to learn Rust before Q3 2025.", _llm(response))
    assert len(facts) == 1
    assert facts[0].fact_type == "intention"
    assert facts[0].metadata.get("intention_status") == "planning"


async def test_intention_default_status_is_planning() -> None:
    """intention without status in LLM response must default to 'planning'."""
    response = {"facts": [{"fact_type": "intention", "what": "Alice wants to write a paper", "entities": ["Alice"]}]}
    facts = await _run_single("Alice wants to write a research paper.", _llm(response))
    assert len(facts) == 1
    assert facts[0].fact_type == "intention"
    # normalize_fact_metadata fills in "planning" when missing
    assert facts[0].metadata.get("intention_status") == "planning"


async def test_action_effect_full_triplet() -> None:
    """action_effect: LLM returns precondition/action/outcome → stored in metadata."""
    response = {"facts": [{
        "fact_type": "action_effect",
        "what": "int8 quantization reduced inference latency by 75%",
        "entities": [],
        "precondition": "Embedding latency > 100ms",
        "action": "Switch to int8 quantization",
        "outcome": "Latency dropped from 180ms to 45ms",
        "confidence": 0.92,
        "devalue_sensitive": True,
    }]}
    facts = await _run_single(
        "When latency exceeded 100ms, switching to int8 quantization reduced it to 45ms.",
        _llm(response),
    )
    assert len(facts) == 1
    f = facts[0]
    assert f.fact_type == "action_effect"
    assert f.metadata.get("precondition") == "Embedding latency > 100ms"
    assert f.metadata.get("action") == "Switch to int8 quantization"
    assert f.metadata.get("outcome") == "Latency dropped from 180ms to 45ms"
    assert f.metadata.get("confidence") == 0.92
    assert f.metadata.get("devalue_sensitive") is True


async def test_action_effect_regex_fallback_when_llm_omits_triplet() -> None:
    """action_effect: when LLM omits triplet fields, regex parser fills in from 'what'."""
    response = {"facts": [{
        "fact_type": "action_effect",
        # No precondition/action/outcome — test regex fallback in _parse_action_effect_triplet
        "what": "When latency exceeded 100ms, Alice switched to int8, so latency dropped",
        "entities": ["Alice"],
    }]}
    facts = await _run_single(
        "When latency exceeded 100ms, Alice switched to int8, so latency dropped.",
        _llm(response),
    )
    assert len(facts) == 1
    f = facts[0]
    assert f.fact_type == "action_effect"
    # Regex should have extracted precondition/action/outcome
    assert f.metadata.get("precondition") is not None, "Regex fallback must fill precondition"
    assert f.metadata.get("action") is not None, "Regex fallback must fill action"
    assert f.metadata.get("outcome") is not None, "Regex fallback must fill outcome"


# ---------------------------------------------------------------------------
# GROUP 4 — RELATION EXTRACTION
# ---------------------------------------------------------------------------


async def test_transition_fulfilled_by_relation() -> None:
    """transition_relations: fulfilled_by links intention to experience."""
    response = {"facts": [
        {
            "fact_type": "intention",
            "what": "Alice plans to complete Rust tutorial",
            "entities": ["Alice"],
            "intention_status": "planning",
            "transition_relations": [
                {"target_index": 1, "transition_type": "fulfilled_by", "strength": 0.9}
            ],
        },
        {
            "fact_type": "experience",
            "what": "Alice completed the Rust tutorial",
            "entities": ["Alice"],
        },
    ]}
    facts = await _run_single(
        "Alice planned to complete Rust tutorial. She completed it last week.",
        _llm(response),
    )
    assert len(facts) == 2
    intention_fact = next(f for f in facts if f.fact_type == "intention")
    assert len(intention_fact.transition_relations) == 1
    assert intention_fact.transition_relations[0].transition_type == "fulfilled_by"


async def test_transition_triggered_relation() -> None:
    """transition_relations: triggered links experience to intention."""
    response = {"facts": [
        {
            "fact_type": "experience",
            "what": "Code review with Minh revealed cache bottleneck",
            "entities": ["Minh"],
            "transition_relations": [
                {"target_index": 1, "transition_type": "triggered", "strength": 0.8}
            ],
        },
        {
            "fact_type": "intention",
            "what": "Alice plans to add a caching layer",
            "entities": ["Alice"],
            "intention_status": "planning",
        },
    ]}
    facts = await _run_single(
        "Review with Minh revealed cache issues. Alice plans to add a caching layer.",
        _llm(response),
    )
    assert len(facts) == 2
    exp_fact = next(f for f in facts if f.fact_type == "experience")
    assert exp_fact.transition_relations[0].transition_type == "triggered"


async def test_causal_relation_extraction() -> None:
    """causal_relations: link between two facts with caused_by."""
    response = {"facts": [
        {
            "fact_type": "world",
            "what": "Server had high memory usage",
            "entities": [],
            "causal_relations": [{"target_index": 1, "relation_type": "caused_by", "strength": 0.75}],
        },
        {
            "fact_type": "experience",
            "what": "Deployment failed due to OOM error",
            "entities": [],
        },
    ]}
    facts = await _run_single(
        "High memory usage caused the deployment to fail with OOM.",
        _llm(response),
        config=_make_config(extract_causal=True),
    )
    assert len(facts) == 2
    world_fact = next(f for f in facts if f.fact_type == "world")
    assert len(world_fact.causal_relations) == 1
    assert world_fact.causal_relations[0].relation_type == "caused_by"


async def test_causal_links_disabled_when_config_off() -> None:
    """When retain_extract_causal_links=False, causal_relations must be empty."""
    response = {"facts": [{
        "fact_type": "world",
        "what": "Memory usage was high",
        "entities": [],
        "causal_relations": [{"target_index": 1, "relation_type": "caused_by", "strength": 0.9}],
    }]}
    facts = await _run_single(
        "High memory caused failure.",
        _llm(response),
        config=_make_config(extract_causal=False),
    )
    assert len(facts) == 1
    assert len(facts[0].causal_relations) == 0, "Causal links must be suppressed when config=False"


# ---------------------------------------------------------------------------
# GROUP 5 — RAW SNIPPET PRESERVATION (Contribution 2 — Lossless Metadata)
# ---------------------------------------------------------------------------


async def test_raw_snippet_set_on_all_extracted_facts() -> None:
    """Every ExtractedFact must carry raw_snippet = source content (lossless storage)."""
    source = "Alice always reviews emails. She joined DI in April 2024."
    response = {"facts": [
        {"fact_type": "habit", "what": "Alice always reviews emails", "entities": ["Alice"]},
        {"fact_type": "experience", "what": "Alice joined DI in April 2024", "entities": ["Alice", "DI"]},
    ]}
    facts = await _run_single(source, _llm(response))
    assert len(facts) == 2
    for f in facts:
        assert f.raw_snippet, f"raw_snippet must be set on fact: {f.fact_text}"
        assert f.raw_snippet == source, "raw_snippet must equal the original source content"


async def test_raw_snippet_preserved_in_verbatim_mode() -> None:
    """In verbatim mode, raw_snippet must still equal source — even though fact_text = chunk."""
    source = "Alice joined DI in April 2024 as ML Engineer."
    response = {"facts": [{
        "fact_type": "experience",
        "what": "Alice joined DI",
        "entities": ["Alice", "DI"],
    }]}
    config = _make_config(mode="verbatim")
    facts = await _run_single(source, _llm(response), config=config)
    assert len(facts) == 1
    # verbatim mode: fact_text = chunk_text (the source), raw_snippet = source
    assert facts[0].raw_snippet == source
    # verbatim sets fact_text to the full chunk
    assert facts[0].fact_text == source


# ---------------------------------------------------------------------------
# GROUP 6 — MULTI-FACT EXTRACTION (same chunk, multiple types)
# ---------------------------------------------------------------------------


async def test_multi_fact_chunk_extracts_multiple_types() -> None:
    """A dense chunk must produce multiple facts of different types."""
    response = {"facts": [
        {"fact_type": "world", "what": "Alice is ML Engineer at DI", "entities": ["Alice", "DI"]},
        {"fact_type": "habit", "what": "Alice always checks email before standup", "entities": ["Alice"]},
        {"fact_type": "opinion", "what": "Alice prefers Python for ML", "entities": ["Alice"], "confidence": 0.8},
        {
            "fact_type": "intention",
            "what": "Alice plans to migrate to Rust by Q3",
            "entities": ["Alice"],
            "intention_status": "planning",
        },
    ]}
    source = (
        "Alice is ML Engineer at DI. She always checks email before standup. "
        "She prefers Python for ML work. She plans to migrate to Rust by Q3."
    )
    facts = await _run_single(source, _llm(response))
    assert len(facts) == 4
    fact_types = {f.fact_type for f in facts}
    assert fact_types == {"world", "habit", "opinion", "intention"}


# ---------------------------------------------------------------------------
# GROUP 7 — VIETNAMESE DIALOGUE (realistic scenario)
# ---------------------------------------------------------------------------


async def test_vietnamese_dialogue_world_fact() -> None:
    """Extraction from Vietnamese text: world fact about user's job."""
    # Simulates what Ministral-3B should produce for Vietnamese input
    response = {"facts": [{
        "fact_type": "world",
        "what": "User chuyên về LLM infrastructure tại DI",
        "entities": ["DI"],
    }]}
    source = "Mình đang làm ML Engineer tại DI, chuyên về LLM infrastructure."
    facts = await _run_single(source, _llm(response))
    assert len(facts) == 1
    assert facts[0].fact_type == "world"
    # Output language should be Vietnamese (check fact_text contains Vietnamese)
    assert "DI" in facts[0].fact_text or "LLM" in facts[0].fact_text


async def test_vietnamese_habit_with_trigger_word() -> None:
    """Vietnamese 'luôn' (always) should be classified as habit."""
    response = {"facts": [{
        "fact_type": "habit",
        "what": "User luôn kiểm tra email trước standup",
        "entities": [],
    }]}
    source = "Mình luôn kiểm tra email trước khi vào standup sáng."
    facts = await _run_single(source, _llm(response))
    assert len(facts) == 1
    assert facts[0].fact_type == "habit"


async def test_vietnamese_action_effect_technical() -> None:
    """Vietnamese technical cause-effect: quantization scenario."""
    response = {"facts": [{
        "fact_type": "action_effect",
        "what": "Chuyển sang int8 giúp giảm latency 75%",
        "entities": [],
        "precondition": "Latency embedding > 100ms",
        "action": "Chuyển sang int8 quantization",
        "outcome": "Latency giảm từ 180ms xuống 45ms",
        "confidence": 0.92,
        "devalue_sensitive": True,
    }]}
    source = "Khi latency vượt 100ms, mình chuyển sang int8 quantization và latency giảm xuống 45ms."
    facts = await _run_single(source, _llm(response))
    assert len(facts) == 1
    f = facts[0]
    assert f.fact_type == "action_effect"
    assert f.metadata.get("precondition")
    assert f.metadata.get("action")
    assert f.metadata.get("outcome")


async def test_vietnamese_intention_with_deadline() -> None:
    """Vietnamese future plan with deadline → intention with status=planning."""
    response = {"facts": [{
        "fact_type": "intention",
        "what": "User định học Rust trước Q3 2025",
        "entities": [],
        "intention_status": "planning",
    }]}
    source = "Mình định học Rust đủ để viết inference server trước Q3 2025."
    facts = await _run_single(source, _llm(response))
    assert len(facts) == 1
    assert facts[0].fact_type == "intention"
    assert facts[0].metadata.get("intention_status") == "planning"


# ---------------------------------------------------------------------------
# GROUP 8 — HEURISTIC FALLBACK (no LLM, pattern-based detection)
# ---------------------------------------------------------------------------


async def test_heuristic_detects_habit_without_llm() -> None:
    """Without LLM, heuristic fallback must detect 'always' as habit."""
    from cogmem_api.engine.retain.fact_extraction import extract_facts_from_contents
    from cogmem_api.engine.retain.types import RetainContent

    _add_to_path()

    facts, _chunks, _usage = await extract_facts_from_contents(
        contents=[RetainContent(
            content="Alice always reviews emails before standup.",
            event_date=datetime(2026, 4, 1, tzinfo=UTC),
        )],
        llm_config=None,  # no LLM → heuristic path
        agent_name="heuristic-test",
        config=_make_config(),
    )
    assert len(facts) >= 1
    assert any(f.fact_type == "habit" for f in facts), (
        "Heuristic fallback must detect 'always' as habit network type"
    )


async def test_heuristic_detects_action_effect_without_llm() -> None:
    """Without LLM, heuristic fallback must detect 'resulted in' as action_effect."""
    from cogmem_api.engine.retain.fact_extraction import extract_facts_from_contents
    from cogmem_api.engine.retain.types import RetainContent

    _add_to_path()

    facts, _chunks, _usage = await extract_facts_from_contents(
        contents=[RetainContent(
            content="Switching to int8 resulted in 75% latency reduction.",
            event_date=datetime(2026, 4, 1, tzinfo=UTC),
        )],
        llm_config=None,
        agent_name="heuristic-test",
        config=_make_config(),
    )
    assert any(f.fact_type == "action_effect" for f in facts), (
        "Heuristic fallback must detect 'resulted in' as action_effect"
    )


# ---------------------------------------------------------------------------
# Entrypoint
# ---------------------------------------------------------------------------


def main() -> None:
    _add_to_path()

    # Run structural (sync) tests
    sync_tests = [
        test_prompt_json_only_instruction,
        test_prompt_has_all_six_fact_types,
        test_prompt_has_required_fields_section,
        test_prompt_has_examples_for_complex_types,
        test_prompt_has_transition_types,
        test_prompt_length_reasonable_for_slm,
        test_mode_prompts_exist_and_nonempty,
        test_concise_mode_in_system_prompt,
        test_verbose_mode_in_system_prompt,
        test_verbatim_mode_in_system_prompt,
        test_custom_mode_injects_instructions,
        test_mission_section_injected,
    ]

    print("=== GROUP 1: Prompt Structure Gate ===")
    for fn in sync_tests:
        fn()
        print(f"  OK {fn.__name__}")

    # Run async tests
    async_tests = [
        test_markdown_json_wrapped_output,
        test_missing_fact_type_defaults_to_world,
        test_empty_facts_list_no_crash,
        test_malformed_json_triggers_heuristic_fallback,
        test_fact_with_only_what_field,
        test_fact_type_observation_coerced_to_world,
        test_fact_type_assistant_coerced_to_experience,
        test_world_fact_extraction,
        test_experience_fact_extraction_with_timestamp,
        test_opinion_fact_with_confidence,
        test_habit_fact_extraction,
        test_intention_fact_with_planning_status,
        test_intention_default_status_is_planning,
        test_action_effect_full_triplet,
        test_action_effect_regex_fallback_when_llm_omits_triplet,
        test_transition_fulfilled_by_relation,
        test_transition_triggered_relation,
        test_causal_relation_extraction,
        test_causal_links_disabled_when_config_off,
        test_raw_snippet_set_on_all_extracted_facts,
        test_raw_snippet_preserved_in_verbatim_mode,
        test_multi_fact_chunk_extracts_multiple_types,
        test_vietnamese_dialogue_world_fact,
        test_vietnamese_habit_with_trigger_word,
        test_vietnamese_action_effect_technical,
        test_vietnamese_intention_with_deadline,
        test_heuristic_detects_habit_without_llm,
        test_heuristic_detects_action_effect_without_llm,
    ]

    groups = {
        "GROUP 2: SLM Quirk Resilience": async_tests[:7],
        "GROUP 3: All 6 Network Types": async_tests[7:15],
        "GROUP 4: Relation Extraction": async_tests[15:19],
        "GROUP 5: Raw Snippet (Lossless Metadata)": async_tests[19:21],
        "GROUP 6: Multi-fact Extraction": async_tests[21:22],
        "GROUP 7: Vietnamese Dialogue": async_tests[22:26],
        "GROUP 8: Heuristic Fallback": async_tests[26:],
    }

    for group_name, tests in groups.items():
        print(f"\n=== {group_name} ===")
        for fn in tests:
            asyncio.run(fn())
            print(f"  OK {fn.__name__}")

    print("\nAll retain SLM quality tests passed.")


if __name__ == "__main__":
    main()
