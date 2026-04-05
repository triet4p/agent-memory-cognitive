from __future__ import annotations

import re
from pathlib import Path


REQUIRED_MANUAL_DOCS = {
    "cogmem_api/engine/retain/__init__.py": "tutorials/per-file/retain--cogmem-api-engine-retain-init.md",
    "cogmem_api/engine/retain/types.py": "tutorials/per-file/retain--cogmem-api-engine-retain-types.md",
    "cogmem_api/engine/retain/orchestrator.py": "tutorials/per-file/retain--cogmem-api-engine-retain-orchestrator.md",
    "cogmem_api/engine/retain/fact_extraction.py": "tutorials/per-file/retain--cogmem-api-engine-retain-fact-extraction.md",
    "cogmem_api/engine/retain/fact_storage.py": "tutorials/per-file/retain--cogmem-api-engine-retain-fact-storage.md",
    "cogmem_api/engine/retain/entity_processing.py": "tutorials/per-file/retain--cogmem-api-engine-retain-entity-processing.md",
    "cogmem_api/engine/retain/link_creation.py": "tutorials/per-file/retain--cogmem-api-engine-retain-link-creation.md",
    "cogmem_api/engine/retain/link_utils.py": "tutorials/per-file/retain--cogmem-api-engine-retain-link-utils.md",
    "cogmem_api/engine/retain/embedding_processing.py": "tutorials/per-file/retain--cogmem-api-engine-retain-embedding-processing.md",
    "cogmem_api/engine/retain/embedding_utils.py": "tutorials/per-file/retain--cogmem-api-engine-retain-embedding-utils.md",
    "cogmem_api/engine/retain/chunk_storage.py": "tutorials/per-file/retain--cogmem-api-engine-retain-chunk-storage.md",
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


def _assert_doc_contract(repo_root: Path, source_file: str, doc_file: str) -> None:
    doc_path = repo_root / doc_file
    assert doc_path.exists(), f"Missing manual retain tutorial: {doc_file}"

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
            "Manifest row mismatch for S19.4 scope: "
            f"expected ('.py', 'done', '{doc_file}'), got {mapping[source_file]}"
        )


def main() -> None:
    repo_root = Path(__file__).resolve().parents[2]

    for source_file, doc_file in REQUIRED_MANUAL_DOCS.items():
        _assert_doc_contract(repo_root, source_file, doc_file)

    _assert_manifest_updates(repo_root)

    print("Task 725 manual retain coverage checks passed.")


if __name__ == "__main__":
    main()
