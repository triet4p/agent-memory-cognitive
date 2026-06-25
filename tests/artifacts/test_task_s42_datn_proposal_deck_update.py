from __future__ import annotations

import re
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
PPTX = ROOT / "docs" / "slides" / "DATN_Proposal - Copy.pptx"
NS = {"a": "http://schemas.openxmlformats.org/drawingml/2006/main"}


def _slide_texts() -> list[list[str]]:
    with zipfile.ZipFile(PPTX) as archive:
        slide_names = sorted(
            [name for name in archive.namelist() if re.match(r"ppt/slides/slide\d+\.xml$", name)],
            key=lambda name: int(re.search(r"slide(\d+)\.xml", name).group(1)),
        )
        slides: list[list[str]] = []
        for name in slide_names:
            root = ET.fromstring(archive.read(name))
            texts = [node.text.strip() for node in root.findall(".//a:t", NS) if node.text and node.text.strip()]
            slides.append(texts)
    return slides


def _joined(slides: list[list[str]]) -> str:
    return "\n".join("\n".join(slide) for slide in slides)


def test_deck_keeps_expected_slide_count_and_reader_friendly_terms() -> None:
    slides = _slide_texts()
    combined = _joined(slides)

    assert len(slides) == 16
    for forbidden in ["LongMemEval v16", "manual PASS", "Manual PASS", "Manual Verdict", "PASS+PARTIAL"]:
        assert forbidden not in combined, f"forbidden deck wording remains: {forbidden}"


def test_outline_matches_updated_report_story() -> None:
    slides = _slide_texts()

    assert "Problem: long conversations break short-context memory" in "\n".join(slides[1])
    assert "HINDSIGHT starts from observations before graph recall" in "\n".join(slides[2])
    assert "Retain walkthrough: raw dialogue becomes typed evidence" in "\n".join(slides[3])
    assert "Evaluation: judge PASS is the reported metric" in "\n".join(slides[8])


def test_experiment_results_match_chapter_5() -> None:
    combined = _joined(_slide_texts())

    for token in [
        "31/35",
        "Multi-channel + 6 types",
        "30/35",
        "HINDSIGHT baseline",
        "judge PASS = 88.6%",
        "judge PASS = 85.7%",
        "119/161",
        "judge PASS = 73.9%",
        "judge PASS = 60.2%",
        "LongMemEval 31/35; LoCoMo 119/161",
        "~30 min vs 90-120; ~700 vs ~1500 nodes",
    ]:
        assert token in combined, f"missing updated result in deck: {token}"


def test_retention_and_qualitative_proof_slides_remain() -> None:
    combined = _joined(_slide_texts())

    for token in [
        "Typed memory node",
        "Lossless evidence",
        "Intention and action-effect have targeted qualitative ablations",
        "Qualitative proof: intention stores unfinished plans",
        "Qualitative proof: action-effect stores tool outcomes",
        "Habit remains the least-proven type",
    ]:
        assert token in combined, f"missing methodology/proof content: {token}"


if __name__ == "__main__":
    test_deck_keeps_expected_slide_count_and_reader_friendly_terms()
    test_outline_matches_updated_report_story()
    test_experiment_results_match_chapter_5()
    test_retention_and_qualitative_proof_slides_remain()
    print("task_s42_datn_proposal_deck_update artifact checks passed")
