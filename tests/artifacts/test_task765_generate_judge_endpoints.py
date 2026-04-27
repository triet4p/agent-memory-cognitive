"""Artifact test for task 765: Generate + Judge endpoints.

Verifies:
1. GenerateRequest, GenerateResponse schemas exist in http.py
2. JudgeRequest, JudgeResponse schemas exist in http.py
3. cogmem_api/engine/eval_helpers.py has build_generation_prompt and build_judge_system_prompt
"""

if __name__ == "__main__":
    import ast
    import sys

    passed = 0
    failed = 0

    # Test 1 & 2: Check GenerateRequest, GenerateResponse, JudgeRequest, JudgeResponse in http.py
    with open("cogmem_api/api/http.py", "r", encoding="utf-8") as f:
        http_tree = ast.parse(f.read(), filename="cogmem_api/api/http.py")

    class_names = {node.name for node in ast.walk(http_tree) if isinstance(node, ast.ClassDef)}

    for cls_name, label in [
        ("GenerateRequest", "GenerateRequest"),
        ("GenerateResponse", "GenerateResponse"),
        ("JudgeRequest", "JudgeRequest"),
        ("JudgeResponse", "JudgeResponse"),
    ]:
        if cls_name in class_names:
            print(f"[PASS] test_765_{cls_name}: {cls_name} schema exists")
            passed += 1
        else:
            print(f"[FAIL] test_765_{cls_name}: {cls_name} schema missing")
            failed += 1

    # Test 3: eval_helpers has build_generation_prompt and build_judge_system_prompt
    with open("cogmem_api/engine/eval_helpers.py", "r", encoding="utf-8") as f:
        helpers_src = f.read()

    for fn_name in ["build_generation_prompt", "build_judge_system_prompt"]:
        if f"def {fn_name}" in helpers_src:
            print(f"[PASS] test_765_{fn_name}: {fn_name} exists in eval_helpers")
            passed += 1
        else:
            print(f"[FAIL] test_765_{fn_name}: {fn_name} missing from eval_helpers")
            failed += 1

    # Test 4: eval_helpers has parse_judge_response
    if "def parse_judge_response" in helpers_src:
        print("[PASS] test_765_parse_judge_response: parse_judge_response exists")
        passed += 1
    else:
        print("[FAIL] test_765_parse_judge_response: parse_judge_response missing")
        failed += 1

    print(f"\nResults: {passed}/6 passed, {failed}/6 failed")
    sys.exit(0 if failed == 0 else 1)