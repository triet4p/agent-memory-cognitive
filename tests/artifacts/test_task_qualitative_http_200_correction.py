from __future__ import annotations

import json
from pathlib import Path

from PIL import Image


ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts" / "build_qualitative_case_graph_assets.py"
MANIFEST = ROOT / "docs" / "slides" / "assets" / "qualitative_case_graphs" / "manifest.json"
HTTP_IMAGE = ROOT / "docs" / "slides" / "assets" / "qualitative_case_graphs" / "02_action_effect_full_vs_ablated.png"


def main() -> None:
    script_text = SCRIPT.read_text(encoding="utf-8")
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))

    assert HTTP_IMAGE.exists(), HTTP_IMAGE
    assert HTTP_IMAGE.stat().st_size > 100_000
    with Image.open(HTTP_IMAGE) as image:
        assert image.size == (2200, 1240)

    full_start = 'panel(d, 60, 180, 1000, 900, "Full bank E7F"'
    ablated_start = 'removed_note(d, 1215, 320, 450, 165, "TYPE REMOVED"'
    assert full_start in script_text
    assert ablated_start in script_text
    full_section = script_text.split(full_start, 1)[1].split(ablated_start, 1)[0]
    ablated_section = script_text.split(ablated_start, 1)[1]

    assert "Run output: in_1: 200; in_2: 200; in_3: 200" in full_section
    assert "the cited run returns 200 for all invoices" in full_section

    assert "in_1: 200" not in ablated_section
    assert "in_2: 200" not in ablated_section
    assert "in_3: 200" not in ablated_section
    assert "Ablated generated answer: missing causal chain" in ablated_section
    assert "Missing: wait Retry-After -> retry -> 200" in ablated_section

    ae_asset = next(asset for asset in manifest["assets"] if "action_effect" in asset["path"])
    for phrase in ["in_1: 200", "in_2: 200", "in_3: 200", "missing causal chain", "Missing: wait Retry-After"]:
        assert phrase in ae_asset["required_phrases"]


if __name__ == "__main__":
    main()
