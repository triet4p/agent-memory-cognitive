from __future__ import annotations

import json
from pathlib import Path

from PIL import Image


ROOT = Path(__file__).resolve().parents[2]
STEP_DIR = ROOT / "docs" / "slides" / "assets" / "retain_extraction_steps"
MANIFEST = STEP_DIR / "manifest.json"
CONTACT_SHEET = STEP_DIR / "contact_sheet.png"
SCRIPT = ROOT / "scripts" / "build_retain_extraction_step_images.py"


def _manifest() -> dict:
    return json.loads(MANIFEST.read_text(encoding="utf-8"))


def test_step_assets_exist_and_are_large_enough() -> None:
    manifest = _manifest()
    assert manifest["asset_type"] == "step_images"
    assert manifest["canvas"] == [1600, 900]
    assert manifest["step_count"] == 7

    for step in manifest["steps"]:
        path = ROOT / step["file"]
        assert path.exists(), f"Missing step image: {path}"
        assert path.stat().st_size > 20_000, f"Step image is unexpectedly small: {path}"
        with Image.open(path) as image:
            assert image.size == (1600, 900), image.size

    assert CONTACT_SHEET.exists()
    assert CONTACT_SHEET.stat().st_size > 50_000


def test_sequence_keeps_all_required_extraction_content() -> None:
    manifest = _manifest()
    assert len(manifest["sessions"]) == 3
    assert manifest["node_count"] == 10
    assert set(manifest["node_types"]) == {
        "world",
        "experience",
        "opinion",
        "habit",
        "intention",
        "action_effect",
    }
    assert manifest["link_count"] == 6


def test_temporal_link_is_a_real_time_relation() -> None:
    manifest = _manifest()
    temporal_links = [
        item
        for item in manifest["link_annotations"]
        if item["kind"] == "temporal_order"
    ]
    assert len(temporal_links) == 1
    temporal = temporal_links[0]
    assert temporal["scope"] == "inter-session"
    assert "Mar 1" in temporal["label"]
    assert "Apr 1" in temporal["label"]
    assert "Apr 10" in temporal["label"]
    assert "later" in temporal["meaning"]
    assert "temporal/entity continuity" not in json.dumps(manifest)


def test_links_are_fully_annotated_for_slide_animation() -> None:
    manifest = _manifest()
    for link in manifest["link_annotations"]:
        assert link["kind"]
        assert link["scope"] in {"intra-session", "inter-session"}
        assert link["label"]
        assert link["meaning"]
        if link["scope"] == "intra-session":
            assert "intra" in link["label"]
        else:
            assert "inter" in link["label"]


def test_source_mentions_step_images_not_gif_only() -> None:
    source = SCRIPT.read_text(encoding="utf-8")
    for expected in [
        "STEPS",
        "temporal_order",
        "Mar 1 / target Apr 1 < Apr 10",
        "write_contact_sheet",
        "asset_type",
        "step_images",
    ]:
        assert expected in source


def main() -> None:
    test_step_assets_exist_and_are_large_enough()
    test_sequence_keeps_all_required_extraction_content()
    test_temporal_link_is_a_real_time_relation()
    test_links_are_fully_annotated_for_slide_animation()
    test_source_mentions_step_images_not_gif_only()
    print("PASS: retain extraction step images are clear and temporally grounded")


if __name__ == "__main__":
    main()
