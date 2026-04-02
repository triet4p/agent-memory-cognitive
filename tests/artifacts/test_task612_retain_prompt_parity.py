from __future__ import annotations

import asyncio
import sys
from datetime import UTC, datetime
from pathlib import Path
from types import SimpleNamespace


class FakeLLMConfig:
    def __init__(self) -> None:
        self.calls: list[dict[str, object]] = []

    async def call(self, messages, **kwargs):
        self.calls.append({"messages": messages, "kwargs": kwargs})
        system_prompt = messages[0]["content"]

        from cogmem_api.engine.response_models import TokenUsage

        usage = TokenUsage(input_tokens=11, output_tokens=7, total_tokens=18)

        if "Mode: verbatim" in system_prompt:
            return {
                "facts": [
                    {
                        "when": "2026-04-01",
                        "where": "Ha Noi",
                        "who": "Alice",
                        "fact_kind": "conversation",
                        "fact_type": "world",
                        "entities": [{"text": "Alice"}, "Rust"],
                    }
                ]
            }, usage

        if "Mode: verbose" in system_prompt:
            return {
                "facts": [
                    {
                        "what": "Alice planned a Rust migration and documented latency constraints in detail",
                        "when": "2026-04-01",
                        "where": "Ha Noi",
                        "who": "Alice",
                        "why": "She needed predictable inference latency for production",
                        "fact_kind": "event",
                        "fact_type": "world",
                        "occurred_start": "2026-04-01T08:00:00+00:00",
                        "occurred_end": "2026-04-01T08:00:00+00:00",
                        "entities": [{"text": "Alice"}, {"text": "Rust"}],
                    }
                ]
            }, usage

        if "Mode: custom" in system_prompt:
            return {
                "facts": [
                    {
                        "what": "Custom mode captured action-effect details for migration",
                        "when": "N/A",
                        "where": "N/A",
                        "who": "Alice",
                        "why": "custom-mode",
                        "fact_kind": "conversation",
                        "fact_type": "action_effect",
                        "entities": [{"text": "Alice"}],
                        "precondition": "Latency over 100ms",
                        "action": "Switch to int8",
                        "outcome": "Latency dropped to 45ms",
                        "confidence": 0.92,
                        "devalue_sensitive": True,
                    }
                ]
            }, usage

        # concise
        return {
            "facts": [
                {
                    "what": "When latency exceeded 100ms, Alice switched to int8 and latency dropped",
                    "when": "2026-04-01",
                    "where": "N/A",
                    "who": "Alice",
                    "why": "To stabilize inference",
                    "fact_kind": "event",
                    "fact_type": "action_effect",
                    "occurred_start": "2026-04-01T09:00:00+00:00",
                    "occurred_end": "2026-04-01T09:00:00+00:00",
                    "entities": [{"text": "Alice"}, "quantization"],
                    "causal_relations": [{"target_index": 0, "relation_type": "caused_by", "strength": 0.8}],
                    "action_effect_relations": [{"target_index": 0, "relation_type": "a_o_causal", "strength": 0.95}],
                    "transition_relations": [{"target_index": 1, "transition_type": "triggered", "strength": 0.7}],
                    "precondition": "Embedding latency > 100ms",
                    "action": "Switch to int8 quantization",
                    "outcome": "Latency reduced to 45ms",
                    "confidence": 0.95,
                    "devalue_sensitive": True,
                    "intention_status": "planning",
                }
            ]
        }, usage


def assert_required_files(repo_root: Path) -> None:
    required = [
        repo_root / "cogmem_api" / "engine" / "retain" / "fact_extraction.py",
        repo_root / "cogmem_api" / "engine" / "llm_wrapper.py",
        repo_root / "logs" / "task_612_summary.md",
    ]
    missing = [str(path.relative_to(repo_root)) for path in required if not path.exists()]
    assert not missing, f"Missing B2 files: {missing}"


def assert_isolation(repo_root: Path) -> None:
    targets = [
        repo_root / "cogmem_api" / "engine" / "retain" / "fact_extraction.py",
        repo_root / "cogmem_api" / "engine" / "llm_wrapper.py",
    ]

    violations: list[str] = []
    for path in targets:
        text = path.read_text(encoding="utf-8")
        if "hindsight_api" in text:
            violations.append(str(path.relative_to(repo_root)))
    assert not violations, f"Isolation violation detected: {violations}"


async def run_behavior_test(repo_root: Path) -> None:
    repo_root_str = str(repo_root)
    if repo_root_str not in sys.path:
        sys.path.insert(0, repo_root_str)

    from cogmem_api.engine.retain.fact_extraction import extract_facts_from_contents
    from cogmem_api.engine.retain.types import RetainContent

    llm = FakeLLMConfig()
    base_content = "When latency exceeded 100ms, Alice switched to int8 and latency dropped to 45ms."
    event_date = datetime(2026, 4, 1, 9, 0, tzinfo=UTC)

    # concise: verifies relation parsing and action-effect metadata mapping.
    concise_config = SimpleNamespace(
        retain_extraction_mode="concise",
        retain_max_completion_tokens=4096,
        retain_chunk_size=3000,
        retain_custom_instructions=None,
        retain_mission=None,
    )
    concise_facts, concise_chunks, concise_usage = await extract_facts_from_contents(
        contents=[RetainContent(content=base_content, event_date=event_date, context="retain")],
        llm_config=llm,
        agent_name="b2-test",
        config=concise_config,
    )

    assert len(concise_facts) == 1
    assert len(concise_chunks) == 1
    assert concise_usage.total_tokens > 0

    fact = concise_facts[0]
    assert fact.fact_type == "action_effect"
    assert fact.metadata.get("precondition") == "Embedding latency > 100ms"
    assert fact.metadata.get("action") == "Switch to int8 quantization"
    assert fact.metadata.get("outcome") == "Latency reduced to 45ms"
    assert fact.metadata.get("intention_status") == "planning"
    assert len(fact.causal_relations) == 1
    assert len(fact.action_effect_relations) == 1
    assert len(fact.transition_relations) == 1

    # custom: verifies prompt parity includes custom instruction text.
    custom_instruction = "CUSTOM_RULE_B2: prioritize migration constraints"
    custom_config = SimpleNamespace(
        retain_extraction_mode="custom",
        retain_max_completion_tokens=4096,
        retain_chunk_size=3000,
        retain_custom_instructions=custom_instruction,
        retain_mission="Retain only migration-critical facts",
    )
    custom_facts, _custom_chunks, _custom_usage = await extract_facts_from_contents(
        contents=[RetainContent(content=base_content, event_date=event_date, context="retain")],
        llm_config=llm,
        agent_name="b2-test",
        config=custom_config,
    )

    assert len(custom_facts) == 1
    last_system_prompt = str(llm.calls[-1]["messages"][0]["content"])
    assert "CUSTOM_RULE_B2" in last_system_prompt

    # verbatim: verifies raw chunk text is preserved as fact_text.
    verbatim_config = SimpleNamespace(
        retain_extraction_mode="verbatim",
        retain_max_completion_tokens=4096,
        retain_chunk_size=3000,
        retain_custom_instructions=None,
        retain_mission=None,
    )
    verbatim_facts, _verbatim_chunks, _verbatim_usage = await extract_facts_from_contents(
        contents=[RetainContent(content=base_content, event_date=event_date, context="retain")],
        llm_config=llm,
        agent_name="b2-test",
        config=verbatim_config,
    )

    assert len(verbatim_facts) == 1
    assert verbatim_facts[0].fact_text == base_content

    # verbose: verifies mode can extract richer fact text while preserving event timestamps.
    verbose_config = SimpleNamespace(
        retain_extraction_mode="verbose",
        retain_max_completion_tokens=4096,
        retain_chunk_size=3000,
        retain_custom_instructions=None,
        retain_mission=None,
    )
    verbose_facts, _verbose_chunks, _verbose_usage = await extract_facts_from_contents(
        contents=[RetainContent(content=base_content, event_date=event_date, context="retain")],
        llm_config=llm,
        agent_name="b2-test",
        config=verbose_config,
    )

    assert len(verbose_facts) == 1
    assert verbose_facts[0].occurred_start is not None
    assert "Latency" in verbose_facts[0].fact_text or "latency" in verbose_facts[0].fact_text


def main() -> None:
    repo_root = Path(__file__).resolve().parents[2]
    assert_required_files(repo_root)
    assert_isolation(repo_root)
    asyncio.run(run_behavior_test(repo_root))
    print("Task 612 retain prompt parity check passed.")


if __name__ == "__main__":
    main()
