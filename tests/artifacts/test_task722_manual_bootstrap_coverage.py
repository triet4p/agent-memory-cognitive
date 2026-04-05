from __future__ import annotations

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

    for source_file, doc_file in REQUIRED_MANUAL_DOCS.items():
        expected_row_fragment = f"| {source_file} | .py | done | {doc_file} |"
        assert expected_row_fragment in manifest_text, (
            "Manifest row mismatch for S19.1 scope: "
            f"expected fragment '{expected_row_fragment}'"
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
