from __future__ import annotations

import json
from pathlib import Path

from PIL import Image


ROOT = Path(__file__).resolve().parents[2]
ASSET_DIR = ROOT / "docs" / "slides" / "assets"
GIF = ASSET_DIR / "retain_six_node_extraction_animation.gif"
PNG = ASSET_DIR / "retain_six_node_extraction_final.png"
MANIFEST = ASSET_DIR / "retain_six_node_extraction_animation_manifest.json"
SCRIPT = ROOT / "scripts" / "build_retain_six_node_extraction_animation.py"


def test_revision_has_more_nodes_and_clearer_canvas() -> None:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    assert manifest["canvas"] == [1600, 900]
    assert manifest["node_count"] == 10
    assert manifest["link_count"] == 6
    assert min(manifest["durations_ms"]) >= 1500
    assert max(manifest["durations_ms"]) >= 3000


def test_each_link_has_scope_label_and_meaning() -> None:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    scopes = {item["scope"] for item in manifest["link_annotations"]}
    assert scopes == {"intra-session", "inter-session"}

    for item in manifest["link_annotations"]:
        assert item["kind"]
        assert item["label"]
        assert item["meaning"]
        assert "intra" in item["label"] or "inter" in item["label"]


def test_final_preview_is_large_and_not_blank() -> None:
    with Image.open(PNG).convert("RGB") as image:
        assert image.size == (1600, 900)
        sample_points = [
            image.getpixel((120, 320)),
            image.getpixel((700, 330)),
            image.getpixel((1300, 500)),
            image.getpixel((100, 854)),
        ]
        assert len(set(sample_points)) > 2

    with Image.open(GIF) as image:
        assert image.size == (1600, 900)
        assert image.n_frames == 7


def test_source_uses_larger_text_and_explicit_link_labels() -> None:
    source = SCRIPT.read_text(encoding="utf-8")
    for expected in [
        '"title": font(40',
        '"node": font(17',
        "label_box",
        "entity/co-topic",
        "temporal/entity",
        "transition/status",
        "a_o_causal",
        "durations_ms",
    ]:
        assert expected in source


def main() -> None:
    test_revision_has_more_nodes_and_clearer_canvas()
    test_each_link_has_scope_label_and_meaning()
    test_final_preview_is_large_and_not_blank()
    test_source_uses_larger_text_and_explicit_link_labels()
    print("PASS: retain extraction animation readability revision checks passed")


if __name__ == "__main__":
    main()
