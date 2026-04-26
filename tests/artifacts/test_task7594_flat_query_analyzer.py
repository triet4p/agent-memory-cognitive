"""Task 759.4 artifact tests: FlatQueryAnalyzer dead code removed.

Verification that FlatQueryAnalyzer.analyze() no longer has unreachable
return None after return QueryAnalysis.
"""

from __future__ import annotations

import ast
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))


def test_flat_query_analyzer_no_dead_code() -> None:
    """FlatQueryAnalyzer.analyze() has no unreachable return None after QueryAnalysis."""
    import cogmem_api.engine.query_analyzer as qa_mod

    source = open(qa_mod.__file__, encoding="utf-8").read()

    tree = ast.parse(source)
    flat_class = None
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == "FlatQueryAnalyzer":
            flat_class = node
            break

    assert flat_class is not None, "FlatQueryAnalyzer class not found"
    analyze_method = next(
        (n for n in flat_class.body if isinstance(n, ast.FunctionDef) and n.name == "analyze"),
        None,
    )
    assert analyze_method is not None, "analyze() method not found in FlatQueryAnalyzer"

    method_source = ast.unparse(analyze_method)
    lines = [l.strip() for l in method_source.splitlines() if l.strip()]

    return_lines = [i for i, line in enumerate(lines) if line.startswith("return QueryAnalysis")]
    assert return_lines, "No return QueryAnalysis found in FlatQueryAnalyzer.analyze()"

    last_return_idx = return_lines[-1]
    if last_return_idx + 1 < len(lines):
        next_line = lines[last_return_idx + 1]
        assert not next_line.startswith("return None"), \
            f"Dead code found: 'return None' immediately follows QueryAnalysis return"

    print("PASS: test_flat_query_analyzer_no_dead_code")


def _main() -> None:
    tests = [test_flat_query_analyzer_no_dead_code]
    passed = 0
    failed = 0
    for test in tests:
        try:
            test()
            passed += 1
        except Exception as exc:
            print(f"FAIL: {test.__name__}: {exc}")
            failed += 1
    print(f"\nResults: {passed}/1 passed")
    if failed:
        print(f"FAILED: {failed} test(s)")
        sys.exit(1)
    print("ALL TESTS PASSED")


if __name__ == "__main__":
    _main()
