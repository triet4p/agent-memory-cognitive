from __future__ import annotations

import re
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET


ROOT = Path(__file__).resolve().parents[2]
DECK = ROOT / "docs" / "slides" / "DATN_Final_Defense_Draft.pptx"


def _slide_paths(deck: zipfile.ZipFile) -> list[str]:
    paths = [
        name
        for name in deck.namelist()
        if re.fullmatch(r"ppt/slides/slide\d+\.xml", name)
    ]
    return sorted(paths, key=lambda name: int(re.search(r"slide(\d+)", name).group(1)))


def _all_text(deck: zipfile.ZipFile, paths: list[str]) -> str:
    parts: list[str] = []
    for path in paths:
        root = ET.fromstring(deck.read(path))
        for node in root.iter():
            if node.tag.endswith("}t") and node.text:
                parts.append(node.text)
    return "\n".join(parts)


def _image_rel_count(deck: zipfile.ZipFile, slide_number: int) -> int:
    rel_path = f"ppt/slides/_rels/slide{slide_number}.xml.rels"
    root = ET.fromstring(deck.read(rel_path))
    return sum(
        1
        for rel in root
        if "image" in (rel.attrib.get("Type") or "")
    )


def main() -> None:
    assert DECK.exists(), f"Missing deck: {DECK}"
    assert DECK.stat().st_size > 2_000_000, "Deck is unexpectedly small"

    with zipfile.ZipFile(DECK) as deck:
        slides = _slide_paths(deck)
        assert len(slides) == 27, f"Expected 27 slides, found {len(slides)}"

        media = [
            name
            for name in deck.namelist()
            if name.startswith("ppt/media/") and not name.endswith("/")
        ]
        assert len(media) >= 27, f"Expected at least 27 media assets, found {len(media)}"
        assert all(deck.getinfo(name).file_size > 0 for name in media), "Found empty media asset"

        text = _all_text(deck, slides)
        required_terms = [
            "CogMem",
            "Talk Map",
            "LongMemEval Results",
            "31/35",
            "119/161",
            "Intention Case",
            "Action-Effect Case",
            "Q&A",
        ]
        missing = [term for term in required_terms if term not in text]
        assert not missing, f"Missing expected deck text: {missing}"

        assert _image_rel_count(deck, 23) >= 2, "Slide 23 should contain summary and graph crop images"
        assert _image_rel_count(deck, 24) >= 2, "Slide 24 should contain summary and graph crop images"

    print("PASS: final defense draft deck package looks valid")


if __name__ == "__main__":
    main()
