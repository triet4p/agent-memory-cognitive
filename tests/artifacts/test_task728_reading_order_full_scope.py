from __future__ import annotations

import re
from pathlib import Path


CATALOG_ROW_RE = re.compile(r"^\|\s*(\d+)\s*\|\s*([^|]+?)\s*\|\s*([^|]+?)\s*\|\s*$")
MANIFEST_ROW_RE = re.compile(r"^\|\s*(\d+)\s*\|\s*([^|]+?)\s*\|\s*([^|]+?)\s*\|\s*([^|]+?)\s*\|\s*([^|]+?)\s*\|\s*$")
IDS_LINE_RE = re.compile(r"^(?:[-*]\s*)?(ONBOARDING_IDS|DEBUG_FIRST_IDS):\s*(.+)$", re.MULTILINE)


def _parse_ids(raw: str) -> list[int]:
    return [int(token.strip()) for token in raw.split(",") if token.strip()]


def _load_manifest_mapping(manifest_text: str) -> dict[int, tuple[str, str]]:
    mapping: dict[int, tuple[str, str]] = {}
    for line in manifest_text.splitlines():
        match = MANIFEST_ROW_RE.match(line)
        if not match:
            continue

        row_id = int(match.group(1))
        source_file = match.group(2).strip()
        status = match.group(4).strip()
        tutorial_doc = match.group(5).strip()

        assert status == "done", f"Manifest row {row_id} is not done: {status}"
        mapping[row_id] = (source_file, tutorial_doc)

    return mapping


def _load_catalog_mapping(reading_order_text: str) -> dict[int, tuple[str, str]]:
    mapping: dict[int, tuple[str, str]] = {}
    for line in reading_order_text.splitlines():
        match = CATALOG_ROW_RE.match(line)
        if not match:
            continue

        row_id = int(match.group(1))
        source_file = match.group(2).strip()
        tutorial_doc = match.group(3).strip()
        mapping[row_id] = (source_file, tutorial_doc)

    return mapping


def main() -> None:
    repo_root = Path(__file__).resolve().parents[2]

    reading_order_path = repo_root / "tutorials" / "per-file" / "READING-ORDER.md"
    tutorials_index_path = repo_root / "tutorials" / "INDEX.md"
    learning_path_path = repo_root / "tutorials" / "learning-path.md"
    manifest_path = repo_root / "tutorials" / "per-file" / "file-manifest.md"

    assert reading_order_path.exists(), "Missing tutorials/per-file/READING-ORDER.md"
    assert tutorials_index_path.exists(), "Missing tutorials/INDEX.md"
    assert learning_path_path.exists(), "Missing tutorials/learning-path.md"
    assert manifest_path.exists(), "Missing tutorials/per-file/file-manifest.md"

    reading_order_text = reading_order_path.read_text(encoding="utf-8")
    tutorials_index_text = tutorials_index_path.read_text(encoding="utf-8")
    learning_path_text = learning_path_path.read_text(encoding="utf-8")
    manifest_text = manifest_path.read_text(encoding="utf-8")

    for section in (
        "## Canonical catalog IDs",
        "## Onboarding path",
        "## Debug-first path",
    ):
        assert section in reading_order_text, f"Missing section {section} in READING-ORDER.md"

    catalog_mapping = _load_catalog_mapping(reading_order_text)
    assert len(catalog_mapping) == 58, f"Catalog rows mismatch: expected 58, got {len(catalog_mapping)}"
    assert sorted(catalog_mapping) == list(range(1, 59)), "Catalog IDs must be 1..58"

    manifest_mapping = _load_manifest_mapping(manifest_text)
    assert len(manifest_mapping) == 58, f"Manifest rows mismatch: expected 58, got {len(manifest_mapping)}"

    for row_id in range(1, 59):
        assert row_id in manifest_mapping, f"Missing manifest row id {row_id}"
        assert row_id in catalog_mapping, f"Missing catalog row id {row_id}"
        assert catalog_mapping[row_id] == manifest_mapping[row_id], (
            f"Catalog row {row_id} mismatch: "
            f"reading-order={catalog_mapping[row_id]} manifest={manifest_mapping[row_id]}"
        )

    ids_matches = dict(IDS_LINE_RE.findall(reading_order_text))
    assert "ONBOARDING_IDS" in ids_matches, "Missing ONBOARDING_IDS line"
    assert "DEBUG_FIRST_IDS" in ids_matches, "Missing DEBUG_FIRST_IDS line"

    onboarding_ids = _parse_ids(ids_matches["ONBOARDING_IDS"])
    debug_first_ids = _parse_ids(ids_matches["DEBUG_FIRST_IDS"])

    assert onboarding_ids == list(range(1, 59)), "ONBOARDING_IDS must be strict 1..58"
    assert len(debug_first_ids) == 58, "DEBUG_FIRST_IDS must contain 58 IDs"
    assert sorted(debug_first_ids) == list(range(1, 59)), "DEBUG_FIRST_IDS must cover 1..58 exactly once"

    assert "tutorials/per-file/READING-ORDER.md" in tutorials_index_text, (
        "tutorials/INDEX.md must reference tutorials/per-file/READING-ORDER.md"
    )
    assert "tutorials/per-file/READING-ORDER.md" in learning_path_text, (
        "tutorials/learning-path.md must reference tutorials/per-file/READING-ORDER.md"
    )

    print("Task 728 reading order full-scope checks passed.")


if __name__ == "__main__":
    main()
