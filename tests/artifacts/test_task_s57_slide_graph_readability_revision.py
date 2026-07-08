"""Checks for the revised slide graph readability requirements."""

from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
ASSET_DIR = ROOT / "docs" / "slides" / "assets"
NODE_SLIDE = ASSET_DIR / "cogmem_conversation_nodes_slide.svg"
LINK_SLIDE = ASSET_DIR / "cogmem_special_links_slide.svg"


def main() -> None:
    node_svg = NODE_SLIDE.read_text(encoding="utf-8")
    link_svg = LINK_SLIDE.read_text(encoding="utf-8")

    forbidden_visible_copy = [
        "Từ một đoạn hội thoại -> các memory nodes",
        "Ví dụ đủ 6 loại node",
        "Graph link đặc trưng từ cùng một hội thoại",
        "Mỗi cạnh thể hiện",
        "Đọc graph",
    ]
    for text in forbidden_visible_copy:
        assert text not in node_svg
        assert text not in link_svg

    for node_type in ["habit", "experience", "intention", "action_effect", "opinion", "world"]:
        assert f">{node_type}<" in node_svg or f">{node_type}<" in link_svg

    longer_facts = [
        "User thường uống 2 ly",
        "User dự định từ mai",
        "Đổi ly thứ hai từ cà phê",
        "Belief đổi từ",
        "Trà xanh có caffeine",
    ]
    for text in longer_facts:
        assert text in node_svg

    assert "class=\"node-title\"" not in node_svg
    assert "class=\"node-title\"" not in link_svg
    assert node_svg.count('markerWidth="8"') == 1
    assert link_svg.count('markerWidth="8"') == 5


if __name__ == "__main__":
    main()
