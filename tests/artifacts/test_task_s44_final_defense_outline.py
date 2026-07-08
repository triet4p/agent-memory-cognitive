from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
OUTLINE = ROOT / "docs" / "slides" / "DATN_Final_Defense_Detailed_Outline.md"


def _read_outline() -> str:
    assert OUTLINE.exists(), f"Missing detailed defense outline: {OUTLINE}"
    text = OUTLINE.read_text(encoding="utf-8")
    assert len(text) > 10_000, "Outline is unexpectedly short"
    return text


def test_outline_has_slide_by_slide_plan() -> None:
    text = _read_outline()
    for slide_no in range(1, 28):
        assert f"### Slide {slide_no}." in text, f"Missing Slide {slide_no}"


def test_outline_documents_visual_sources_and_reuse_strategy() -> None:
    text = _read_outline()
    required_assets = [
        "cogmem_pipeline_overview.png",
        "cogmem_memory_graph.png",
        "manual_evaluation_flow.png",
        "cogmem_bench_intention_graph.png",
        "cogmem_bench_action_effect_graph.png",
        "neg_intention_14_graph.html",
        "agentic_ae_01_http_429_graph.html",
        "neg_intention_14_explanation.md",
        "agentic_ae_01_http_429_explanation.md",
    ]
    for asset in required_assets:
        assert asset in text, f"Missing visual/source asset: {asset}"

    required_phrases = [
        "Reuse directly",
        "Reuse only after crop/annotation",
        "Redraw for slides",
        "do not place the entire graph as the only visual",
    ]
    for phrase in required_phrases:
        assert phrase in text, f"Missing reuse guidance: {phrase}"


def test_outline_documents_slide_copy_style() -> None:
    text = _read_outline()
    required_phrases = [
        "Slide Writing Rules",
        "Prefer short noun phrases over complete sentences.",
        "Full sentences should usually move to speaker notes.",
        "Keep one bullet to one idea",
        "Avoid report-style paragraphs",
        "Keep slide copy phrase-based",
    ]
    for phrase in required_phrases:
        assert phrase in text, f"Missing slide copy guidance: {phrase}"


def test_outline_uses_updated_report_numbers() -> None:
    text = _read_outline()
    required_numbers = [
        "31/35 = 88.6%",
        "30/35 = 85.7%",
        "29/35 = 82.9%",
        "22/35 = 62.9%",
        "119/161 = 73.9%",
        "105/161 = 65.2%",
        "97/161 = 60.2%",
        "0.805",
        "0.762",
        "5/12 clean discriminations",
    ]
    for number in required_numbers:
        assert number in text, f"Missing updated result: {number}"


def test_outline_covers_requested_sections() -> None:
    text = _read_outline()
    required_terms = [
        "Problem: Long Conversations Are Not Just Long Text",
        "Common Approaches and Their Limits",
        "Related Work Landscape",
        "CogMem Pipeline Overview",
        "Four Contributions",
        "Six Typed Memory Networks",
        "Structured Fact + Raw Snippet",
        "Four Recall Channels",
        "RRF + CrossEncoder",
        "Adaptive Query Routing",
        "SUM vs MAX Graph Activation",
        "Cycle Guards",
        "Experiment Overview",
        "LongMemEval",
        "LoCoMo",
        "CogMem Bench",
        "Intention Node",
        "Action-Effect Node",
        "Limitations and Future Work",
    ]
    for term in required_terms:
        assert term in text, f"Missing requested section: {term}"


def test_outline_records_coverage_gate_status() -> None:
    text = _read_outline()
    assert "Coverage gate" in text
    assert "read-only" in text


if __name__ == "__main__":
    test_outline_has_slide_by_slide_plan()
    test_outline_documents_visual_sources_and_reuse_strategy()
    test_outline_documents_slide_copy_style()
    test_outline_uses_updated_report_numbers()
    test_outline_covers_requested_sections()
    test_outline_records_coverage_gate_status()
    print("task_s44_final_defense_outline artifact checks passed")
