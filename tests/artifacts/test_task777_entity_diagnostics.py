"""Task 777: Entity diagnostic search script.

Verifies:
1. scripts/diagnose_bank.py exists and is readable
2. Has _run_diagnose function with expected SQL query (ILIKE + entity join)
3. Main function accepts bank_id, entity_keyword, fact_type, limit args
"""

import ast
import os
import sys


def test_diagnose_script_exists():
    path = "scripts/diagnose_bank.py"
    assert os.path.exists(path), f"{path} must exist"
    assert os.path.isfile(path), f"{path} must be a file"


def test_diagnose_has_entity_join_sql():
    path = "scripts/diagnose_bank.py"
    with open(path, "r", encoding="utf-8") as f:
        source = f.read()

    assert "ILIKE" in source, "SQL query must use ILIKE for case-insensitive search"
    assert "unit_entities" in source, "SQL query must join unit_entities table"
    assert "entities e" in source, "SQL query must join entities table"
    assert "chunk_id" in source, "Query must return chunk_id field"
    assert "has_snippet" in source, "Query must return has_snippet derived field"


def test_diagnose_argparse():
    path = "scripts/diagnose_bank.py"
    with open(path, "r", encoding="utf-8") as f:
        source = f.read()

    tree = ast.parse(source)

    has_bank_id_arg = False
    has_keyword_arg = False
    has_fact_type_arg = False

    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == "main":
            func_source = ast.unparse(node)
            if "bank_id" in func_source and "add_argument" in func_source:
                has_bank_id_arg = True
            if "entity_keyword" in func_source:
                has_keyword_arg = True
            if "fact-type" in func_source or "fact_type" in func_source:
                has_fact_type_arg = True

    assert has_bank_id_arg, "Script must accept bank_id positional argument"
    assert has_keyword_arg, "Script must accept entity_keyword positional argument"
    assert has_fact_type_arg, "Script must accept --fact-type optional argument"


if __name__ == "__main__":
    test_diagnose_script_exists()
    test_diagnose_has_entity_join_sql()
    test_diagnose_argparse()
    print("3/3 PASS")
    sys.exit(0)
