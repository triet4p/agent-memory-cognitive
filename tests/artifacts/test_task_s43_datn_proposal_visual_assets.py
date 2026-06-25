from __future__ import annotations

import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET


ROOT = Path(__file__).resolve().parents[2]
PPTX = ROOT / "docs" / "slides" / "DATN_Proposal - Copy.pptx"
ASSET_DIR = ROOT / "docs" / "slides" / "assets"

NS = {
    "a": "http://schemas.openxmlformats.org/drawingml/2006/main",
    "p": "http://schemas.openxmlformats.org/presentationml/2006/main",
}


def _slide_text(zip_file: zipfile.ZipFile, slide_no: int) -> str:
    xml = zip_file.read(f"ppt/slides/slide{slide_no}.xml")
    root = ET.fromstring(xml)
    return "\n".join(node.text or "" for node in root.findall(".//a:t", NS))


def _slide_xml(zip_file: zipfile.ZipFile, slide_no: int) -> str:
    return zip_file.read(f"ppt/slides/slide{slide_no}.xml").decode("utf-8", errors="replace")


def _slide_rels(zip_file: zipfile.ZipFile, slide_no: int) -> str:
    return zip_file.read(f"ppt/slides/_rels/slide{slide_no}.xml.rels").decode(
        "utf-8",
        errors="replace",
    )


def main() -> None:
    required_assets = [
        ASSET_DIR / "retain_intra_inter_links_animation.html",
        ASSET_DIR / "retain_intra_inter_links_animation.gif",
        ASSET_DIR / "neg_intention_14_graph.png",
        ASSET_DIR / "agentic_ae_01_http_429_graph.png",
    ]
    for asset in required_assets:
        assert asset.exists(), f"missing visual asset: {asset}"
        minimum_size = 1_000 if asset.suffix == ".html" else 10_000
        assert asset.stat().st_size > minimum_size, f"visual asset looks empty: {asset}"

    html = (ASSET_DIR / "retain_intra_inter_links_animation.html").read_text(
        encoding="utf-8"
    )
    assert "intra-session link" in html
    assert "inter-session link" in html
    assert "edge-recall" in html
    assert "URLSearchParams" in html

    assert PPTX.exists(), f"missing deck: {PPTX}"
    assert PPTX.stat().st_size > 1_000_000, "deck is unexpectedly small"

    with zipfile.ZipFile(PPTX) as zip_file:
        slides = [
            name
            for name in zip_file.namelist()
            if name.startswith("ppt/slides/slide") and name.endswith(".xml")
        ]
        media = [name for name in zip_file.namelist() if name.startswith("ppt/media/")]
        assert len(slides) == 16, f"expected 16 slides, found {len(slides)}"
        assert any(name.endswith(".gif") for name in media), "retain GIF not embedded"
        assert len(media) >= 12, "expected embedded deck media assets"

        slide4_text = _slide_text(zip_file, 4)
        assert "solid teal = intra-session links" in slide4_text
        assert "dashed gold = inter-session links" in slide4_text
        assert "CodexViz retain intra/inter animated GIF" in _slide_xml(zip_file, 4)
        assert ".gif" in _slide_rels(zip_file, 4)

        slide13_text = _slide_text(zip_file, 13)
        assert "FULL BANK: gold representation exists" in slide13_text
        assert "ABLATED BANK: gold representation removed" in slide13_text
        assert "[experience] rain barrel / rainwater garden" in slide13_text
        assert "Speaker cue:" not in slide13_text
        assert "CodexViz intention graph screenshot" in _slide_xml(zip_file, 13)

        slide14_text = _slide_text(zip_file, 14)
        assert "FULL BANK: causal triple is explicit" in slide14_text
        assert "ABLATED BANK: causal bridge is missing" in slide14_text
        assert "condition -> action -> 200 outcome" in slide14_text
        assert "Speaker cue:" not in slide14_text
        assert "CodexViz action-effect graph screenshot" in _slide_xml(zip_file, 14)

    print("task_s43_datn_proposal_visual_assets artifact checks passed")


if __name__ == "__main__":
    main()
