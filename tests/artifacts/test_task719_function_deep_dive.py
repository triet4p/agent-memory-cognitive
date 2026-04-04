from __future__ import annotations

import json
from pathlib import Path


REQUIRED_DOC_HEADINGS = [
    "## Purpose",
    "## Inputs",
    "## Outputs",
    "## Top-down level",
    "## Prerequisites",
    "## Module responsibility",
    "## Function inventory (public/private)",
    "## Failure modes",
    "## Verify commands",
]

REQUIRED_FUNCTION_MARKERS = [
    "- Purpose:",
    "- Inputs:",
    "- Outputs:",
    "- Side effects:",
    "- Dependency calls:",
    "- Failure modes:",
    "- Pre-conditions:",
    "- Post-conditions:",
    "- Verify command:",
]


def _assert_contains_in_order(text: str, chunks: list[str]) -> None:
    cursor = -1
    for chunk in chunks:
        idx = text.find(chunk)
        assert idx != -1, f"Missing expected section: {chunk}"
        assert idx > cursor, f"Section order mismatch: {chunk}"
        cursor = idx


def _split_function_sections(doc_text: str) -> dict[str, str]:
    sections: dict[str, str] = {}
    marker = "### Function: "
    parts = doc_text.split(marker)
    for part in parts[1:]:
        title_line, _, body = part.partition("\n")
        sections[title_line.strip()] = body
    return sections


def assert_tutorial_navigation(repo_root: Path) -> None:
    index_doc = repo_root / "tutorials" / "INDEX.md"
    learning_path = repo_root / "tutorials" / "learning-path.md"
    module_map = repo_root / "tutorials" / "module-map.md"
    functions_index = repo_root / "tutorials" / "functions" / "README.md"

    for path in [index_doc, learning_path, module_map, functions_index]:
        assert path.exists(), f"Missing tutorial navigation doc: {path}"

    index_text = index_doc.read_text(encoding="utf-8")
    learning_path_text = learning_path.read_text(encoding="utf-8")
    module_map_text = module_map.read_text(encoding="utf-8")
    functions_index_text = functions_index.read_text(encoding="utf-8")

    assert "tutorials/functions/README.md" in index_text
    assert "tutorials/functions/function-doc-index.json" in index_text
    assert "tutorials/functions/README.md" in learning_path_text
    assert "tests/artifacts/test_task719_function_deep_dive.py" in learning_path_text
    assert "tests/artifacts/test_task719_function_deep_dive.py" in module_map_text
    assert "test_task719_function_deep_dive.py" in functions_index_text


def assert_function_docs_contract(repo_root: Path) -> None:
    inventory_path = repo_root / "tutorials" / "functions" / "function-inventory.json"
    doc_index_path = repo_root / "tutorials" / "functions" / "function-doc-index.json"

    assert inventory_path.exists(), "Missing tutorials/functions/function-inventory.json"
    assert doc_index_path.exists(), "Missing tutorials/functions/function-doc-index.json"

    inventory = json.loads(inventory_path.read_text(encoding="utf-8"))
    doc_index = json.loads(doc_index_path.read_text(encoding="utf-8"))

    assert isinstance(inventory, list) and inventory, "Inventory payload must be non-empty list"
    assert isinstance(doc_index, list) and doc_index, "Doc index payload must be non-empty list"

    for item in inventory:
        assert item.get("deep_dive_status") == "documented", (
            f"Expected deep_dive_status=documented, got {item.get('deep_dive_status')} for {item}"
        )

    by_module: dict[str, list[dict]] = {}
    for item in inventory:
        by_module.setdefault(item["module"], []).append(item)

    indexed_modules = {entry["module"] for entry in doc_index}
    expected_modules = set(by_module.keys())
    assert indexed_modules == expected_modules, (
        f"Doc index modules mismatch. expected={sorted(expected_modules)} actual={sorted(indexed_modules)}"
    )

    for entry in doc_index:
        module = entry["module"]
        doc_rel = entry["doc"]
        expected_count = entry["function_count"]
        module_items = sorted(by_module[module], key=lambda x: (x["owner"], x["line"], x["function"]))

        assert expected_count == len(module_items), (
            f"Function count mismatch for module={module}: index={expected_count}, inventory={len(module_items)}"
        )

        doc_path = repo_root / doc_rel
        assert doc_path.exists(), f"Missing deep-dive doc: {doc_rel}"

        text = doc_path.read_text(encoding="utf-8")
        for heading in REQUIRED_DOC_HEADINGS:
            assert heading in text, f"Missing heading {heading} in {doc_rel}"
        _assert_contains_in_order(text, REQUIRED_DOC_HEADINGS)

        sections = _split_function_sections(text)
        assert len(sections) == len(module_items), (
            f"Function section count mismatch in {doc_rel}: sections={len(sections)} expected={len(module_items)}"
        )

        for item in module_items:
            section_key = f"{item['owner']}.{item['function']}"
            assert section_key in sections, f"Missing section {section_key} in {doc_rel}"
            section = sections[section_key]

            for marker in REQUIRED_FUNCTION_MARKERS:
                assert marker in section, f"Missing marker {marker} in section {section_key} ({doc_rel})"

            assert item["signature"] in section, f"Missing signature in section {section_key} ({doc_rel})"
            assert item["location"] in section, f"Missing location in section {section_key} ({doc_rel})"


def main() -> None:
    repo_root = Path(__file__).resolve().parents[2]
    assert_tutorial_navigation(repo_root)
    assert_function_docs_contract(repo_root)
    print("Task 719 S18.2 function deep-dive checks passed.")


if __name__ == "__main__":
    main()
