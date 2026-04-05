from __future__ import annotations

import json
import re
from pathlib import Path


def _load_manifest_docs(manifest_text: str) -> list[str]:
    row_re = re.compile(r"^\|\s*(\d+)\s*\|\s*([^|]+?)\s*\|\s*(\.[a-z0-9]+)\s*\|\s*([^|]+?)\s*\|\s*([^|]+?)\s*\|$")
    docs: list[str] = []
    for line in manifest_text.splitlines():
        match = row_re.match(line)
        if not match:
            continue
        doc_path = match.group(5).strip()
        if doc_path.startswith("tutorials/"):
            doc_path = doc_path[len("tutorials/"):]
        docs.append(doc_path)
    return docs


def main() -> None:
    repo_root = Path(__file__).resolve().parents[2]

    mkdocs_path = repo_root / "mkdocs.yml"
    manifest_path = repo_root / "tutorials" / "per-file" / "file-manifest.md"
    function_doc_index_path = repo_root / "tutorials" / "functions" / "function-doc-index.json"

    assert mkdocs_path.exists(), "Missing mkdocs.yml"
    assert manifest_path.exists(), "Missing tutorials/per-file/file-manifest.md"
    assert function_doc_index_path.exists(), "Missing tutorials/functions/function-doc-index.json"

    mkdocs_text = mkdocs_path.read_text(encoding="utf-8")
    manifest_text = manifest_path.read_text(encoding="utf-8")
    function_doc_index = json.loads(function_doc_index_path.read_text(encoding="utf-8"))

    assert "- Functions:" in mkdocs_text, "mkdocs nav must include Functions section"
    assert "- Per-file:" in mkdocs_text, "mkdocs nav must include Per-file section"
    assert "navigation.expand" in mkdocs_text, "mkdocs theme should expand nested navigation"

    per_file_docs = _load_manifest_docs(manifest_text)
    assert per_file_docs, "Manifest docs list must not be empty"

    for doc in per_file_docs:
        assert (doc in mkdocs_text) or (f"tutorials/{doc}" in mkdocs_text), (
            f"Per-file doc missing from mkdocs nav: {doc}"
        )

    function_docs = []
    for item in function_doc_index:
        doc = str(item["doc"])
        if doc.startswith("tutorials/"):
            doc = doc[len("tutorials/"):]
        function_docs.append(doc)

    assert function_docs, "Function docs list must not be empty"
    for doc in function_docs:
        assert (doc in mkdocs_text) or (f"tutorials/{doc}" in mkdocs_text), (
            f"Function deep-dive doc missing from mkdocs nav: {doc}"
        )

    print("Task 732 tutorials detailed navigation checks passed.")


if __name__ == "__main__":
    main()
