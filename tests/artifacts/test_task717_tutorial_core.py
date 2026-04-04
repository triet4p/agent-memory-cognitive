from __future__ import annotations

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

MODULE_DOSSIERS = [
    "tutorials/modules/runtime-and-api.md",
    "tutorials/modules/config-and-schema.md",
    "tutorials/modules/engine-core-services.md",
    "tutorials/modules/adapters-llm-embeddings-reranker.md",
    "tutorials/modules/retain-pipeline.md",
    "tutorials/modules/search-pipeline.md",
    "tutorials/modules/reflect-pipeline.md",
]


def _assert_contains_in_order(text: str, chunks: list[str]) -> None:
    cursor = -1
    for chunk in chunks:
        idx = text.find(chunk)
        assert idx != -1, f"Missing expected section: {chunk}"
        assert idx > cursor, f"Section order mismatch: {chunk}"
        cursor = idx


def assert_flow_doc_contract(flow_text: str) -> None:
    for heading in REQUIRED_HEADINGS:
        assert heading in flow_text, f"Missing heading in flow doc: {heading}"

    _assert_contains_in_order(flow_text, REQUIRED_HEADINGS)

    required_flow_markers = [
        "retain_memories",
        "recall_memories",
        "retain_batch_async",
        "recall_async",
        "retain_batch",
        "retrieve_all_fact_types_parallel",
        "fuse_parallel_results",
        "synthesize_lazy_reflect",
        "flowchart TD",
    ]
    for marker in required_flow_markers:
        assert marker in flow_text, f"Missing flow marker: {marker}"


def assert_module_dossier_contract(dossier_text: str, dossier_path: str) -> None:
    for heading in REQUIRED_HEADINGS:
        assert heading in dossier_text, f"Missing heading {heading} in {dossier_path}"
    _assert_contains_in_order(dossier_text, REQUIRED_HEADINGS)


def collect_cogmem_modules(repo_root: Path) -> list[str]:
    module_paths: list[str] = []
    for path in sorted((repo_root / "cogmem_api").rglob("*.py")):
        rel = path.relative_to(repo_root).as_posix()
        if rel.startswith("cogmem_api/alembic/versions/"):
            continue
        if "__pycache__" in rel:
            continue
        module_paths.append(rel)
    return module_paths


def main() -> None:
    repo_root = Path(__file__).resolve().parents[2]

    flow_doc = repo_root / "tutorials" / "flows" / "retain-recall-reflect-response.md"
    index_doc = repo_root / "tutorials" / "INDEX.md"
    learning_path_doc = repo_root / "tutorials" / "learning-path.md"
    modules_index_doc = repo_root / "tutorials" / "modules" / "README.md"

    assert flow_doc.exists(), "Missing tutorials/flows/retain-recall-reflect-response.md"
    assert index_doc.exists(), "Missing tutorials/INDEX.md"
    assert learning_path_doc.exists(), "Missing tutorials/learning-path.md"
    assert modules_index_doc.exists(), "Missing tutorials/modules/README.md"

    flow_text = flow_doc.read_text(encoding="utf-8")
    index_text = index_doc.read_text(encoding="utf-8")
    learning_path_text = learning_path_doc.read_text(encoding="utf-8")
    modules_index_text = modules_index_doc.read_text(encoding="utf-8")

    assert_flow_doc_contract(flow_text)

    assert "tutorials/flows/retain-recall-reflect-response.md" in index_text
    assert "tutorials/flows/retain-recall-reflect-response.md" in learning_path_text
    assert "tutorials/modules/README.md" in index_text
    assert "tutorials/modules/README.md" in learning_path_text

    dossier_texts: list[str] = []
    for dossier in MODULE_DOSSIERS:
        dossier_path = repo_root / dossier
        assert dossier_path.exists(), f"Missing module dossier: {dossier}"
        text = dossier_path.read_text(encoding="utf-8")
        assert_module_dossier_contract(text, dossier)
        assert dossier in modules_index_text, f"Missing dossier entry in modules index: {dossier}"
        dossier_texts.append(text)

    merged_dossiers = "\n".join(dossier_texts)
    for module_path in collect_cogmem_modules(repo_root):
        assert module_path in merged_dossiers, f"Module not mapped in S17.2 dossiers: {module_path}"

    print("Task 717 tutorial core checks passed (S17.1 + S17.2 scope).")


if __name__ == "__main__":
    main()