from __future__ import annotations

import re
from pathlib import Path


def assert_required_files_exist(repo_root: Path) -> None:
    required_files = [
        repo_root / "AGENTS.md",
        repo_root / "docs" / "CogMem-Idea.md",
        repo_root / "docs" / "PLAN.md",
        repo_root / "cogmem_api" / "__init__.py",
    ]
    missing = [str(path.relative_to(repo_root)) for path in required_files if not path.exists()]
    assert not missing, f"Missing required files: {missing}"


def assert_hindsight_directory_removed(repo_root: Path) -> None:
    assert not (repo_root / "hindsight_api").exists(), "hindsight_api directory must be removed in delete-first baseline"


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
    assert_hindsight_directory_removed(repo_root)
    assert_no_hindsight_imports_in_cogmem(repo_root)

    print("Task 001 inventory check passed for post-S11 baseline.")


if __name__ == "__main__":
    main()
