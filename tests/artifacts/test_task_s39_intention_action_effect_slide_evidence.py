from __future__ import annotations

import re
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
PPTX = ROOT / "docs" / "slides" / "DATN_Proposal - Copy.pptx"
PLAN = ROOT / "docs" / "slides" / "DATN_Proposal_Copy_revision_plan.md"
INTENTION_SOURCE = ROOT / "data" / "bench" / "visualization" / "neg_intention_14_explanation.md"
ACTION_EFFECT_SOURCE = ROOT / "data" / "bench" / "visualization" / "agentic_ae_01_http_429_explanation.md"

NS = {"a": "http://schemas.openxmlformats.org/drawingml/2006/main"}


def _slide_num(name: str) -> int:
    match = re.search(r"slide(\d+)\.xml$", name)
    return int(match.group(1)) if match else 9999


def _read_slide_texts() -> list[str]:
    assert PPTX.exists(), f"Missing target deck: {PPTX}"
    texts: list[str] = []
    with zipfile.ZipFile(PPTX) as deck:
        names = sorted(
            [name for name in deck.namelist() if re.match(r"ppt/slides/slide\d+\.xml$", name)],
            key=_slide_num,
        )
        for name in names:
            root = ET.fromstring(deck.read(name))
            texts.append(
                " ".join(
                    t.text.strip()
                    for t in root.findall(".//a:t", NS)
                    if t.text and t.text.strip()
                )
            )
    return texts


def test_source_visualization_explanations_remain_available() -> None:
    assert INTENTION_SOURCE.exists(), f"Missing intention source visualization note: {INTENTION_SOURCE}"
    assert ACTION_EFFECT_SOURCE.exists(), f"Missing action-effect source visualization note: {ACTION_EFFECT_SOURCE}"

    intention_text = INTENTION_SOURCE.read_text(encoding="utf-8")
    action_effect_text = ACTION_EFFECT_SOURCE.read_text(encoding="utf-8")

    assert "Composting" in intention_text
    assert "rainwater collection" in intention_text
    assert "HTTP 429" in action_effect_text
    assert "Retry-After" in action_effect_text


def test_deck_adds_two_qualitative_proof_slides_from_visualizations() -> None:
    slides = _read_slide_texts()
    assert len(slides) == 16

    intention_slide = slides[12]
    action_effect_slide = slides[13]

    for required in [
        "Qualitative proof: intention stores unfinished plans",
        "What sustainability habit did the user intend to start but has not?",
        "37 facts, including 4 intention nodes",
        "26 facts, 0 intention nodes",
        "Answer: Composting",
        "Wrong decoy: rainwater",
    ]:
        assert required in intention_slide, f"Missing intention proof detail: {required}"

    for required in [
        "Qualitative proof: action-effect stores tool outcomes",
        "When Stripe returns HTTP 429 with Retry-After",
        "13 facts, including 7 action-effect nodes",
        "12 facts, 0 action-effect nodes",
        "sleep + retry",
        "returns 200",
        "Answer hedges: specifics not documented",
    ]:
        assert required in action_effect_slide, f"Missing action-effect proof detail: {required}"


def test_revision_plan_documents_qualitative_evidence_honestly() -> None:
    text = PLAN.read_text(encoding="utf-8")
    required = [
        "This does not prove intention is universally necessary.",
        "This is conditional evidence, not universal proof",
        "5/12",
        "paired-bank",
        "short mocked traces sometimes let the extractor re-type causal rules as world facts",
    ]
    for item in required:
        assert item in text, f"Missing honest methodology note: {item}"


def test_new_slides_do_not_use_unexplained_internal_case_labels() -> None:
    full_text = "\n".join(_read_slide_texts())
    forbidden_patterns = [
        r"\bE7[A-Z]*\b",
        r"\bE9[A-Z]*\b",
        r"\bE10[A-Z]*\b",
        r"\bE11[A-Z]*\b",
        r"\bT8[A-Z]?\b",
        r"\bc\d{3}\b",
        r"PASS\+PARTIAL",
        r"\bPARTIAL\b",
    ]
    for pattern in forbidden_patterns:
        assert not re.search(pattern, full_text), f"Internal label leaked: {pattern}"


if __name__ == "__main__":
    test_source_visualization_explanations_remain_available()
    test_deck_adds_two_qualitative_proof_slides_from_visualizations()
    test_revision_plan_documents_qualitative_evidence_honestly()
    test_new_slides_do_not_use_unexplained_internal_case_labels()
    print("task_s39_intention_action_effect_slide_evidence artifact checks passed")
