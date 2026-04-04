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


def main() -> None:
    repo_root = Path(__file__).resolve().parents[2]

    flow_doc = repo_root / "tutorials" / "flows" / "retain-recall-reflect-response.md"
    index_doc = repo_root / "tutorials" / "INDEX.md"
    learning_path_doc = repo_root / "tutorials" / "learning-path.md"

    assert flow_doc.exists(), "Missing tutorials/flows/retain-recall-reflect-response.md"
    assert index_doc.exists(), "Missing tutorials/INDEX.md"
    assert learning_path_doc.exists(), "Missing tutorials/learning-path.md"

    flow_text = flow_doc.read_text(encoding="utf-8")
    index_text = index_doc.read_text(encoding="utf-8")
    learning_path_text = learning_path_doc.read_text(encoding="utf-8")

    assert_flow_doc_contract(flow_text)

    assert "tutorials/flows/retain-recall-reflect-response.md" in index_text
    assert "tutorials/flows/retain-recall-reflect-response.md" in learning_path_text

    print("Task 717 tutorial core flow checks passed (S17.1 scope).")


if __name__ == "__main__":
    main()