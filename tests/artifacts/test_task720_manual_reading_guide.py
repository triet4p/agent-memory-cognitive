from __future__ import annotations

from pathlib import Path


def _assert_contains_in_order(text: str, chunks: list[str]) -> None:
    cursor = -1
    for chunk in chunks:
        idx = text.find(chunk)
        assert idx != -1, f"Missing expected chunk: {chunk}"
        assert idx > cursor, f"Chunk out of order: {chunk}"
        cursor = idx


def main() -> None:
    repo_root = Path(__file__).resolve().parents[2]

    guide = repo_root / "tutorials" / "manual-code-reading-guide.md"
    index_doc = repo_root / "tutorials" / "INDEX.md"
    learning_path = repo_root / "tutorials" / "learning-path.md"

    assert guide.exists(), "Missing tutorials/manual-code-reading-guide.md"
    assert index_doc.exists(), "Missing tutorials/INDEX.md"
    assert learning_path.exists(), "Missing tutorials/learning-path.md"

    guide_text = guide.read_text(encoding="utf-8")
    index_text = index_doc.read_text(encoding="utf-8")
    learning_path_text = learning_path.read_text(encoding="utf-8")

    required_sections = [
        "## Mục tiêu",
        "## Đọc từ đâu để nắm hệ thống nhanh nhất",
        "## Runtime call chain thật",
        "## Retain call chain thật",
        "## Recall call chain thật",
        "## Reflect call chain thật",
        "## Instance và singleton quan trọng (đây là nơi giữ state)",
        "## File-by-file map (mục đích + phụ thuộc + ai gọi)",
    ]

    for section in required_sections:
        assert section in guide_text, f"Missing section in manual guide: {section}"

    _assert_contains_in_order(guide_text, required_sections)

    required_file_markers = [
        "cogmem_api/main.py",
        "cogmem_api/server.py",
        "cogmem_api/api/http.py",
        "cogmem_api/engine/memory_engine.py",
        "cogmem_api/engine/retain/orchestrator.py",
        "cogmem_api/engine/search/retrieval.py",
        "cogmem_api/engine/reflect/agent.py",
        "cogmem_api/models.py",
        "cogmem_api/config.py",
    ]
    for marker in required_file_markers:
        assert marker in guide_text, f"Missing core file marker in manual guide: {marker}"

    assert "manual-code-reading-guide.md" in index_text
    assert "manual-code-reading-guide.md" in learning_path_text

    print("Task 720 manual reading guide checks passed.")


if __name__ == "__main__":
    main()
