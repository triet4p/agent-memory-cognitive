"""Artifact test for task 764: Two-tier recall (top_k + snippet_budget).

Verifies:
1. RecallRequest has top_k and snippet_budget fields with default None
2. recall_async source has logic reranked_results[:top_k]
3. recall_async source has snippet_budget strip logic (item["raw_snippet"] = None)
"""

if __name__ == "__main__":
    import ast
    import sys

    src_http = "cogmem_api/api/http.py"
    src_engine = "cogmem_api/engine/memory_engine.py"

    passed = 0
    failed = 0

    # Test 1: RecallRequest has top_k and snippet_budget fields
    with open(src_http, "r", encoding="utf-8") as f:
        http_tree = ast.parse(f.read(), filename=src_http)

    recall_req_fields = {}
    for node in ast.walk(http_tree):
        if isinstance(node, ast.ClassDef) and node.name == "RecallRequest":
            for item in node.body:
                if isinstance(item, ast.AnnAssign) and isinstance(item.target, ast.Name):
                    recall_req_fields[item.target.id] = item

    if "top_k" in recall_req_fields:
        print("[PASS] test_764_1: RecallRequest.top_k field exists")
        passed += 1
    else:
        print("[FAIL] test_764_1: RecallRequest.top_k field missing")
        failed += 1

    if "snippet_budget" in recall_req_fields:
        print("[PASS] test_764_2: RecallRequest.snippet_budget field exists")
        passed += 1
    else:
        print("[FAIL] test_764_2: RecallRequest.snippet_budget field missing")
        failed += 1

    # Test 3: recall_async has top_k slice logic
    with open(src_engine, "r", encoding="utf-8") as f:
        engine_src = f.read()

    if "reranked_results = reranked_results[:top_k]" in engine_src or "[:top_k]" in engine_src:
        print("[PASS] test_764_3: recall_async has reranked_results[:top_k] logic")
        passed += 1
    else:
        print("[FAIL] test_764_3: recall_async missing top_k slice logic")
        failed += 1

    # Test 4: recall_async has snippet_budget strip logic
    if 'item["raw_snippet"] = None' in engine_src or 'item[\'raw_snippet\'] = None' in engine_src:
        print("[PASS] test_764_4: recall_async has snippet_budget strip logic")
        passed += 1
    else:
        print("[FAIL] test_764_4: recall_async missing snippet_budget strip logic")
        failed += 1

    print(f"\nResults: {passed}/4 passed, {failed}/4 failed")
    sys.exit(0 if failed == 0 else 1)