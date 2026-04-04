from __future__ import annotations

from pathlib import Path


def _assert_contains_in_order(text: str, chunks: list[str]) -> None:
    current = -1
    for chunk in chunks:
        idx = text.find(chunk)
        assert idx != -1, f"Missing expected chunk: {chunk}"
        assert idx > current, f"Chunk out of order: {chunk}"
        current = idx


def assert_module_map_contract(module_map_text: str) -> None:
    required_headings = [
        "## Layer 0 - System Overview",
        "## Layer 1 - End-to-end Flows",
        "## Layer 2 - Module Catalog",
        "## Layer 3 - Function Inventory Seed",
    ]
    for heading in required_headings:
        assert heading in module_map_text, f"Missing heading: {heading}"

    _assert_contains_in_order(module_map_text, required_headings)

    required_module_markers = [
        "cogmem_api/main.py",
        "cogmem_api/api/http.py",
        "cogmem_api/engine/retain/",
        "cogmem_api/engine/search/",
        "cogmem_api/engine/reflect/",
    ]
    for marker in required_module_markers:
        assert marker in module_map_text, f"Missing module marker: {marker}"


def assert_learning_path_contract(learning_path_text: str) -> None:
    required_sections = [
        "## Thứ tự đọc đề xuất",
        "## Checklist hoàn tất S16.1",
        "## Verify commands",
    ]
    for section in required_sections:
        assert section in learning_path_text, f"Missing section: {section}"

    expected_order = [
        "Layer 0 - Architecture overview",
        "Layer 1 - End-to-end flow map",
        "Layer 2 - Module catalog",
        "Layer 3 - Function inventory seed",
        "Chuyển tiếp sang S17/S18",
    ]
    _assert_contains_in_order(learning_path_text, expected_order)

    assert "Architecture -> Module -> Function" in learning_path_text


def assert_template_contract(template_text: str) -> None:
    required_headings = [
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
    for heading in required_headings:
        assert heading in template_text, f"Missing template heading: {heading}"

    _assert_contains_in_order(template_text, required_headings)


def assert_no_legacy_roadmap_labels(*texts: str) -> None:
    forbidden = [
        "tutorial core",
        "tutorial non-core",
        "core/non-core",
        "module core",
        "module non-core",
        "Sprint S17 - Tutorial Core",
        "Sprint S18 - Tutorial Non-core + Capstone",
    ]
    merged = "\n".join(texts).lower()
    found = [term for term in forbidden if term.lower() in merged]
    assert not found, f"Legacy tutorial roadmap labels still present: {found}"


def main() -> None:
    repo_root = Path(__file__).resolve().parents[2]
    module_map_path = repo_root / "tutorials" / "module-map.md"
    learning_path = repo_root / "tutorials" / "learning-path.md"
    template_path = repo_root / "tutorials" / "templates" / "function-property-template.md"
    tutorial_readme = repo_root / "tutorials" / "README.md"
    tutorial_index = repo_root / "tutorials" / "INDEX.md"
    plan_path = repo_root / "docs" / "PLAN.md"

    assert module_map_path.exists(), "Missing tutorials/module-map.md"
    assert learning_path.exists(), "Missing tutorials/learning-path.md"
    assert template_path.exists(), "Missing tutorials/templates/function-property-template.md"
    assert tutorial_readme.exists(), "Missing tutorials/README.md"
    assert tutorial_index.exists(), "Missing tutorials/INDEX.md"
    assert plan_path.exists(), "Missing docs/PLAN.md"

    module_map_text = module_map_path.read_text(encoding="utf-8")
    learning_path_text = learning_path.read_text(encoding="utf-8")
    template_text = template_path.read_text(encoding="utf-8")
    tutorial_readme_text = tutorial_readme.read_text(encoding="utf-8")
    tutorial_index_text = tutorial_index.read_text(encoding="utf-8")
    plan_text = plan_path.read_text(encoding="utf-8")

    assert_module_map_contract(module_map_text)
    assert_learning_path_contract(learning_path_text)
    assert_template_contract(template_text)
    assert_no_legacy_roadmap_labels(
        tutorial_readme_text,
        tutorial_index_text,
        learning_path_text,
        plan_text,
    )

    print("Task 716 tutorial framework contract checks passed.")


if __name__ == "__main__":
    main()
