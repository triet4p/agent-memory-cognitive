"""Artifact test for task 767: S24.5 master test runner.

Runs all S24.5 artifact tests (764, 765, 766) in one pass.
Exit code 0 only if ALL tests from ALL sub-sprints pass.
"""

if __name__ == "__main__":
    import subprocess
    import sys

    tests = [
        ("tests/artifacts/test_task764_recall_top_k.py", "764"),
        ("tests/artifacts/test_task765_generate_judge_endpoints.py", "765"),
        ("tests/artifacts/test_task766_eval_script_simplified.py", "766"),
    ]

    total_pass = 0
    total_fail = 0

    for test_path, task_id in tests:
        print(f"\n{'='*60}")
        print(f"Running S24.5 task {task_id} tests: {test_path}")
        print("=" * 60)
        result = subprocess.run(
            [sys.executable, test_path],
            capture_output=False,
        )
        if result.returncode == 0:
            total_pass += 1
            print(f"[OK] Task {task_id} tests PASSED")
        else:
            total_fail += 1
            print(f"[FAIL] Task {task_id} tests FAILED (exit {result.returncode})")

    print(f"\n{'='*60}")
    print(f"S24.5 Master Runner: {total_pass}/{len(tests)} passed, {total_fail}/{len(tests)} failed")
    print("=" * 60)
    sys.exit(0 if total_fail == 0 else 1)