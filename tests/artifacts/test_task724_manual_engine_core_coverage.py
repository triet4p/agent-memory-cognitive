from __future__ import annotations

from pathlib import Path


REQUIRED_MANUAL_DOCS = {
    "cogmem_api/engine/__init__.py": "tutorials/per-file/engine-core--cogmem-api-engine-init.md",
    "cogmem_api/engine/memory_engine.py": "tutorials/per-file/engine-core--cogmem-api-engine-memory-engine.md",
    "cogmem_api/engine/db_utils.py": "tutorials/per-file/engine-core--cogmem-api-engine-db-utils.md",
    "cogmem_api/engine/embeddings.py": "tutorials/per-file/engine-core--cogmem-api-engine-embeddings.md",
    "cogmem_api/engine/cross_encoder.py": "tutorials/per-file/engine-core--cogmem-api-engine-cross-encoder.md",
    "cogmem_api/engine/llm_wrapper.py": "tutorials/per-file/engine-core--cogmem-api-engine-llm-wrapper.md",
    "cogmem_api/engine/response_models.py": "tutorials/per-file/engine-core--cogmem-api-engine-response-models.md",
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
    assert doc_path.exists(), f"Missing manual engine-core tutorial: {doc_file}"

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
            "Manifest row mismatch for S19.3 scope: "
            f"expected fragment '{expected_row_fragment}'"
        )


def main() -> None:
    repo_root = Path(__file__).resolve().parents[2]

    for source_file, doc_file in REQUIRED_MANUAL_DOCS.items():
        _assert_doc_contract(repo_root, source_file, doc_file)

    _assert_manifest_updates(repo_root)

    print("Task 724 manual engine-core coverage checks passed.")


if __name__ == "__main__":
    main()
