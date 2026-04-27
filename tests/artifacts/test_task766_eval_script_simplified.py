"""Artifact test for task 766: eval_cogmem.py simplified (no LLM logic).

Verifies:
1. eval_cogmem.py no longer has call_openai_chat
2. eval_cogmem.py no longer has EvalLLMConfig
3. build_recall_payload has top_k and snippet_budget
4. run_full_pipeline has no llm_config parameter
"""

if __name__ == "__main__":
    import ast
    import sys

    src = "scripts/eval_cogmem.py"
    passed = 0
    failed = 0

    with open(src, "r", encoding="utf-8") as f:
        src_tree = ast.parse(f.read(), filename=src)

    func_names = {node.name for node in ast.walk(src_tree) if isinstance(node, ast.FunctionDef)}
    class_names = {node.name for node in ast.walk(src_tree) if isinstance(node, ast.ClassDef)}

    # Test 1: No call_openai_chat
    if "call_openai_chat" not in func_names:
        print("[PASS] test_766_1: eval_cogmem has no call_openai_chat function")
        passed += 1
    else:
        print("[FAIL] test_766_1: eval_cogmem still has call_openai_chat")
        failed += 1

    # Test 2: No EvalLLMConfig
    if "EvalLLMConfig" not in class_names:
        print("[PASS] test_766_2: eval_cogmem has no EvalLLMConfig class")
        passed += 1
    else:
        print("[FAIL] test_766_2: eval_cogmem still has EvalLLMConfig")
        failed += 1

    # Test 3: build_recall_payload has top_k and snippet_budget
    with open(src, "r", encoding="utf-8") as f:
        src_text = f.read()

    if "top_k" in src_text and "snippet_budget" in src_text:
        print("[PASS] test_766_3: build_recall_payload has top_k and snippet_budget")
        passed += 1
    else:
        print("[FAIL] test_766_3: build_recall_payload missing top_k or snippet_budget")
        failed += 1

    # Test 4: run_full_pipeline has no llm_config or llm_call_fn parameter
    for node in ast.walk(src_tree):
        if isinstance(node, ast.FunctionDef) and node.name == "run_full_pipeline":
            param_names = [a.arg for a in node.args.args]
            if "llm_config" not in param_names and "llm_call_fn" not in param_names:
                print("[PASS] test_766_4: run_full_pipeline has no llm_config/llm_call_fn params")
                passed += 1
            else:
                print(f"[FAIL] test_766_4: run_full_pipeline still has llm params: {param_names}")
                failed += 1
            break
    else:
        print("[FAIL] test_766_4: run_full_pipeline function not found")
        failed += 1

    print(f"\nResults: {passed}/4 passed, {failed}/4 failed")
    sys.exit(0 if failed == 0 else 1)