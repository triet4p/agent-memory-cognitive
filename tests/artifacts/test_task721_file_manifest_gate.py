from __future__ import annotations

import re
from pathlib import Path


ALLOWED_EXTENSIONS = {".py", ".sh", ".ps1"}
ALLOWED_STATUSES = {"not-started", "in-progress", "done"}
ROW_PATTERN = re.compile(
    r"^\|\s*(\d+)\s*\|\s*([^|]+?)\s*\|\s*(\.[a-z0-9]+)\s*\|\s*(not-started|in-progress|done)\s*\|\s*([^|]+?)\s*\|$"
)
LINK_CELL_PATTERN = re.compile(r"^\[([^\]]+)\]\([^\)]+\)$")


def _normalize_cell(value: str) -> str:
    raw = value.strip()
    match = LINK_CELL_PATTERN.match(raw)
    if match:
        return match.group(1).strip()
    return raw


def _collect_scope_files(repo_root: Path) -> list[str]:
    files: list[str] = []
    for root_name in ("cogmem_api", "scripts", "docker"):
        root = repo_root / root_name
        assert root.exists(), f"Missing scope root: {root_name}"
        for path in root.rglob("*"):
            if path.is_file() and path.suffix.lower() in ALLOWED_EXTENSIONS:
                files.append(path.relative_to(repo_root).as_posix())
    return sorted(files)


def _parse_manifest_rows(manifest_text: str) -> list[tuple[int, str, str, str]]:
    rows: list[tuple[int, str, str, str]] = []
    for line in manifest_text.splitlines():
        match = ROW_PATTERN.match(line)
        if not match:
            continue
        index = int(match.group(1))
        file_path = _normalize_cell(match.group(2))
        extension = match.group(3)
        status = match.group(4)
        rows.append((index, file_path, extension, status))
    return rows


def main() -> None:
    repo_root = Path(__file__).resolve().parents[2]

    index_file = repo_root / "tutorials" / "per-file" / "INDEX.md"
    manifest_file = repo_root / "tutorials" / "per-file" / "file-manifest.md"

    assert index_file.exists(), "Missing tutorials/per-file/INDEX.md"
    assert manifest_file.exists(), "Missing tutorials/per-file/file-manifest.md"

    index_text = index_file.read_text(encoding="utf-8")
    manifest_text = manifest_file.read_text(encoding="utf-8")

    required_scope_markers = [
        "cogmem_api/**",
        "scripts/**",
        "docker/**",
        "tests/artifacts/**",
        ".py",
        ".sh",
        ".ps1",
    ]
    for marker in required_scope_markers:
        assert marker in manifest_text, f"Missing scope marker in manifest: {marker}"

    assert "file-manifest.md" in index_text, "INDEX must link to file-manifest.md"
    assert "not-started" in index_text
    assert "in-progress" in index_text
    assert "done" in index_text

    manifest_rows = _parse_manifest_rows(manifest_text)
    assert manifest_rows, "Manifest table has no parseable rows"

    indices = [row[0] for row in manifest_rows]
    assert indices == list(range(1, len(manifest_rows) + 1)), "Manifest row indices must be contiguous from 1"

    manifest_paths = [row[1] for row in manifest_rows]
    manifest_extensions = [row[2] for row in manifest_rows]
    manifest_statuses = [row[3] for row in manifest_rows]

    assert len(set(manifest_paths)) == len(manifest_paths), "Duplicate file path entries in manifest"
    assert all(ext in ALLOWED_EXTENSIONS for ext in manifest_extensions), "Unexpected file extension in manifest"
    assert all(status in ALLOWED_STATUSES for status in manifest_statuses), "Unexpected coverage status in manifest"
    assert all(not path.startswith("tests/artifacts/") for path in manifest_paths), "tests/artifacts must be excluded"

    expected_paths = _collect_scope_files(repo_root)
    expected_set = set(expected_paths)
    manifest_set = set(manifest_paths)

    missing_paths = sorted(expected_set - manifest_set)
    extra_paths = sorted(manifest_set - expected_set)

    assert not missing_paths, f"Manifest is missing scoped files: {missing_paths}"
    assert not extra_paths, f"Manifest contains files outside scope: {extra_paths}"
    assert len(manifest_rows) == len(expected_paths), "Manifest file count mismatch against workspace scope"

    print("Task 721 file manifest gate checks passed.")


if __name__ == "__main__":
    main()
