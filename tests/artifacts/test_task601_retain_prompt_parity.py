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
        system_prompt = str(messages[0]["content"])

        from cogmem_api.engine.response_models import TokenUsage

        usage = TokenUsage(input_tokens=20, output_tokens=15, total_tokens=35)

        if "Mode: custom" in system_prompt:
            return {
                "facts": [
                    {
                        "what": "Alice used int8 to reduce inference latency in production",
                        "when": "2026-04-04",
                        "where": "N/A",
                        "who": "Alice",
                        "why": "Optimization for stable tail latency",
                        "fact_kind": "event",
                        "fact_type": "action_effect",
                        "entities": [{"text": "Alice"}, "inference"],
                        "precondition": "Latency > 100ms",
                        "action": "Switch to int8 quantization",
                        "outcome": "Latency dropped to 45ms",
                        "confidence": 0.91,
                        "devalue_sensitive": True,
                        "transition_relations": [
                            {"target_index": 0, "transition_type": "triggered", "strength": 0.7}
                        ],
                    }
                ]
            }, usage

        if "Mode: verbatim" in system_prompt:
            return {
                "facts": [
                    {
                        "when": "2026-04-04",
                        "where": "Ha Noi",
                        "who": "Alice",
                        "fact_kind": "conversation",
                        "fact_type": "world",
                        "entities": [{"text": "Alice"}],
                    }
                ]
            }, usage

        if "Mode: verbose" in system_prompt:
            return {
                "facts": [
                    {
                        "what": "Alice repeatedly documents every production regression before rollout",
                        "when": "2026-04-04",
                        "where": "Ha Noi",
                        "who": "Alice",
                        "why": "She wants safer deploy decisions",
                        "fact_kind": "conversation",
                        "fact_type": "habit",
                        "entities": [{"text": "Alice"}, {"text": "regression"}],
                    }
                ]
            }, usage

        # concise (default)
        return {
            "facts": [
                {
                    "what": "Alice asked the assistant to analyze latency spikes during deployment",
                    "when": "2026-04-04",
                    "where": "N/A",
                    "who": "Alice",
                    "why": "Need to stabilize production",
                    "fact_kind": "event",
                    "fact_type": "assistant",
                    "occurred_start": "2026-04-04T10:00:00+00:00",
                    "occurred_end": "2026-04-04T10:00:00+00:00",
                    "entities": [{"text": "Alice"}],
                    "causal_relations": [{"target_index": 0, "relation_type": "caused_by", "strength": 0.8}],
                    "transition_relations": [{"target_index": 1, "transition_type": "enabled_by", "strength": 0.6}],
                }
            ]
        }, usage


def _build_config(mode: str, **overrides):
    payload = {
        "retain_extraction_mode": mode,
        "retain_mission": "Retain durable user memory relevant for future assistance",
        "retain_custom_instructions": "CUSTOM_RULE_601: prioritize long-term engineering constraints",
        "retain_max_completion_tokens": 64000,
        "retain_chunk_size": 3000,
        "retain_extract_causal_links": True,
    }
    payload.update(overrides)
    return SimpleNamespace(**payload)


def assert_required_files(repo_root: Path) -> None:
    required = [
        repo_root / "cogmem_api" / "engine" / "retain" / "fact_extraction.py",
        repo_root / "cogmem_api" / "engine" / "retain" / "orchestrator.py",
        repo_root / "cogmem_api" / "engine" / "llm_wrapper.py",
        repo_root / "tests" / "artifacts" / "test_task601_retain_prompt_parity.py",
        repo_root / "logs" / "task_601_summary.md",
    ]
    missing = [str(path.relative_to(repo_root)) for path in required if not path.exists()]
    assert not missing, f"Missing T6.1 files: {missing}"


def assert_isolation(repo_root: Path) -> None:
    targets = [
        repo_root / "cogmem_api" / "engine" / "retain" / "fact_extraction.py",
        repo_root / "cogmem_api" / "engine" / "retain" / "orchestrator.py",
        repo_root / "cogmem_api" / "engine" / "llm_wrapper.py",
    ]

    violations: list[str] = []
    for path in targets:
        text = path.read_text(encoding="utf-8")
        if "hindsight_api" in text:
            violations.append(str(path.relative_to(repo_root)))

    assert not violations, f"Isolation violation detected: {violations}"


def assert_drift_contract(repo_root: Path) -> None:
    extraction_source = (repo_root / "cogmem_api" / "engine" / "retain" / "fact_extraction.py").read_text(
        encoding="utf-8"
    )

    required_markers = [
        "_CONCISE_MODE",
        "_CUSTOM_MODE",
        "_VERBATIM_MODE",
        "_VERBOSE_MODE",
        "retain_mission",
        "retain_custom_instructions",
        "retain_extract_causal_links",
    ]
    missing = [marker for marker in required_markers if marker not in extraction_source]
    assert not missing, f"Prompt/cfg parity markers missing in fact_extraction.py: {missing}"


async def run_behavior_test(repo_root: Path) -> None:
    repo_root_str = str(repo_root)
    if repo_root_str not in sys.path:
        sys.path.insert(0, repo_root_str)

    from cogmem_api.engine.retain.fact_extraction import extract_facts_from_contents
    from cogmem_api.engine.retain.types import RetainContent

    llm = FakeLLMConfig()
    base_content = "When deployment latency went above 100ms, Alice switched to int8 and got 45ms latency."
    event_date = datetime(2026, 4, 4, 10, 0, tzinfo=UTC)

    # concise with causal links enabled
    concise_cfg = _build_config("concise", retain_extract_causal_links=True)
    concise_facts, concise_chunks, concise_usage = await extract_facts_from_contents(
        contents=[RetainContent(content=base_content, event_date=event_date, context="retain")],
        llm_config=llm,
        agent_name="t601",
        config=concise_cfg,
    )
    assert len(concise_facts) == 1
    assert len(concise_chunks) == 1
    assert concise_usage.total_tokens > 0
    assert concise_facts[0].fact_type == "experience"  # assistant -> experience mapping
    assert len(concise_facts[0].causal_relations) == 1
    assert len(concise_facts[0].transition_relations) == 1

    # concise with causal links disabled
    concise_no_causal_cfg = _build_config("concise", retain_extract_causal_links=False)
    no_causal_facts, _no_causal_chunks, _no_causal_usage = await extract_facts_from_contents(
        contents=[RetainContent(content=base_content, event_date=event_date, context="retain")],
        llm_config=llm,
        agent_name="t601",
        config=concise_no_causal_cfg,
    )
    assert len(no_causal_facts) == 1
    assert len(no_causal_facts[0].causal_relations) == 0

    # custom
    custom_cfg = _build_config("custom")
    custom_facts, _custom_chunks, _custom_usage = await extract_facts_from_contents(
        contents=[RetainContent(content=base_content, event_date=event_date, context="retain")],
        llm_config=llm,
        agent_name="t601",
        config=custom_cfg,
    )
    assert len(custom_facts) == 1
    assert custom_facts[0].fact_type == "action_effect"
    assert custom_facts[0].metadata.get("precondition") == "Latency > 100ms"
    assert custom_facts[0].metadata.get("action") == "Switch to int8 quantization"
    assert custom_facts[0].metadata.get("outcome") == "Latency dropped to 45ms"
    custom_prompt = str(llm.calls[-1]["messages"][0]["content"])
    assert "CUSTOM_RULE_601" in custom_prompt

    # verbatim
    verbatim_cfg = _build_config("verbatim")
    verbatim_facts, _verbatim_chunks, _verbatim_usage = await extract_facts_from_contents(
        contents=[RetainContent(content=base_content, event_date=event_date, context="retain")],
        llm_config=llm,
        agent_name="t601",
        config=verbatim_cfg,
    )
    assert len(verbatim_facts) == 1
    assert verbatim_facts[0].fact_text == base_content

    # verbose
    verbose_cfg = _build_config("verbose")
    verbose_facts, _verbose_chunks, _verbose_usage = await extract_facts_from_contents(
        contents=[RetainContent(content=base_content, event_date=event_date, context="retain")],
        llm_config=llm,
        agent_name="t601",
        config=verbose_cfg,
    )
    assert len(verbose_facts) == 1
    assert verbose_facts[0].fact_type == "habit"

    # Ensure all four mode prompts were used.
    system_prompts = [str(call["messages"][0]["content"]) for call in llm.calls]
    assert any("Mode: concise" in prompt for prompt in system_prompts)
    assert any("Mode: custom" in prompt for prompt in system_prompts)
    assert any("Mode: verbatim" in prompt for prompt in system_prompts)
    assert any("Mode: verbose" in prompt for prompt in system_prompts)


def main() -> None:
    repo_root = Path(__file__).resolve().parents[2]
    assert_required_files(repo_root)
    assert_drift_contract(repo_root)
    assert_isolation(repo_root)
    asyncio.run(run_behavior_test(repo_root))
    print("Task 601 retain prompt parity check passed.")


if __name__ == "__main__":
    main()
