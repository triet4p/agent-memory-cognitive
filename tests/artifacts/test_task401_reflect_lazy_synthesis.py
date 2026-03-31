from __future__ import annotations

import sys
from datetime import UTC, datetime
from pathlib import Path


def assert_required_files(repo_root: Path) -> None:
    required = [
        repo_root / "cogmem_api" / "engine" / "reflect" / "__init__.py",
        repo_root / "cogmem_api" / "engine" / "reflect" / "agent.py",
        repo_root / "cogmem_api" / "engine" / "reflect" / "models.py",
        repo_root / "cogmem_api" / "engine" / "reflect" / "prompts.py",
        repo_root / "cogmem_api" / "engine" / "reflect" / "tools.py",
        repo_root / "logs" / "task_401_summary.md",
    ]
    missing = [str(path.relative_to(repo_root)) for path in required if not path.exists()]
    assert not missing, f"Missing T4.1 files: {missing}"


def assert_isolation(repo_root: Path) -> None:
    scope = [
        repo_root / "cogmem_api" / "engine" / "reflect",
    ]

    violating: list[str] = []
    for root in scope:
        for py_file in root.rglob("*.py"):
            text = py_file.read_text(encoding="utf-8")
            if "hindsight_api" in text:
                violating.append(str(py_file.relative_to(repo_root)))

    assert not violating, f"Found forbidden hindsight imports: {violating}"


def run_lazy_synthesis_behavior() -> None:
    from cogmem_api.engine.reflect import synthesize_lazy_reflect
    from cogmem_api.engine.search.types import MergedCandidate, RetrievalResult

    world = RetrievalResult(
        id="w1",
        text="User moved from VCCorp to DI in April 2024",
        fact_type="world",
        raw_snippet="I left VCCorp and accepted a DI offer with +40% salary.",
        event_date=datetime(2024, 4, 1, tzinfo=UTC),
        similarity=0.88,
    )
    intention = RetrievalResult(
        id="i1",
        text="User plans to learn Rust before Q3",
        fact_type="intention",
        raw_snippet="I want to finish Rust basics before Q3.",
        event_date=datetime(2024, 5, 10, tzinfo=UTC),
        temporal_score=0.81,
    )
    habit = RetrievalResult(
        id="h1",
        text="User checks email before standup",
        fact_type="habit",
        activation=0.74,
    )
    action_effect = MergedCandidate(
        retrieval=RetrievalResult(
            id="ae1",
            text="Filtering by high rating leads to faster delivery",
            fact_type="action_effect",
            raw_snippet="When I filter shops by high ratings, delivery is usually faster.",
            event_date=datetime(2024, 6, 3, tzinfo=UTC),
        ),
        rrf_score=0.95,
    )
    duplicate_lower_score = {
        "id": "w1",
        "text": "Duplicate world fact should be dropped",
        "fact_type": "world",
        "score": 0.1,
    }
    unsupported = {
        "id": "obs1",
        "text": "Legacy observation should be ignored in CogMem reflect",
        "fact_type": "observation",
        "score": 1.0,
    }

    result = synthesize_lazy_reflect(
        question="What do we know about plans and behavior?",
        retrieved_items=[world, intention, habit, action_effect, duplicate_lower_score, unsupported],
        include_prompt=True,
    )

    assert result.evidence_count == 4, "Expected 4 supported evidence items after dedupe/filtering"
    assert result.used_memory_ids.count("w1") == 1, "Duplicate memory IDs should be deduplicated"
    assert "observation" not in result.networks_covered, "Observation network should remain excluded"
    assert set(result.networks_covered) == {"world", "intention", "habit", "action_effect"}

    answer_lower = result.answer.lower()
    assert "memory-grounded answer" in answer_lower
    assert "rust" in answer_lower
    assert "email before standup" in answer_lower
    assert "high rating" in answer_lower

    assert result.prompt is not None
    assert "raw_snippet" in result.prompt
    assert "+40% salary" in result.prompt


def main() -> None:
    repo_root = Path(__file__).resolve().parents[2]
    repo_root_str = str(repo_root)
    if repo_root_str not in sys.path:
        sys.path.insert(0, repo_root_str)

    assert_required_files(repo_root)
    assert_isolation(repo_root)
    run_lazy_synthesis_behavior()
    print("Task 401 reflect lazy synthesis check passed.")


if __name__ == "__main__":
    main()
