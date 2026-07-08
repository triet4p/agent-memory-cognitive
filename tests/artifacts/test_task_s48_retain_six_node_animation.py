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


def test_files_exist_and_are_nonempty() -> None:
    for path in [GIF, PNG, MANIFEST, SCRIPT]:
        assert path.exists(), f"Missing expected retain animation artifact: {path}"
        assert path.stat().st_size > 0, f"Artifact is empty: {path}"


def test_gif_has_expected_canvas_and_frames() -> None:
    with Image.open(GIF) as image:
        assert image.size == (1600, 900), image.size
        assert getattr(image, "n_frames", 1) >= 7, image.n_frames

    with Image.open(PNG) as image:
        assert image.size == (1600, 900), image.size


def test_manifest_covers_goal_requirements() -> None:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))

    required_node_types = {
        "world",
        "experience",
        "opinion",
        "habit",
        "intention",
        "action_effect",
    }
    assert set(manifest["node_types"]) == required_node_types
    assert manifest["node_count"] >= 10
    assert len(manifest["sessions"]) >= 3
    assert manifest["link_count"] >= 6
    assert len(manifest["link_types"]) >= 4
    assert len(manifest["link_annotations"]) == manifest["link_count"]
    assert len(manifest["intra_session_links"]) >= 2
    assert len(manifest["inter_session_links"]) >= 1
    assert min(manifest["durations_ms"]) >= 1500

    joined_links = "\n".join(
        manifest["link_types"]
        + manifest["intra_session_links"]
        + manifest["inter_session_links"]
    )
    for expected in ["s_r_link", "a_o_causal", "transition", "temporal", "intra", "inter"]:
        assert expected in joined_links, f"Missing link evidence: {expected}"


def test_source_names_all_visual_labels() -> None:
    source = SCRIPT.read_text(encoding="utf-8")
    for expected in [
        "solid = intra-session",
        "dashed = inter-session",
        "transition/status",
        "entity/co-topic",
        "semantic",
        "s_r_link",
        "a_o_causal",
        "intra S2",
        "inter S1 -> S3",
        "Query: \"What plan has not been started?\"",
    ]:
        assert expected in source


def main() -> None:
    test_files_exist_and_are_nonempty()
    test_gif_has_expected_canvas_and_frames()
    test_manifest_covers_goal_requirements()
    test_source_names_all_visual_labels()
    print("PASS: retain six-node extraction animation satisfies goal requirements")


if __name__ == "__main__":
    main()
