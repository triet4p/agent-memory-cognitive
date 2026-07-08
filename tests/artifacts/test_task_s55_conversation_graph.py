"""Artifact check for the CogMem conversation graph example."""

from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
GRAPH_HTML = ROOT / "docs" / "slides" / "cogmem_conversation_graph_example.html"


def main() -> None:
    html = GRAPH_HTML.read_text(encoding="utf-8")

    required_node_types = [
        "habit",
        "experience",
        "intention",
        "action_effect",
        "opinion",
        "world",
    ]
    required_links = [
        "s_r_link",
        "triggered",
        "fulfilled_by",
        "a_o_causal",
        "revised_to",
    ]
    required_dialogue = [
        "Mỗi sáng tôi thường uống 2 ly cà phê trước khi code.",
        "từ mai tôi sẽ đổi ly thứ hai sang trà xanh.",
        "Sau 3 ngày đổi sang trà",
    ]

    assert GRAPH_HTML.exists(), f"missing graph artifact: {GRAPH_HTML}"
    for text in required_node_types + required_links + required_dialogue:
        assert text in html, f"missing required graph text: {text}"

    assert html.count('class="node ') == 8, "expected eight visible memory nodes"
    assert "<svg" in html and "</svg>" in html, "expected inline SVG edge layer"


if __name__ == "__main__":
    main()
