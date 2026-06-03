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
    _build_derived_temporal_hints,
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
    assert score_enumeration_candidate(
        spec,
        "Dave was restoring a car that was a beat-up mess and wanted it fixed up by the end of next month",
    ) >= 10.0
    assert score_enumeration_candidate(
        spec,
        "Dave works on cars as a mechanic and has helped a neighbor with repairs ever since childhood",
    ) == 0.0
    print("[ok] duration supplements recover controlled Ford/Mustang project-start facts")


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


def test_derived_temporal_hint_city_before_travel() -> None:
    evidence = [
        {
            "text": "John took a trip to Chicago and enjoyed exploring the city",
            "document_id": "D6",
            "raw_snippet": "[john]: I traveled to Chicago and explored the city.",
        },
        {
            "text": "John has a basketball game in Seattle next month | Seattle is one of his favorite cities",
            "document_id": "D3",
            "raw_snippet": "[john]: Seattle is one of my favorite cities.",
        },
    ]
    hints = _build_derived_temporal_hints(
        "Which city was John in before traveling to Chicago?",
        evidence,
        {"D3": "2023-07-16", "D6": "2023-08-11"},
    )
    assert "DERIVED TEMPORAL HINTS" in hints
    assert "Answer hint: Seattle" in hints
    assert "[2]/D3 2023-07-16" in hints
    assert "[1]/D6 2023-08-11" in hints
    print("[ok] derived city-before-travel hint selects Seattle before Chicago")


def test_derived_temporal_hint_city_negative_controls() -> None:
    evidence = [
        {
            "text": "John took a trip to Chicago and enjoyed exploring the city",
            "document_id": "D6",
            "raw_snippet": "[john]: I traveled to Chicago and explored the city.",
        },
        {
            "text": "John has a basketball game in Seattle next month | Seattle is one of his favorite cities",
            "document_id": "D3",
            "raw_snippet": "[john]: Seattle is one of my favorite cities.",
        },
        {
            "text": "John visited Boston and liked walking around the city",
            "document_id": "D2",
            "raw_snippet": "[john]: I visited Boston last month.",
        },
    ]
    assert _build_derived_temporal_hints(
        "Which city was John in before traveling to Chicago?",
        evidence[:2],
        None,
    ) == ""
    assert _build_derived_temporal_hints(
        "Which city was John in before traveling to Chicago?",
        evidence,
        {"D2": "2023-07-01", "D3": "2023-07-16", "D6": "2023-08-11"},
    ) == ""
    print("[ok] city-before-travel hints stay silent without dates or unique city")


def test_derived_temporal_hint_workshop_duration_ignores_selection_date() -> None:
    evidence = [
        {
            "text": "Dave was picked for a car mod workshop to learn car modification skills",
            "document_id": "D13",
            "raw_snippet": "[dave]: I was selected for a car mod workshop.",
        },
        {
            "text": "Dave visited a car workshop in San Francisco to learn about car restoration techniques",
            "document_id": "D14",
            "raw_snippet": "[dave]: I got to go to a car workshop in San Francisco!",
        },
        {
            "text": "Dave returned from San Francisco with knowledge about car modification",
            "document_id": "D17",
            "raw_snippet": "[dave]: I came back from San Francisco yesterday.",
        },
    ]
    hints = _build_derived_temporal_hints(
        "How long was the car modification workshop in San Francisco?",
        evidence,
        {"D13": "2023-08-11", "D14": "2023-08-14", "D17": "2023-09-02"},
    )
    assert "Answer hint: about two weeks" in hints
    assert "[2]/D14 2023-08-14" in hints
    assert "[3]/D17 2023-09-01" in hints
    assert "[1]/D13" not in hints
    print("[ok] workshop hint uses attended/returned dates and ignores selected date")


def test_derived_temporal_hint_project_duration() -> None:
    evidence = [
        {
            "text": "Dave was restoring a car that was a beat-up mess and wanted it fixed up by the end of next month",
            "document_id": "D14",
            "raw_snippet": "[dave]: The car project is going great.",
        },
        {
            "text": "Dave's Ford Mustang restoration project finally came back to life",
            "document_id": "D21",
            "raw_snippet": "[dave]: The Ford Mustang from the junkyard finally came back to life.",
        },
    ]
    hints = _build_derived_temporal_hints(
        "How long did Dave's work on the Ford Mustang take?",
        evidence,
        {"D14": "2023-08-14", "D21": "2023-10-04"},
    )
    assert "roughly seven weeks / nearly two months" in hints
    assert "Answer hint: nearly two months" in hints
    assert "[1]/D14 2023-08-14" in hints
    assert "[2]/D21 2023-10-04" in hints
    print("[ok] project hint bridges D14 restoration start to D21 Ford Mustang")


def test_derived_temporal_hint_project_negative_control() -> None:
    evidence = [
        {
            "text": "Calvin was restoring a car that was a beat-up mess",
            "document_id": "D14",
            "raw_snippet": "[calvin]: The car project is going great.",
        },
        {
            "text": "Dave's Ford Mustang restoration project finally came back to life",
            "document_id": "D21",
            "raw_snippet": "[dave]: The Ford Mustang finally came back to life.",
        },
    ]
    hints = _build_derived_temporal_hints(
        "How long did Dave's work on the Ford Mustang take?",
        evidence,
        {"D14": "2023-08-14", "D21": "2023-10-04"},
    )
    assert hints == ""
    print("[ok] project hint requires same-subject project overlap")


def test_prompt_inserts_derived_temporal_hints_before_instructions() -> None:
    evidence = [
        {
            "text": "John took a trip to Chicago and enjoyed exploring the city",
            "document_id": "D6",
            "raw_snippet": "[john]: I traveled to Chicago.",
        },
        {
            "text": "John has a basketball game in Seattle next month | Seattle is one of his favorite cities",
            "document_id": "D3",
            "raw_snippet": "[john]: Seattle is one of my favorite cities.",
        },
    ]
    prompt = build_generation_prompt_v4_evidence_guard(
        "Which city was John in before traveling to Chicago?",
        evidence,
        question_date="2026-06-02",
        session_date_map={"D3": "2023-07-16", "D6": "2023-08-11"},
    )
    assert "DERIVED TEMPORAL HINTS" in prompt
    assert "Answer hint: Seattle" in prompt
    assert prompt.index("DERIVED TEMPORAL HINTS") < prompt.index("Instructions:")
    print("[ok] prompt inserts derived temporal hints before instructions")


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
    test_derived_temporal_hint_city_before_travel()
    test_derived_temporal_hint_city_negative_controls()
    test_derived_temporal_hint_workshop_duration_ignores_selection_date()
    test_derived_temporal_hint_project_duration()
    test_derived_temporal_hint_project_negative_control()
    test_prompt_inserts_derived_temporal_hints_before_instructions()
    test_v4_prompt_contains_evidence_guard_rules_and_dispatch()
    print("\nS35-T8G PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
