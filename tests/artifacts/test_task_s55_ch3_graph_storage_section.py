from __future__ import annotations

from pathlib import Path

from PIL import Image


ROOT = Path(__file__).resolve().parents[2]
CHAPTER = ROOT / "reports" / "final_reports" / "src" / "Chapter" / "3_Methodology.tex"
IMAGE_DIR = ROOT / "reports" / "final_reports" / "src" / "Images"


def main() -> None:
    text = CHAPTER.read_text(encoding="utf-8")

    old_intro = "\\subsection{Động lực nhận thức và cấu trúc đa hệ thống}"
    new_section = "\\subsection{Lược đồ lưu trữ chung của đồ thị bộ nhớ}"
    old_next = "\\subsection{Các mạng phân định}"
    assert old_intro in text
    assert new_section in text
    assert old_next in text
    assert text.index(old_intro) < text.index(new_section) < text.index(old_next)

    required_phrases = [
        "sáu mạng bộ nhớ của CogMem không phải là sáu kho dữ liệu tách rời",
        "tất cả các đơn vị thông tin đều được đặt trong cùng một đồ thị bộ nhớ",
        "\\textit{fact\\_type}",
        "\\textit{metadata}",
        "\\textit{s\\_r\\_link}",
        "\\textit{fulfilled\\_by}",
        "\\textit{a\\_o\\_causal}",
        "\\label{fig:ch3_common_node_storage}",
        "\\label{fig:ch3_typed_edge_storage}",
    ]
    for phrase in required_phrases:
        assert phrase in text, phrase

    for image_name in [
        "cogmem_conversation_nodes_report.png",
        "cogmem_special_links_report.png",
    ]:
        image_path = IMAGE_DIR / image_name
        assert image_path.exists(), image_path
        assert image_path.stat().st_size > 50_000, image_path
        with Image.open(image_path) as image:
            assert image.size == (2400, 1350)

    script = ROOT / "scripts" / "build_ch3_graph_storage_assets.py"
    script_text = script.read_text(encoding="utf-8")
    assert "cairosvg.svg2png" in script_text
    assert "link owned:" in script_text
    assert "edge type:" in script_text


if __name__ == "__main__":
    main()
