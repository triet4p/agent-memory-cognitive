from __future__ import annotations

import re
import posixpath
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
PPTX = ROOT / "docs" / "slides" / "DATN_Proposal - Copy.pptx"

NS = {
    "a": "http://schemas.openxmlformats.org/drawingml/2006/main",
    "p": "http://schemas.openxmlformats.org/presentationml/2006/main",
    "rel": "http://schemas.openxmlformats.org/package/2006/relationships",
}


def _slide_num(name: str) -> int:
    match = re.search(r"slide(\d+)\.xml$", name)
    return int(match.group(1)) if match else 9999


def _read_slides() -> list[tuple[int, str, int]]:
    assert PPTX.exists(), f"Missing target deck: {PPTX}"
    slides: list[tuple[int, str, int]] = []
    with zipfile.ZipFile(PPTX) as deck:
        names = sorted(
            [
                name
                for name in deck.namelist()
                if re.match(r"ppt/slides/slide\d+\.xml$", name)
            ],
            key=_slide_num,
        )
        for name in names:
            xml = deck.read(name)
            root = ET.fromstring(xml)
            text = " ".join(
                t.text.strip()
                for t in root.findall(".//a:t", NS)
                if t.text and t.text.strip()
            )
            pic_count = len(root.findall(".//p:pic", NS))
            slides.append((_slide_num(name), text, pic_count))
    return slides


def _read_slide_size() -> tuple[int, int]:
    with zipfile.ZipFile(PPTX) as deck:
        root = ET.fromstring(deck.read("ppt/presentation.xml"))
    size = root.find(".//p:sldSz", NS)
    assert size is not None, "Missing slide size metadata"
    return int(size.attrib["cx"]), int(size.attrib["cy"])


def _read_slide_layout_names() -> list[str]:
    layout_names: list[str] = []
    with zipfile.ZipFile(PPTX) as deck:
        slide_names = sorted(
            [
                name
                for name in deck.namelist()
                if re.match(r"ppt/slides/slide\d+\.xml$", name)
            ],
            key=_slide_num,
        )
        for slide_name in slide_names:
            rel_name = f"ppt/slides/_rels/{Path(slide_name).name}.rels"
            rel_root = ET.fromstring(deck.read(rel_name))
            layout_target = None
            for rel in rel_root.findall(".//rel:Relationship", NS):
                if rel.attrib.get("Type", "").endswith("/slideLayout"):
                    layout_target = rel.attrib["Target"]
                    break
            assert layout_target is not None, f"Missing layout relationship for {slide_name}"
            layout_path = posixpath.normpath(posixpath.join("ppt/slides", layout_target))
            layout_root = ET.fromstring(deck.read(layout_path))
            c_sld = layout_root.find(".//p:cSld", NS)
            assert c_sld is not None, f"Missing cSld in {layout_path}"
            layout_names.append(c_sld.attrib.get("name", ""))
    return layout_names


def test_deck_was_rebuilt_to_defense_length() -> None:
    slides = _read_slides()
    assert len(slides) == 16
    assert _read_slide_size() == (9144000, 6858000)
    assert slides[0][1].startswith("CogMem")
    assert "THANK YOU" in slides[-1][1]


def test_deck_uses_original_three_template_layouts() -> None:
    layout_names = _read_slide_layout_names()
    assert layout_names[0] == "1_Title and Content"
    assert layout_names[1:15] == ["2_Two Content"] * 14
    assert layout_names[15] == "1_Content with Caption"


def test_deck_covers_required_story_arc() -> None:
    full_text = "\n".join(text for _, text, _ in _read_slides())
    required = [
        "Problem: long conversations break short-context memory",
        "Solution overview: Retain -> Graph -> Recall -> Answer",
        "What is stored: compressed fact + lossless snippet",
        "Six typed memory networks",
        "Recall: four channels become one ranked evidence list",
        "Graph recall: SUM instead of MAX",
        "Running example: before-travel question",
        "Evaluation: manual verdicts, not blind judge trust",
        "LongMemEval v16: multi-channel recall is strongest",
        "Control experiment: SUM improves graph-only top-k priority",
        "LoCoMo: final system crosses the 70% target",
        "Qualitative proof: intention stores unfinished plans",
        "Qualitative proof: action-effect stores tool outcomes",
        "What was proved, and what remains",
    ]
    for item in required:
        assert item in full_text, f"Missing story slide: {item}"


def test_deck_reports_current_results_not_old_proposal_eval() -> None:
    full_text = "\n".join(text for _, text, _ in _read_slides())
    required_numbers = [
        "29/35",
        "82.9%",
        "26/35",
        "74.3%",
        "0.8052",
        "0.7624",
        "+0.0429",
        "119/161",
        "73.9%",
        "97/161",
        "60.2%",
        "+22",
        "41.7%",
        "37 facts",
        "26 facts",
        "13 facts",
        "12 facts",
        "5/12",
    ]
    for number in required_numbers:
        assert number in full_text, f"Missing result number: {number}"
    old_eval_markers = ["10/12", "83%", "12 conversation", "Ministral3-3B"]
    for marker in old_eval_markers:
        assert marker not in full_text, f"Old proposal eval marker remains: {marker}"


def test_deck_has_visual_slides_and_text_labels() -> None:
    slides = _read_slides()
    pic_slides = {num for num, _, pic_count in slides if pic_count > 0}
    assert {3, 5, 9}.issubset(pic_slides)
    full_text = "\n".join(text for _, text, _ in slides)
    visual_labels = [
        "Retain typed facts",
        "Store memory graph",
        "Multi-channel recall",
        "Grounded generation",
        "Narrative fact",
        "Raw snippet",
        "Graph-only SUM",
        "Graph-only MAX",
        "Full memory bank",
        "Intention-ablated bank",
        "Action-effect-ablated bank",
    ]
    for label in visual_labels:
        assert label in full_text, f"Missing visual label: {label}"


def test_deck_includes_qualitative_intention_and_action_effect_evidence() -> None:
    full_text = "\n".join(text for _, text, _ in _read_slides())
    required = [
        "plans composting",
        "Answer: Composting",
        "Wrong decoy: rainwater",
        "HTTP 429",
        "Retry-After",
        "sleep + retry",
        "returns 200",
        "Answer hedges: specifics not documented",
        "conditional evidence",
    ]
    for item in required:
        assert item in full_text, f"Missing qualitative proof evidence: {item}"


def test_deck_avoids_unexplained_internal_labels() -> None:
    full_text = "\n".join(text for _, text, _ in _read_slides())
    assert "CogMem defense deck |" not in full_text
    forbidden_patterns = [
        r"\bE7[A-Z]*\b",
        r"\bT8[A-Z]?\b",
        r"\bc\d{3}\b",
        r"PASS\+PARTIAL",
        r"\bPARTIAL\b",
    ]
    for pattern in forbidden_patterns:
        assert not re.search(pattern, full_text), f"Internal label leaked: {pattern}"


if __name__ == "__main__":
    test_deck_was_rebuilt_to_defense_length()
    test_deck_uses_original_three_template_layouts()
    test_deck_covers_required_story_arc()
    test_deck_reports_current_results_not_old_proposal_eval()
    test_deck_has_visual_slides_and_text_labels()
    test_deck_includes_qualitative_intention_and_action_effect_evidence()
    test_deck_avoids_unexplained_internal_labels()
    print("task_s38_direct_pptx_revision artifact checks passed")
