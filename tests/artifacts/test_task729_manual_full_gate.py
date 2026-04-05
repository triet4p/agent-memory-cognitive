from __future__ import annotations

import re
from pathlib import Path


MANIFEST_ROW_RE = re.compile(
    r"^\|\s*(\d+)\s*\|\s*([^|]+?)\s*\|\s*(\.[a-z0-9]+)\s*\|\s*(not-started|in-progress|done)\s*\|\s*([^|]+?)\s*\|$"
)
LINK_CELL_RE = re.compile(r"^\[([^\]]+)\]\([^\)]+\)$")

REQUIRED_DOC_SECTIONS = [
    "## Purpose",
    "## Symbol-by-symbol explanation",
    "## Cross-file dependencies (inbound/outbound)",
    "## Runtime implications/side effects",
    "## Failure modes",
    "## Verify commands",
]


def _parse_manifest_rows(manifest_text: str) -> list[tuple[int, str, str, str, str]]:
    rows: list[tuple[int, str, str, str, str]] = []
    for line in manifest_text.splitlines():
        match = MANIFEST_ROW_RE.match(line)
        if not match:
            continue

        rows.append(
            (
                int(match.group(1)),
                _normalize_cell(match.group(2)),
                match.group(3).strip(),
                match.group(4).strip(),
                _normalize_cell(match.group(5)),
            )
        )
    return rows


def _normalize_cell(value: str) -> str:
    raw = value.strip()
    match = LINK_CELL_RE.match(raw)
    if match:
        return match.group(1).strip()
    return raw


def _assert_required_sections(doc_path: Path) -> None:
    text = doc_path.read_text(encoding="utf-8")
    for section in REQUIRED_DOC_SECTIONS:
        assert section in text, f"Missing section '{section}' in {doc_path.as_posix()}"


def main() -> None:
    repo_root = Path(__file__).resolve().parents[2]

    manifest_path = repo_root / "tutorials" / "per-file" / "file-manifest.md"
    reading_order_path = repo_root / "tutorials" / "per-file" / "READING-ORDER.md"
    per_file_index_path = repo_root / "tutorials" / "per-file" / "INDEX.md"

    assert manifest_path.exists(), "Missing tutorials/per-file/file-manifest.md"
    assert reading_order_path.exists(), "Missing tutorials/per-file/READING-ORDER.md"
    assert per_file_index_path.exists(), "Missing tutorials/per-file/INDEX.md"

    manifest_text = manifest_path.read_text(encoding="utf-8")
    reading_order_text = reading_order_path.read_text(encoding="utf-8")
    per_file_index_text = per_file_index_path.read_text(encoding="utf-8")

    rows = _parse_manifest_rows(manifest_text)
    assert rows, "Manifest table has no parseable rows"

    row_ids = [row[0] for row in rows]
    assert row_ids == list(range(1, len(rows) + 1)), "Manifest row IDs must be contiguous"

    source_files = [row[1] for row in rows]
    statuses = [row[3] for row in rows]
    tutorial_docs = [row[4] for row in rows]

    assert len(set(source_files)) == len(source_files), "Duplicate source files in manifest"
    assert len(set(tutorial_docs)) == len(tutorial_docs), "Each source file must map to exactly one tutorial doc"
    assert all(status == "done" for status in statuses), "All manifest rows must be done at final gate"

    for _, source_file, extension, _, tutorial_doc in rows:
        assert source_file.endswith(extension), (
            f"Manifest extension mismatch for source '{source_file}' and extension '{extension}'"
        )
        assert tutorial_doc != "TBD", f"Tutorial doc must not be TBD for {source_file}"
        assert tutorial_doc.startswith("tutorials/per-file/"), (
            f"Canonical tutorial must live under tutorials/per-file: {tutorial_doc}"
        )
        assert not tutorial_doc.startswith("tutorials/functions/"), (
            f"tutorials/functions is not canonical per-file explanation: {tutorial_doc}"
        )

        doc_path = repo_root / tutorial_doc
        assert doc_path.exists(), f"Missing tutorial doc: {tutorial_doc}"
        assert doc_path.suffix == ".md", f"Tutorial doc must be markdown: {tutorial_doc}"

        _assert_required_sections(doc_path)

        doc_text = doc_path.read_text(encoding="utf-8")
        assert source_file in doc_text, f"Missing source marker '{source_file}' in {tutorial_doc}"

    # Reading order must reference all canonical tutorial docs.
    for tutorial_doc in tutorial_docs:
        assert tutorial_doc in reading_order_text, (
            f"READING-ORDER does not reference canonical tutorial doc: {tutorial_doc}"
        )

    # Per-file index must point to READING-ORDER as canonical entry.
    assert "READING-ORDER.md" in per_file_index_text, "Per-file index must reference READING-ORDER.md"

    print("Task 729 manual full gate checks passed.")


if __name__ == "__main__":
    main()
