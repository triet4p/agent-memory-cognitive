from __future__ import annotations

import re
from pathlib import Path


REQUIRED_MANUAL_DOCS = {
    "cogmem_api/__init__.py": "tutorials/per-file/bootstrap--cogmem-api-init.md",
    "cogmem_api/main.py": "tutorials/per-file/bootstrap--cogmem-api-main.md",
    "cogmem_api/server.py": "tutorials/per-file/bootstrap--cogmem-api-server.md",
    "cogmem_api/config.py": "tutorials/per-file/bootstrap--cogmem-api-config.md",
    "cogmem_api/pg0.py": "tutorials/per-file/bootstrap--cogmem-api-pg0.md",
}

REQUIRED_DOC_SECTIONS = [
    "## Purpose",
    "## Source File",
    "## Symbol-by-symbol explanation",
    "## Cross-file dependencies (inbound/outbound)",
    "## Runtime implications/side effects",
    "## Failure modes",
    "## Verify commands",
]

ROW_RE = re.compile(
    r"^\|\s*(\d+)\s*\|\s*([^|]+?)\s*\|\s*(\.[a-z0-9]+)\s*\|\s*(not-started|in-progress|done)\s*\|\s*([^|]+?)\s*\|$"
)
LINK_CELL_RE = re.compile(r"^\[([^\]]+)\]\([^\)]+\)$")


def _normalize_cell(value: str) -> str:
    raw = value.strip()
    match = LINK_CELL_RE.match(raw)
    if match:
        return match.group(1).strip()
    return raw


def _read(repo_root: Path, rel_path: str) -> str:
    return (repo_root / rel_path).read_text(encoding="utf-8")


def _assert_doc_contract(repo_root: Path, source_file: str, doc_file: str) -> None:
    doc_path = repo_root / doc_file
    assert doc_path.exists(), f"Missing manual bootstrap tutorial: {doc_file}"

    text = doc_path.read_text(encoding="utf-8")

    for section in REQUIRED_DOC_SECTIONS:
        assert section in text, f"Missing section '{section}' in {doc_file}"

    assert source_file in text, f"Missing source file marker '{source_file}' in {doc_file}"


def _assert_manifest_updates(repo_root: Path) -> None:
    manifest_path = repo_root / "tutorials" / "per-file" / "file-manifest.md"
    assert manifest_path.exists(), "Missing tutorials/per-file/file-manifest.md"

    manifest_text = manifest_path.read_text(encoding="utf-8")
    mapping: dict[str, tuple[str, str, str]] = {}
    for line in manifest_text.splitlines():
        match = ROW_RE.match(line)
        if not match:
            continue
        source = _normalize_cell(match.group(2))
        extension = match.group(3).strip()
        status = match.group(4).strip()
        doc = _normalize_cell(match.group(5))
        mapping[source] = (extension, status, doc)

    for source_file, doc_file in REQUIRED_MANUAL_DOCS.items():
        assert source_file in mapping, f"Manifest row missing source file: {source_file}"
        assert mapping[source_file] == (".py", "done", doc_file), (
            "Manifest row mismatch for S19.1 scope: "
            f"expected ('.py', 'done', '{doc_file}'), got {mapping[source_file]}"
        )


def main() -> None:
    repo_root = Path(__file__).resolve().parents[2]

    for source_file, doc_file in REQUIRED_MANUAL_DOCS.items():
        _assert_doc_contract(repo_root, source_file, doc_file)

    _assert_manifest_updates(repo_root)

    index_text = _read(repo_root, "tutorials/per-file/INDEX.md")
    assert "S19.0" in index_text, "Per-file index should preserve S19.0 baseline context"

    print("Task 722 manual bootstrap coverage checks passed.")


if __name__ == "__main__":
    main()
