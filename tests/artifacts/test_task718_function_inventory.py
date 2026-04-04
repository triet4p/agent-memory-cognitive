from __future__ import annotations

import ast
import json
from dataclasses import dataclass
from pathlib import Path


REQUIRED_HEADINGS = [
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


@dataclass(frozen=True)
class EntryKey:
    module: str
    owner: str
    function: str
    line: int


def _assert_contains_in_order(text: str, chunks: list[str]) -> None:
    cursor = -1
    for chunk in chunks:
        idx = text.find(chunk)
        assert idx != -1, f"Missing expected section: {chunk}"
        assert idx > cursor, f"Section order mismatch: {chunk}"
        cursor = idx


def _visibility_of(name: str) -> str:
    return "private" if name.startswith("_") else "public"


def _signature_of(node: ast.FunctionDef | ast.AsyncFunctionDef) -> str:
    args = ast.unparse(node.args)
    signature = f"{node.name}({args})"
    if node.returns is not None:
        signature = f"{signature} -> {ast.unparse(node.returns)}"
    if isinstance(node, ast.AsyncFunctionDef):
        signature = f"async {signature}"
    return signature


def collect_source_entries(repo_root: Path) -> dict[EntryKey, dict[str, str]]:
    source_entries: dict[EntryKey, dict[str, str]] = {}
    code_root = repo_root / "cogmem_api"

    for path in sorted(code_root.rglob("*.py")):
        rel = path.relative_to(repo_root).as_posix()
        if rel.startswith("cogmem_api/alembic/versions/"):
            continue
        if "__pycache__" in rel:
            continue

        tree = ast.parse(path.read_text(encoding="utf-8"), filename=rel)

        for node in tree.body:
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                key = EntryKey(module=rel, owner="(module)", function=node.name, line=node.lineno)
                source_entries[key] = {
                    "signature": _signature_of(node),
                    "visibility": _visibility_of(node.name),
                    "location": f"{rel}:{node.lineno}",
                }
                continue

            if not isinstance(node, ast.ClassDef):
                continue

            for child in node.body:
                if not isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    continue
                key = EntryKey(module=rel, owner=node.name, function=child.name, line=child.lineno)
                source_entries[key] = {
                    "signature": _signature_of(child),
                    "visibility": _visibility_of(child.name),
                    "location": f"{rel}:{child.lineno}",
                }

    return source_entries


def assert_inventory_docs_contract(repo_root: Path) -> None:
    inventory_md = repo_root / "tutorials" / "functions" / "function-inventory.md"
    index_doc = repo_root / "tutorials" / "INDEX.md"
    learning_path = repo_root / "tutorials" / "learning-path.md"
    module_map = repo_root / "tutorials" / "module-map.md"

    assert inventory_md.exists(), "Missing tutorials/functions/function-inventory.md"
    assert index_doc.exists(), "Missing tutorials/INDEX.md"
    assert learning_path.exists(), "Missing tutorials/learning-path.md"
    assert module_map.exists(), "Missing tutorials/module-map.md"

    inventory_md_text = inventory_md.read_text(encoding="utf-8")
    index_text = index_doc.read_text(encoding="utf-8")
    learning_path_text = learning_path.read_text(encoding="utf-8")
    module_map_text = module_map.read_text(encoding="utf-8")

    for heading in REQUIRED_HEADINGS:
        assert heading in inventory_md_text, f"Missing heading in inventory doc: {heading}"

    _assert_contains_in_order(inventory_md_text, REQUIRED_HEADINGS)

    assert "### Module coverage summary" in inventory_md_text
    assert "### Detailed function inventory" in inventory_md_text
    assert "tutorials/functions/function-inventory.md" in index_text
    assert "tutorials/functions/function-inventory.md" in learning_path_text
    assert "tutorials/functions/function-inventory.md" in module_map_text


def assert_inventory_json_matches_source(repo_root: Path) -> None:
    inventory_json = repo_root / "tutorials" / "functions" / "function-inventory.json"
    assert inventory_json.exists(), "Missing tutorials/functions/function-inventory.json"

    payload = json.loads(inventory_json.read_text(encoding="utf-8"))
    assert isinstance(payload, list), "Inventory JSON must be a list"
    assert payload, "Inventory JSON must not be empty"

    source_entries = collect_source_entries(repo_root)

    actual_entries: dict[EntryKey, dict[str, str]] = {}
    for item in payload:
        for required in [
            "module",
            "owner",
            "function",
            "signature",
            "visibility",
            "line",
            "location",
            "inventory_status",
            "deep_dive_status",
        ]:
            assert required in item, f"Missing key '{required}' in inventory item: {item}"

        key = EntryKey(
            module=item["module"],
            owner=item["owner"],
            function=item["function"],
            line=item["line"],
        )
        assert key not in actual_entries, f"Duplicate inventory key found: {key}"

        actual_entries[key] = {
            "signature": item["signature"],
            "visibility": item["visibility"],
            "location": item["location"],
            "inventory_status": item["inventory_status"],
            "deep_dive_status": item["deep_dive_status"],
        }

    expected_keys = set(source_entries.keys())
    actual_keys = set(actual_entries.keys())

    missing = sorted(expected_keys - actual_keys, key=lambda k: (k.module, k.owner, k.line, k.function))
    unexpected = sorted(actual_keys - expected_keys, key=lambda k: (k.module, k.owner, k.line, k.function))

    assert not missing, f"Functions missing from inventory: {missing}"
    assert not unexpected, f"Inventory has functions not in source: {unexpected}"

    for key in sorted(expected_keys, key=lambda k: (k.module, k.owner, k.line, k.function)):
        expected = source_entries[key]
        actual = actual_entries[key]

        assert actual["signature"] == expected["signature"], f"Signature mismatch for {key}"
        assert actual["visibility"] == expected["visibility"], f"Visibility mismatch for {key}"
        assert actual["location"] == expected["location"], f"Location mismatch for {key}"
        assert actual["inventory_status"] == "mapped", f"Unexpected inventory_status for {key}"
        assert actual["deep_dive_status"] in {"pending", "documented"}, (
            f"Unexpected deep_dive_status for {key}: {actual['deep_dive_status']}"
        )


def main() -> None:
    repo_root = Path(__file__).resolve().parents[2]
    assert_inventory_docs_contract(repo_root)
    assert_inventory_json_matches_source(repo_root)
    print("Task 718 S18.1 function inventory checks passed.")


if __name__ == "__main__":
    main()
