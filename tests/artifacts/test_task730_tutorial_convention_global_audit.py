from __future__ import annotations

import ast
import json
import re
from pathlib import Path


LOG_FILE_PATTERN = re.compile(r"^task_(\d{3})_summary\.md$")
TEST_FILE_PATTERN = re.compile(r"^test_task(\d{3})_[a-z0-9_]+\.py$")
FORBIDDEN_IMPORT_PATTERN = re.compile(r"^\s*(from\s+hindsight_api\b|import\s+hindsight_api\b)", re.MULTILINE)

REQUIRED_LOG_SECTIONS = [
    "## Scope",
    "## Outputs Created",
    "## Verification Strategy Applied",
]

REQUIRED_DOC_SECTIONS = [
    "## Purpose",
    "## Source File",
    "## Symbol-by-symbol explanation",
    "## Cross-file dependencies (inbound/outbound)",
    "## Runtime implications/side effects",
    "## Failure modes",
    "## Verify commands",
]

MANIFEST_ROW_RE = re.compile(
    r"^\|\s*(\d+)\s*\|\s*([^|]+?)\s*\|\s*(\.[a-z0-9]+)\s*\|\s*(not-started|in-progress|done)\s*\|\s*([^|]+?)\s*\|$"
)

ALLOWED_EXTENSIONS = {".py", ".sh", ".ps1"}


def _collect_scope_files(repo_root: Path) -> list[str]:
    files: list[str] = []
    for root_name in ("cogmem_api", "scripts", "docker"):
        root = repo_root / root_name
        assert root.exists(), f"Missing scope root: {root_name}"
        for path in root.rglob("*"):
            if path.is_file() and path.suffix.lower() in ALLOWED_EXTENSIONS:
                files.append(path.relative_to(repo_root).as_posix())
    return sorted(files)


def _parse_manifest_rows(manifest_text: str) -> list[tuple[int, str, str, str, str]]:
    rows: list[tuple[int, str, str, str, str]] = []
    for line in manifest_text.splitlines():
        match = MANIFEST_ROW_RE.match(line)
        if not match:
            continue
        rows.append(
            (
                int(match.group(1)),
                match.group(2).strip(),
                match.group(3).strip(),
                match.group(4).strip(),
                match.group(5).strip(),
            )
        )
    return rows


def _collect_python_symbols(source_path: Path) -> tuple[list[str], list[str], list[str]]:
    tree = ast.parse(source_path.read_text(encoding="utf-8"), filename=source_path.as_posix())

    variables: list[str] = []
    functions_and_methods: list[str] = []
    classes: list[str] = []

    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            functions_and_methods.append(node.name)
            continue

        if isinstance(node, ast.ClassDef):
            classes.append(node.name)
            for child in node.body:
                if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    functions_and_methods.append(child.name)
            continue

        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name):
                    name = target.id
                    if name.isupper() or name in {"__all__", "JsonDict"}:
                        variables.append(name)
            continue

        if isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name):
            name = node.target.id
            if name.isupper() or name in {"__all__", "JsonDict"}:
                variables.append(name)

    def _unique(seq: list[str]) -> list[str]:
        seen: set[str] = set()
        out: list[str] = []
        for item in seq:
            if item in seen:
                continue
            seen.add(item)
            out.append(item)
        return out

    return _unique(variables), _unique(functions_and_methods), _unique(classes)


def _collect_shell_symbols(source_path: Path) -> tuple[list[str], list[str]]:
    variables: list[str] = []
    functions: list[str] = []

    for line in source_path.read_text(encoding="utf-8", errors="ignore").splitlines():
        stripped = line.strip()

        match_var = re.match(r"^([A-Za-z_][A-Za-z0-9_]*)=", stripped)
        if match_var:
            variables.append(match_var.group(1))

        match_func = re.match(r"^([A-Za-z_][A-Za-z0-9_]*)\s*\(\)\s*\{", stripped)
        if match_func:
            functions.append(match_func.group(1))

    return sorted(set(variables), key=variables.index), sorted(set(functions), key=functions.index)


def _collect_ps_symbols(source_path: Path) -> tuple[list[str], list[str], list[str]]:
    variables: list[str] = []
    functions: list[str] = []
    classes: list[str] = []

    for line in source_path.read_text(encoding="utf-8", errors="ignore").splitlines():
        stripped = line.strip()

        match_var = re.match(r"^\$([A-Za-z_][A-Za-z0-9_]*)\s*=\s*", stripped)
        if match_var:
            variables.append("$" + match_var.group(1))

        match_func = re.match(r"^function\s+([A-Za-z_][A-Za-z0-9_-]*)\b", stripped, re.IGNORECASE)
        if match_func:
            functions.append(match_func.group(1))

        match_class = re.match(r"^class\s+([A-Za-z_][A-Za-z0-9_]*)\b", stripped, re.IGNORECASE)
        if match_class:
            classes.append(match_class.group(1))

    return (
        sorted(set(variables), key=variables.index),
        sorted(set(functions), key=functions.index),
        sorted(set(classes), key=classes.index),
    )


def _assert_symbol_coverage(
    source_file: str,
    extension: str,
    per_file_doc_text: str,
    function_doc_text: str | None,
    repo_root: Path,
) -> None:
    source_path = repo_root / source_file
    assert source_path.exists(), f"Missing source file in scope: {source_file}"

    searchable_text = per_file_doc_text + "\n" + (function_doc_text or "")

    if extension == ".py":
        variables, functions, classes = _collect_python_symbols(source_path)

        for symbol in variables:
            assert symbol in per_file_doc_text, (
                f"Missing variable symbol '{symbol}' in per-file tutorial for {source_file}"
            )

        for symbol in functions:
            assert symbol in searchable_text, (
                f"Missing function symbol '{symbol}' in tutorials for {source_file}"
            )

        for symbol in classes:
            assert symbol in searchable_text, (
                f"Missing class symbol '{symbol}' in tutorials for {source_file}"
            )

        return

    if extension == ".sh":
        variables, functions = _collect_shell_symbols(source_path)
        for symbol in variables + functions:
            assert symbol in per_file_doc_text, (
                f"Missing shell symbol '{symbol}' in per-file tutorial for {source_file}"
            )
        return

    if extension == ".ps1":
        variables, functions, classes = _collect_ps_symbols(source_path)
        for symbol in variables + functions + classes:
            assert symbol in per_file_doc_text, (
                f"Missing PowerShell symbol '{symbol}' in per-file tutorial for {source_file}"
            )
        return

    raise AssertionError(f"Unsupported extension for symbol audit: {extension}")


def _assert_artifact_conventions(repo_root: Path) -> None:
    logs_dir = repo_root / "logs"
    artifacts_dir = repo_root / "tests" / "artifacts"

    assert logs_dir.exists() and logs_dir.is_dir(), "Missing logs directory"
    assert artifacts_dir.exists() and artifacts_dir.is_dir(), "Missing tests/artifacts directory"

    log_files = [path for path in logs_dir.iterdir() if path.is_file()]
    test_files = [path for path in artifacts_dir.iterdir() if path.is_file()]

    invalid_logs = [path.name for path in log_files if not LOG_FILE_PATTERN.match(path.name)]
    invalid_tests = [path.name for path in test_files if not TEST_FILE_PATTERN.match(path.name)]

    assert not invalid_logs, f"Invalid log file names: {invalid_logs}"
    assert not invalid_tests, f"Invalid artifact test names: {invalid_tests}"

    log_ids: set[str] = set()
    for path in log_files:
        match = LOG_FILE_PATTERN.match(path.name)
        if not match:
            continue
        log_ids.add(match.group(1))

        content = path.read_text(encoding="utf-8")
        missing_sections = [section for section in REQUIRED_LOG_SECTIONS if section not in content]
        assert not missing_sections, f"{path.name} is missing sections: {missing_sections}"

    test_ids: set[str] = set()
    for path in test_files:
        match = TEST_FILE_PATTERN.match(path.name)
        if not match:
            continue
        test_ids.add(match.group(1))

        content = path.read_text(encoding="utf-8")
        assert not FORBIDDEN_IMPORT_PATTERN.search(content), (
            f"Forbidden hindsight_api import in artifact test: {path.name}"
        )

    assert log_ids == test_ids, (
        f"Task pairing mismatch: logs_only={sorted(log_ids - test_ids)}, tests_only={sorted(test_ids - log_ids)}"
    )


def main() -> None:
    repo_root = Path(__file__).resolve().parents[2]

    manifest_path = repo_root / "tutorials" / "per-file" / "file-manifest.md"
    function_doc_index_path = repo_root / "tutorials" / "functions" / "function-doc-index.json"

    assert manifest_path.exists(), "Missing tutorials/per-file/file-manifest.md"
    assert function_doc_index_path.exists(), "Missing tutorials/functions/function-doc-index.json"

    manifest_text = manifest_path.read_text(encoding="utf-8")
    rows = _parse_manifest_rows(manifest_text)
    assert rows, "Manifest table has no parseable rows"

    row_ids = [row[0] for row in rows]
    assert row_ids == list(range(1, len(rows) + 1)), "Manifest row IDs must be contiguous"

    expected_scope = _collect_scope_files(repo_root)
    manifest_sources = [row[1] for row in rows]
    assert sorted(manifest_sources) == expected_scope, "Manifest sources mismatch workspace scope"

    function_doc_index = json.loads(function_doc_index_path.read_text(encoding="utf-8"))
    function_doc_map: dict[str, str] = {
        str(item["module"]): str(item["doc"])
        for item in function_doc_index
    }

    for _, source_file, extension, status, tutorial_doc in rows:
        assert status == "done", f"Final convention gate requires status=done for {source_file}"
        assert tutorial_doc != "TBD", f"Tutorial doc must not be TBD for {source_file}"
        assert tutorial_doc.startswith("tutorials/per-file/"), (
            f"Canonical tutorial must live under tutorials/per-file: {tutorial_doc}"
        )
        assert not tutorial_doc.startswith("tutorials/functions/"), (
            f"tutorials/functions is not canonical per-file explanation: {tutorial_doc}"
        )

        source_path = repo_root / source_file
        tutorial_path = repo_root / tutorial_doc

        assert source_path.exists(), f"Missing source file: {source_file}"
        assert tutorial_path.exists(), f"Missing tutorial file: {tutorial_doc}"
        assert source_path.suffix.lower() == extension, (
            f"Extension mismatch for source {source_file}: manifest={extension} actual={source_path.suffix.lower()}"
        )

        tutorial_text = tutorial_path.read_text(encoding="utf-8")
        for section in REQUIRED_DOC_SECTIONS:
            assert section in tutorial_text, f"Missing section '{section}' in {tutorial_doc}"
        assert source_file in tutorial_text, f"Missing source marker '{source_file}' in {tutorial_doc}"

        function_doc_text: str | None = None
        function_doc_rel = function_doc_map.get(source_file)
        if function_doc_rel:
            function_doc_path = repo_root / function_doc_rel
            assert function_doc_path.exists(), f"Missing function deep-dive doc: {function_doc_rel}"
            function_doc_text = function_doc_path.read_text(encoding="utf-8")

        _assert_symbol_coverage(
            source_file=source_file,
            extension=extension,
            per_file_doc_text=tutorial_text,
            function_doc_text=function_doc_text,
            repo_root=repo_root,
        )

    _assert_artifact_conventions(repo_root)

    print("Task 730 tutorial convention global audit passed.")


if __name__ == "__main__":
    main()
