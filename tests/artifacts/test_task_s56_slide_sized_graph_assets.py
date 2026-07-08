"""Artifact checks for slide-sized CogMem graph SVGs."""

from __future__ import annotations

from pathlib import Path
from xml.etree import ElementTree


ROOT = Path(__file__).resolve().parents[2]
ASSET_DIR = ROOT / "docs" / "slides" / "assets"
NODE_SLIDE = ASSET_DIR / "cogmem_conversation_nodes_slide.svg"
LINK_SLIDE = ASSET_DIR / "cogmem_special_links_slide.svg"


def _read_svg(path: Path) -> str:
    assert path.exists(), f"missing SVG asset: {path}"
    text = path.read_text(encoding="utf-8")
    root = ElementTree.fromstring(text)
    assert root.attrib.get("width") == "1600", f"{path.name} width must be slide-sized"
    assert root.attrib.get("height") == "900", f"{path.name} height must be slide-sized"
    assert root.attrib.get("viewBox") == "0 0 1600 900", f"{path.name} viewBox must be 16:9"
    return text


def main() -> None:
    node_svg = _read_svg(NODE_SLIDE)
    link_svg = _read_svg(LINK_SLIDE)

    for node_type in ["habit", "experience", "intention", "action_effect", "opinion", "world"]:
        assert node_type in node_svg, f"node slide missing node type: {node_type}"

    for link in ["s_r_link", "triggered", "fulfilled_by", "a_o_causal", "revised_to"]:
        assert link in node_svg, f"node slide missing link label: {link}"
        assert link in link_svg, f"link slide missing link label: {link}"

    assert "Mỗi sáng tôi uống 2 ly cà phê" in node_svg
    assert "Graph link đặc trưng" not in link_svg
    assert "Đọc graph" not in link_svg
    assert "Từ một đoạn hội thoại" not in node_svg
    assert "semantic" in link_svg
    assert "filter: drop-shadow" in node_svg
    assert 'markerWidth="8"' in node_svg
    assert 'markerWidth="8"' in link_svg


if __name__ == "__main__":
    main()
