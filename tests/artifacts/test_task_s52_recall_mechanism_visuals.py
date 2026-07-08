from __future__ import annotations

import json
from pathlib import Path

from PIL import Image


ROOT = Path(__file__).resolve().parents[2]
ASSET_DIR = ROOT / "docs" / "slides" / "assets" / "recall_mechanism_visuals"
MANIFEST = ASSET_DIR / "manifest.json"
SCRIPT = ROOT / "scripts" / "build_recall_mechanism_visuals.py"


def _manifest() -> dict:
    return json.loads(MANIFEST.read_text(encoding="utf-8"))


def test_all_recall_visual_assets_exist() -> None:
    manifest = _manifest()
    assert manifest["asset_type"] == "recall_mechanism_diagram_assets"
    assert manifest["canvas"] == [1600, 900]
    assert manifest["image_count"] == 3
    assert manifest["style"] == "diagram_asset_not_full_slide"
    assert manifest["formula_renderer"] == "matplotlib_mathtext"
    assert manifest["text_scale"] == "slide_readable_large"

    for item in manifest["images"]:
        path = ROOT / item["file"]
        assert path.exists(), path
        assert path.stat().st_size > 40_000, path
        with Image.open(path) as image:
            assert image.size == (1600, 900)

    contact_sheet = ROOT / manifest["contact_sheet"]
    assert contact_sheet.exists()
    assert contact_sheet.stat().st_size > 40_000


def test_visuals_cover_requested_mechanisms() -> None:
    manifest = _manifest()
    concepts = " ".join(manifest["required_concepts"])
    for expected in [
        "four recall channels",
        "Weighted RRF",
        "ADR - Đóng góp 3",
        "Cross Encoder",
        "final scoring uses both CE and RRF",
        "symbol legend",
        "LaTeX-style formula rendering",
        "init node activation",
        "multi-layer propagation graph",
        "contribution table",
        "SUM vs MAX ranking effect",
        "Refractory",
        "Firing quota",
        "Saturation",
    ]:
        assert expected in concepts


def test_renderer_contains_slide_text_for_required_diagrams() -> None:
    source = SCRIPT.read_text(encoding="utf-8")
    for expected in [
        "matplotlib.use",
        "math_img",
        "Semantic",
        "BM25",
        "Graph",
        "Temporal",
        "Weighted RRF",
        "Cross Encoder",
        "s_{\\mathrm{RRF}}",
        "A_0(s)=\\mathrm{sim}(q,s)",
        "a_{u\\to v}=A(u)",
        "Symbol legend",
        "Contribution table",
        "A_T=\\max(e_1,e_2,e_4)=0.08",
        "A_T=e_1+e_2+e_4=0.21",
        "Refractory",
        "Firing quota",
        "Saturation",
    ]:
        assert expected in source


def main() -> None:
    test_all_recall_visual_assets_exist()
    test_visuals_cover_requested_mechanisms()
    test_renderer_contains_slide_text_for_required_diagrams()
    print("PASS: recall mechanism visuals cover pipeline, SUM/MAX, and guards")


if __name__ == "__main__":
    main()
