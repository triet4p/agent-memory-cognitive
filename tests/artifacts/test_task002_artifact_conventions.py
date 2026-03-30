from __future__ import annotations

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


def list_matching_ids(files: list[Path], pattern: re.Pattern[str]) -> set[str]:
    ids: set[str] = set()
    for file in files:
        match = pattern.match(file.name)
        if match:
            ids.add(match.group(1))
    return ids


def assert_required_directories(repo_root: Path) -> tuple[Path, Path]:
    logs_dir = repo_root / "logs"
    artifacts_dir = repo_root / "tests" / "artifacts"

    assert logs_dir.exists() and logs_dir.is_dir(), "Missing logs directory"
    assert artifacts_dir.exists() and artifacts_dir.is_dir(), "Missing tests/artifacts directory"
    return logs_dir, artifacts_dir


def assert_log_and_test_naming(logs_dir: Path, artifacts_dir: Path) -> tuple[set[str], set[str]]:
    log_files = [path for path in logs_dir.iterdir() if path.is_file()]
    test_files = [path for path in artifacts_dir.iterdir() if path.is_file()]

    invalid_logs = [path.name for path in log_files if not LOG_FILE_PATTERN.match(path.name)]
    invalid_tests = [path.name for path in test_files if not TEST_FILE_PATTERN.match(path.name)]

    assert not invalid_logs, f"Invalid log file names: {invalid_logs}"
    assert not invalid_tests, f"Invalid artifact test names: {invalid_tests}"

    log_ids = list_matching_ids(log_files, LOG_FILE_PATTERN)
    test_ids = list_matching_ids(test_files, TEST_FILE_PATTERN)

    assert log_ids, "No task log files found"
    assert test_ids, "No task artifact tests found"

    return log_ids, test_ids


def assert_log_structure(logs_dir: Path) -> None:
    for log_file in logs_dir.iterdir():
        if not log_file.is_file() or not LOG_FILE_PATTERN.match(log_file.name):
            continue
        content = log_file.read_text(encoding="utf-8")
        missing_sections = [section for section in REQUIRED_LOG_SECTIONS if section not in content]
        assert not missing_sections, f"{log_file.name} is missing sections: {missing_sections}"


def assert_task_pairing(log_ids: set[str], test_ids: set[str]) -> None:
    missing_test_for_log = sorted(log_ids - test_ids)
    missing_log_for_test = sorted(test_ids - log_ids)

    assert not missing_test_for_log, f"Missing artifact test files for task IDs: {missing_test_for_log}"
    assert not missing_log_for_test, f"Missing task summary logs for task IDs: {missing_log_for_test}"


def assert_artifact_tests_are_isolated(artifacts_dir: Path) -> None:
    violating_files: list[str] = []
    for test_file in artifacts_dir.iterdir():
        if not test_file.is_file() or not TEST_FILE_PATTERN.match(test_file.name):
            continue
        content = test_file.read_text(encoding="utf-8")
        if FORBIDDEN_IMPORT_PATTERN.search(content):
            violating_files.append(test_file.name)

    assert not violating_files, f"Forbidden hindsight_api imports in artifact tests: {violating_files}"


def main() -> None:
    repo_root = Path(__file__).resolve().parents[2]

    logs_dir, artifacts_dir = assert_required_directories(repo_root)
    log_ids, test_ids = assert_log_and_test_naming(logs_dir, artifacts_dir)
    assert_log_structure(logs_dir)
    assert_task_pairing(log_ids, test_ids)
    assert_artifact_tests_are_isolated(artifacts_dir)

    print("Task 002 artifact convention check passed.")


if __name__ == "__main__":
    main()
