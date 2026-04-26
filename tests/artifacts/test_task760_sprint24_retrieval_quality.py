"""Task 760 artifact tests: Combined verification for Sprint S24 retrieval quality.

Runs all sub-task tests: migration (758), code adaptations (759.1-759.4).
This is the master test file that verifies the full sprint deliverables.
"""

from __future__ import annotations

import os
import subprocess
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))


TESTS = {
    "758-migration": "tests/artifacts/test_task758_migration.py",
    "759.1-bm25": "tests/artifacts/test_task7591_bm25_search_vector.py",
    "759.2-ef_search": "tests/artifacts/test_task7592_ef_search.py",
    "759.3-tags": "tests/artifacts/test_task7593_document_tags.py",
    "759.4-dead_code": "tests/artifacts/test_task7594_flat_query_analyzer.py",
}


def _main() -> None:
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    os.chdir(base_dir)

    results = {}
    for name, rel_path in TESTS.items():
        path = os.path.join(base_dir, rel_path)
        print(f"\n{'='*60}")
        print(f"Running: {name} ({rel_path})")
        print("=" * 60)
        result = subprocess.run(
            [sys.executable, path],
            capture_output=False,
        )
        results[name] = result.returncode == 0
        print(f"Result: {'PASS' if results[name] else 'FAIL'}")

    print(f"\n{'='*60}")
    print("SUMMARY")
    print("=" * 60)
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    print(f"Results: {passed}/{total} passed")

    failed = [k for k, v in results.items() if not v]
    if failed:
        print(f"FAILED: {', '.join(failed)}")
        sys.exit(1)

    print("ALL TESTS PASSED")


if __name__ == "__main__":
    _main()
