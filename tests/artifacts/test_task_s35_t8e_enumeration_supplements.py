"""S35-T8E artifact: enumeration recall supplements + prompt guard.

Run: uv run python tests/artifacts/test_task_s35_t8e_enumeration_supplements.py
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
    merge_enumeration_supplements,
    score_enumeration_candidate,
)
from cogmem_api.prompts.eval.generate import (
    build_generation_prompt_v3_temporal,
    build_generation_prompt_v3_temporal_list,
)


def test_camping_location_supplement_scores_missing_place() -> None:
    spec = build_enumeration_query_spec("Where has Melanie camped?")
    assert spec is not None
    assert spec.mode == "camping_places"
    assert score_enumeration_candidate(spec, "Melanie took her family camping in the mountains last week") >= 5.0
    assert score_enumeration_candidate(spec, "Melanie loves camping trips with her family") == 0.0
    print("[ok] camping supplements prefer concrete camp locations")


def test_visited_location_supplement_rejects_wishlist_noise() -> None:
    spec = build_enumeration_query_spec("Which geographical locations has Tim been to?")
    assert spec is not None
    assert spec.mode == "visited_places"
    assert score_enumeration_candidate(spec, "Tim had a nice chat with a Harry Potter fan in California") >= 5.0
    assert score_enumeration_candidate(spec, "tim visited a Harry Potter-themed place in London a few years ago") >= 5.0
    assert score_enumeration_candidate(spec, "Tim has Italy on his list of places to visit") == 0.0
    print("[ok] visited-place supplements reject wishlist/planning facts")


def test_mentioned_city_supplement_scores_nyc_for_subject() -> None:
    spec = build_enumeration_query_spec("Which US cities does John mention visiting to Tim?")
    assert spec is not None
    assert spec.mode == "mentioned_places"
    assert score_enumeration_candidate(spec, "John had trouble figuring out the subway in NYC but someone helped him") >= 5.0
    assert score_enumeration_candidate(spec, "Tim has Italy on his list of places to visit") == 0.0
    print("[ok] mentioned-place supplements keep subject-specific city evidence")


def test_merge_supplements_preserves_top_k_window() -> None:
    primary = [{"id": f"p{i}", "text": f"primary {i}"} for i in range(5)]
    supplements = [{"id": "s1", "text": "supplement 1"}, {"id": "s2", "text": "supplement 2"}]
    merged = merge_enumeration_supplements(primary, supplements, top_k=5)
    assert len(merged) == 5
    assert [item["id"] for item in merged] == ["p0", "p1", "p2", "s1", "s2"]
    print("[ok] supplements replace tail items without increasing top-k")


def test_prompt_variant_keeps_t8b_isolated() -> None:
    evidence = [{"text": "John visited Chicago", "document_id": "D1"}]
    v3 = build_generation_prompt_v3_temporal("Where was John before Chicago?", evidence)
    v3_list = build_generation_prompt_v3_temporal_list("Which cities did John visit?", evidence)
    assert "before a Chicago trip" in v3
    assert "scan ALL numbered MEMORIES" not in v3
    assert "before a Chicago trip" in v3_list
    assert "scan ALL numbered MEMORIES" in v3_list

    os.environ["COGMEM_API_GENERATE_PROMPT_VARIANT"] = "v3_temporal_list"
    try:
        dispatched = eval_helpers.build_generation_prompt("Which cities did John visit?", evidence)
        assert "scan ALL numbered MEMORIES" in dispatched
    finally:
        os.environ.pop("COGMEM_API_GENERATE_PROMPT_VARIANT", None)
    print("[ok] v3_temporal_list dispatch is separate from T8B")


def main() -> int:
    test_camping_location_supplement_scores_missing_place()
    test_visited_location_supplement_rejects_wishlist_noise()
    test_mentioned_city_supplement_scores_nyc_for_subject()
    test_merge_supplements_preserves_top_k_window()
    test_prompt_variant_keeps_t8b_isolated()
    print("\nS35-T8E PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
