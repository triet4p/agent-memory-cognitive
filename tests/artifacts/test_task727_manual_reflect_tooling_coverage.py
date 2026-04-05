from __future__ import annotations

import re
from pathlib import Path


REQUIRED_MANUAL_DOCS = {
    "cogmem_api/engine/reflect/__init__.py": "tutorials/per-file/reflect--cogmem-api-engine-reflect-init.md",
    "cogmem_api/engine/reflect/agent.py": "tutorials/per-file/reflect--cogmem-api-engine-reflect-agent.md",
    "cogmem_api/engine/reflect/models.py": "tutorials/per-file/reflect--cogmem-api-engine-reflect-models.md",
    "cogmem_api/engine/reflect/prompts.py": "tutorials/per-file/reflect--cogmem-api-engine-reflect-prompts.md",
    "cogmem_api/engine/reflect/tools.py": "tutorials/per-file/reflect--cogmem-api-engine-reflect-tools.md",
    "scripts/ablation_runner.py": "tutorials/per-file/tooling--scripts-ablation-runner.md",
    "scripts/distill_dataset.py": "tutorials/per-file/tooling--scripts-distill-dataset.md",
    "scripts/eval_cogmem.py": "tutorials/per-file/tooling--scripts-eval-cogmem.md",
    "scripts/test_hindsight.py": "tutorials/per-file/tooling--scripts-test-hindsight.md",
    "scripts/docker.sh": "tutorials/per-file/tooling--scripts-docker-sh.md",
    "scripts/docker.ps1": "tutorials/per-file/tooling--scripts-docker-ps1.md",
    "scripts/run_hindsight.ps1": "tutorials/per-file/tooling--scripts-run-hindsight-ps1.md",
    "scripts/smoke-test-cogmem.ps1": "tutorials/per-file/tooling--scripts-smoke-test-cogmem-ps1.md",
    "scripts/smoke-test-cogmem.sh": "tutorials/per-file/tooling--scripts-smoke-test-cogmem-sh.md",
    "docker/test-image.sh": "tutorials/per-file/docker--docker-test-image-sh.md",
    "docker/test-image.ps1": "tutorials/per-file/docker--docker-test-image-ps1.md",
    "docker/standalone/start-all.sh": "tutorials/per-file/docker--docker-standalone-start-all-sh.md",
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
    assert doc_path.exists(), f"Missing manual reflect/tooling tutorial: {doc_file}"

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

    extension_by_source = {
        source_file: Path(source_file).suffix
        for source_file in REQUIRED_MANUAL_DOCS
    }

    for source_file, doc_file in REQUIRED_MANUAL_DOCS.items():
        assert source_file in mapping, f"Manifest row missing source file: {source_file}"
        expected = (extension_by_source[source_file], "done", doc_file)
        assert mapping[source_file] == expected, (
            "Manifest row mismatch for S19.6 scope: "
            f"expected {expected}, got {mapping[source_file]}"
        )


def main() -> None:
    repo_root = Path(__file__).resolve().parents[2]

    for source_file, doc_file in REQUIRED_MANUAL_DOCS.items():
        _assert_doc_contract(repo_root, source_file, doc_file)

    _assert_manifest_updates(repo_root)

    print("Task 727 manual reflect/tooling coverage checks passed.")


if __name__ == "__main__":
    main()
