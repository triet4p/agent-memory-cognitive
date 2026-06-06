from __future__ import annotations

import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
PLAN = ROOT / "docs" / "slides" / "DATN_Proposal_Copy_revision_plan.md"


def _read_plan() -> str:
    assert PLAN.exists(), f"Missing slide revision plan: {PLAN}"
    return PLAN.read_text(encoding="utf-8")


def test_plan_targets_source_deck_and_defense_timing() -> None:
    text = _read_plan()
    assert "DATN_Proposal - Copy.pptx" in text
    assert "10-15 minute" in text
    assert "15 main slides plus a Q&A slide" in text
    assert "45-60 seconds per slide" in text


def test_plan_covers_full_presentation_story() -> None:
    text = _read_plan().lower()
    required_terms = [
        "problem",
        "solution overview",
        "six memory networks",
        "four channels",
        "sum instead of max",
        "running example",
        "evaluation protocol",
        "longmemeval",
        "locomo",
        "qualitative proof",
        "intention stores unfinished plans",
        "action-effect stores tool outcomes",
        "what was proved",
        "what remains",
    ]
    for term in required_terms:
        assert term in text, f"Missing story element: {term}"


def test_plan_reports_current_verified_results() -> None:
    text = _read_plan()
    required_numbers = [
        "29/35 PASS = 82.9%",
        "26/35 PASS = 74.3%",
        "0.8052",
        "0.7624",
        "119/161 = 73.9%",
        "97/161 = 60.2%",
        "+22",
        "5/12 = 41.7%",
        "37",
        "26",
        "13",
        "12",
    ]
    for number in required_numbers:
        assert number in text, f"Missing current result: {number}"


def test_plan_prioritizes_visuals_and_contribution_proof() -> None:
    text = _read_plan()
    required_assets = [
        "cogmem_pipeline_overview.png",
        "cogmem_memory_graph.png",
        "manual_evaluation_flow.png",
        "neg_intention_14_explanation.md",
        "agentic_ae_01_http_429_explanation.md",
    ]
    for asset in required_assets:
        assert asset in text, f"Missing visual asset: {asset}"
    assert "proof matrix" in text.lower()
    assert "paired-bank" in text.lower()
    assert "Every visual should include text labels" in text


def test_plan_avoids_unexplained_internal_eval_labels() -> None:
    text = _read_plan()
    forbidden_patterns = [
        r"\bE7[A-Z]*\b",
        r"\bT8[A-Z]?\b",
        r"\bc\d{3}\b",
    ]
    for pattern in forbidden_patterns:
        assert not re.search(pattern, text), f"Internal label leaked: {pattern}"


if __name__ == "__main__":
    test_plan_targets_source_deck_and_defense_timing()
    test_plan_covers_full_presentation_story()
    test_plan_reports_current_verified_results()
    test_plan_prioritizes_visuals_and_contribution_proof()
    test_plan_avoids_unexplained_internal_eval_labels()
    print("task_s37_slide_revision_plan artifact checks passed")
