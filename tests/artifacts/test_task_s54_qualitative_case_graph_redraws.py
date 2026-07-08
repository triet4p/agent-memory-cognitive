from __future__ import annotations

import json
from pathlib import Path

from PIL import Image


ROOT = Path(__file__).resolve().parents[2]
ASSET_DIR = ROOT / "docs" / "slides" / "assets" / "qualitative_case_graphs"
MANIFEST = ASSET_DIR / "manifest.json"


def main() -> None:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    assert manifest["asset_type"] == "qualitative_case_graph_redraws"
    assert len(manifest["assets"]) == 2
    assert manifest["contact_sheet"] == "docs/slides/assets/qualitative_case_graphs/contact_sheet.png"

    expected_sources = {
        "experiments/cogmem_bench/visualization/neg_intention_14_graph.html",
        "experiments/cogmem_bench/visualization/agentic_ae_01_http_429_graph.html",
    }
    seen_sources = {asset["source_html"] for asset in manifest["assets"]}
    assert seen_sources == expected_sources

    for asset in manifest["assets"]:
        image_path = ROOT / asset["path"]
        assert image_path.exists(), image_path
        assert image_path.stat().st_size > 100_000, image_path
        with Image.open(image_path) as image:
            assert image.size == tuple(asset["canvas"]) == (2200, 1240)
        assert asset["node_count"] <= 10
        assert asset["required_phrases"]
        for phrase in asset["required_phrases"]:
            assert isinstance(phrase, str) and phrase.strip()

    contact = ROOT / manifest["contact_sheet"]
    assert contact.exists(), contact
    with Image.open(contact) as image:
        assert image.width == 1100
        assert image.height > 1000

    script_text = (ROOT / "scripts" / "build_qualitative_case_graph_assets.py").read_text(encoding="utf-8")
    for token in [
        "Composting",
        "Rainwater collection (wrong)",
        "Retry-After",
        "HTTP 429",
        "TYPE REMOVED",
        "not a graph node",
        "action_effect",
        "intention",
    ]:
        assert token in script_text


if __name__ == "__main__":
    main()
