from __future__ import annotations

from pathlib import Path


REQUIRED_MANUAL_DOCS = {
    "cogmem_api/api/__init__.py": "tutorials/per-file/api--cogmem-api-api-init.md",
    "cogmem_api/api/http.py": "tutorials/per-file/api--cogmem-api-api-http.md",
    "cogmem_api/models.py": "tutorials/per-file/schema--cogmem-api-models.md",
    "cogmem_api/alembic/versions/20260330_0001_t1_2_schema_extensions.py": "tutorials/per-file/schema--cogmem-api-alembic-t1-2-schema-extensions.md",
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


def _assert_doc_contract(repo_root: Path, source_file: str, doc_file: str) -> None:
    doc_path = repo_root / doc_file
    assert doc_path.exists(), f"Missing manual API/schema tutorial: {doc_file}"

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
            "Manifest row mismatch for S19.2 scope: "
            f"expected fragment '{expected_row_fragment}'"
        )


def main() -> None:
    repo_root = Path(__file__).resolve().parents[2]

    for source_file, doc_file in REQUIRED_MANUAL_DOCS.items():
        _assert_doc_contract(repo_root, source_file, doc_file)

    _assert_manifest_updates(repo_root)

    print("Task 723 manual API/schema coverage checks passed.")


if __name__ == "__main__":
    main()
