from __future__ import annotations

import re
from pathlib import Path


def parse_check_constraint_values(pattern: str, source_text: str) -> list[str]:
    match = re.search(pattern, source_text)
    if not match:
        return []
    raw_values = match.group(1)
    return [v.strip().strip("'") for v in raw_values.split(",")]


def assert_required_files_exist(repo_root: Path) -> None:
    required_files = [
        repo_root / "AGENTS.md",
        repo_root / "docs" / "CogMem-Idea.md",
        repo_root / "docs" / "PLAN.md",
        repo_root / "hindsight_api" / "models.py",
        repo_root / "hindsight_api" / "engine" / "retain" / "orchestrator.py",
        repo_root / "hindsight_api" / "engine" / "search" / "retrieval.py",
        repo_root / "cogmem_api" / "__init__.py",
    ]
    missing = [str(path.relative_to(repo_root)) for path in required_files if not path.exists()]
    assert not missing, f"Missing required files: {missing}"


def assert_hindsight_schema_baseline(repo_root: Path) -> None:
    models_path = repo_root / "hindsight_api" / "models.py"
    source_text = models_path.read_text(encoding="utf-8")

    fact_types = parse_check_constraint_values(
        r"fact_type\s+IN\s*\(([^)]+)\)",
        source_text,
    )
    expected_fact_types = ["world", "experience", "opinion", "observation"]
    assert fact_types == expected_fact_types, (
        "Unexpected baseline fact_type values. "
        f"Expected {expected_fact_types}, got {fact_types}"
    )

    link_types = parse_check_constraint_values(
        r"link_type\s+IN\s*\(([^)]+)\)",
        source_text,
    )
    expected_link_types = ["temporal", "semantic", "entity", "causes", "caused_by", "enables", "prevents"]
    assert link_types == expected_link_types, (
        "Unexpected baseline link_type values. "
        f"Expected {expected_link_types}, got {link_types}"
    )

    assert "raw_snippet" not in source_text, "Baseline schema already contains raw_snippet; T1.2 assumption is invalid"


def assert_no_hindsight_imports_in_cogmem(repo_root: Path) -> None:
    cogmem_root = repo_root / "cogmem_api"
    py_files = list(cogmem_root.rglob("*.py"))
    bad_imports: list[str] = []

    pattern = re.compile(r"^\s*(from\s+hindsight_api\b|import\s+hindsight_api\b)", re.MULTILINE)

    for py_file in py_files:
        content = py_file.read_text(encoding="utf-8")
        if pattern.search(content):
            bad_imports.append(str(py_file.relative_to(repo_root)))

    assert not bad_imports, f"Found forbidden hindsight_api imports in cogmem_api: {bad_imports}"


def main() -> None:
    repo_root = Path(__file__).resolve().parents[2]

    assert_required_files_exist(repo_root)
    assert_hindsight_schema_baseline(repo_root)
    assert_no_hindsight_imports_in_cogmem(repo_root)

    print("Task 001 inventory check passed.")


if __name__ == "__main__":
    main()
