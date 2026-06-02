"""S35-T8G artifact: generalized supplements + v4 evidence guard prompt.

Run: uv run python tests/artifacts/test_task_s35_t8g_evidence_guard.py
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from cogmem_api.engine import eval_helpers
from cogmem_api.engine.enumeration_supplements import (
    build_enumeration_query_spec,
    score_enumeration_candidate,
)
from cogmem_api.prompts.eval.generate import (
    build_generation_prompt_v4_evidence_guard,
    select_query_relevant_snippet,
)


def test_band_supplement_scores_fireworks_for_subject() -> None:
    spec = build_enumeration_query_spec("Which bands has Dave enjoyed listening to?")
    assert spec is not None
    assert spec.mode == "bands"

    score = score_enumeration_candidate(
        spec,
        "Dave experienced The Fireworks headlining a festival",
        "[dave]: The Fireworks headlined the festival.",
    )
    assert score >= 7.0
    assert score_enumeration_candidate(
        spec,
        "Dave joined a rock band that he has been a fan of for ages.",
    ) == 0.0
    assert score_enumeration_candidate(
        spec,
        "Calvin experienced The Fireworks headlining a festival",
        "[calvin]: The Fireworks headlined the festival.",
    ) == 0.0
    print("[ok] band supplements recover Fireworks while preserving subject guard")


def test_basketball_supplement_prefers_training_addons_over_generic_basketball() -> None:
    spec = build_enumeration_query_spec("What does John do to supplement his basketball training?")
    assert spec is not None
    assert spec.mode == "sports_exercises"

    assert score_enumeration_candidate(spec, "John does yoga to supplement basketball training") >= 7.0
    assert score_enumeration_candidate(spec, "John added strength training for basketball") >= 7.0
    assert score_enumeration_candidate(spec, "John started surfing five years ago") == 0.0
    assert score_enumeration_candidate(spec, "John thinks basketball training is important") == 0.0
    assert score_enumeration_candidate(spec, "John's team dinners strengthen unity away from practice") == 0.0
    assert (
        score_enumeration_candidate(
            spec,
            "Tim and John both enjoy fantasy books and movies",
            "John is trying yoga to improve strength and flexibility.",
        )
        == 0.0
    )
    print("[ok] basketball supplement scoring rejects generic basketball facts")


def test_generic_supplements_do_not_bleed_from_raw_snippet() -> None:
    spec = build_enumeration_query_spec("Which bands has Dave enjoyed listening to?")
    assert spec is not None

    assert (
        score_enumeration_candidate(
            spec,
            "Dave started a blog about car mods to share his passion with others.",
            "Dave experienced The Fireworks headlining a festival.",
        )
        == 0.0
    )
    print("[ok] generic supplement scoring requires category cues in fact text")


def test_collectibles_have_explicit_supplement_mode() -> None:
    spec = build_enumeration_query_spec("Which collectibles does Dave collect?")
    assert spec is not None
    assert spec.mode == "collectibles"
    assert score_enumeration_candidate(spec, "Dave collects vintage baseball cards and jerseys") >= 7.0
    assert score_enumeration_candidate(spec, "Calvin collects vintage baseball cards and jerseys") == 0.0
    print("[ok] collectibles queries use an explicit supplement mode")


def test_query_relevant_snippet_prefers_duration_entity_window() -> None:
    irrelevant_prefix = "Dave talked about groceries and parking logistics. " * 10
    raw = (
        "[dave]: "
        + irrelevant_prefix
        + "The Ford Mustang restoration took nearly two months before Dave finished it."
    )
    snippet = select_query_relevant_snippet(
        "How long did Dave's work on the Ford Mustang take?",
        raw,
        fact_text="Dave worked on the Ford Mustang restoration",
    )
    assert "nearly two months" in snippet
    assert not snippet.startswith("[dave]: Dave talked about groceries")
    print("[ok] snippet window exposes duration evidence instead of irrelevant prefix")


def test_duration_supplement_prefers_stated_duration_for_named_target() -> None:
    spec = build_enumeration_query_spec("How long did Dave's work on the Ford Mustang take?")
    assert spec is not None
    assert spec.mode == "duration"
    assert score_enumeration_candidate(
        spec,
        "Dave restored a Ford Mustang from a junkyard",
        "[dave]: The Ford Mustang restoration took nearly two months before I finished it.",
    ) >= 10.0
    assert score_enumeration_candidate(
        spec,
        "Dave worked on cars with his dad as a kid, spending one summer restoring an old car together",
    ) == 0.0
    print("[ok] duration supplements require explicit duration plus target terms")


def test_temporal_city_supplement_scores_non_anchor_city() -> None:
    spec = build_enumeration_query_spec("Which city was John in before traveling to Chicago?")
    assert spec is not None
    assert spec.mode == "temporal_city"
    assert score_enumeration_candidate(
        spec,
        "John has a basketball game in Seattle next month | one of his favorite cities",
    ) >= 6.0
    assert score_enumeration_candidate(spec, "John took a trip to Chicago and liked it") == 0.0
    print("[ok] temporal city supplements can recover non-anchor city evidence")


def test_v4_prompt_contains_evidence_guard_rules_and_dispatch() -> None:
    evidence = [
        {
            "text": "Dave worked on the Ford Mustang restoration",
            "document_id": "D1",
            "raw_snippet": (
                "[dave]: We discussed unrelated errands. "
                "The Ford Mustang restoration took nearly two months before I finished it."
            ),
        }
    ]
    prompt = build_generation_prompt_v4_evidence_guard(
        "How long did Dave's work on the Ford Mustang take?",
        evidence,
        question_date="2026-06-02",
        session_date_map={"D1": "2024-05-01"},
    )
    assert "scan ALL numbered MEMORIES" in prompt
    assert "queried subject/object/action" in prompt
    assert "do NOT continue by explaining the adjacent pair" in prompt
    assert "explicit duration phrases" in prompt
    assert "Session-date ordering is valid evidence" in prompt
    assert "City-before-travel pattern" in prompt
    assert "Attended-workshop/returned-from-city" in prompt
    assert "compute the gap between relevant" in prompt
    assert "coarse rounded" in prompt
    assert "nearly two months" in prompt

    os.environ["COGMEM_API_GENERATE_PROMPT_VARIANT"] = "v4_evidence_guard"
    try:
        dispatched = eval_helpers.build_generation_prompt(
            "Why did Dave sell the Mustang?",
            evidence,
            question_date="2026-06-02",
            session_date_map={"D1": "2024-05-01"},
        )
        assert "queried subject/object/action" in dispatched
        assert "query-relevant source line" in dispatched
    finally:
        os.environ.pop("COGMEM_API_GENERATE_PROMPT_VARIANT", None)
    print("[ok] v4 evidence guard prompt and env dispatch are wired")


def main() -> int:
    test_band_supplement_scores_fireworks_for_subject()
    test_basketball_supplement_prefers_training_addons_over_generic_basketball()
    test_generic_supplements_do_not_bleed_from_raw_snippet()
    test_collectibles_have_explicit_supplement_mode()
    test_query_relevant_snippet_prefers_duration_entity_window()
    test_duration_supplement_prefers_stated_duration_for_named_target()
    test_temporal_city_supplement_scores_non_anchor_city()
    test_v4_prompt_contains_evidence_guard_rules_and_dispatch()
    print("\nS35-T8G PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
