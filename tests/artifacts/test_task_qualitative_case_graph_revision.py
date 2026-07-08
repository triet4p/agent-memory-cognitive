from __future__ import annotations

import json
from pathlib import Path

from PIL import Image


ROOT = Path(__file__).resolve().parents[2]
ASSET_DIR = ROOT / "docs" / "slides" / "assets" / "qualitative_case_graphs"
SCRIPT = ROOT / "scripts" / "build_qualitative_case_graph_assets.py"
MANIFEST = ASSET_DIR / "manifest.json"


def _segment_after(text: str, start: str, stop: str) -> str:
    assert start in text, start
    segment = text.split(start, 1)[1]
    assert stop in segment, stop
    return segment.split(stop, 1)[0]


def main() -> None:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    manifest_text = json.dumps(manifest, ensure_ascii=False)
    script_text = SCRIPT.read_text(encoding="utf-8")

    assert "Focused graph" not in script_text
    assert "partial" not in script_text.lower()
    assert "partial" not in manifest_text.lower()

    for image_name in [
        "01_intention_full_vs_ablated.png",
        "02_action_effect_full_vs_ablated.png",
    ]:
        image_path = ASSET_DIR / image_name
        assert image_path.exists(), image_path
        assert image_path.stat().st_size > 100_000, image_path
        with Image.open(image_path) as image:
            assert image.size == (2200, 1240)

    assert "Ablated generated answer: Rainwater collection (wrong)" in script_text
    assert "Ablated generated answer: missing causal chain" in script_text
    assert "Missing: wait Retry-After -> retry -> 200" in script_text
    assert "subsequent calls return 200" in script_text
    assert "Run output: in_1: 200; in_2: 200; in_3: 200" in script_text
    assert "Generic backoff logic added for rate limits" in script_text

    intention_note = _segment_after(
        script_text,
        'removed_note(d, 1215, 310, 440, 155, "TYPE REMOVED"',
        'card(d, 1690, 335, 380, 185, "R5"',
    )
    action_effect_note = _segment_after(
        script_text,
        'removed_note(d, 1215, 320, 450, 165, "TYPE REMOVED"',
        'card(d, 1710, 320, 390, 180, "R1"',
    )
    assert "arrow(" not in intention_note
    assert "arrow(" not in action_effect_note

    ae_asset = next(
        asset for asset in manifest["assets"] if "action_effect" in asset["path"]
    )
    assert "missing causal chain" in ae_asset["required_phrases"]
    assert "Missing: wait Retry-After" in ae_asset["required_phrases"]
    assert "partial" not in ae_asset["required_phrases"]


if __name__ == "__main__":
    main()
