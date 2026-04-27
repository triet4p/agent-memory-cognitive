"""Task 769: Enable cross-encoder reranker + fix reranker_used tracking.

Verifies:
1. RecallResult in http.py has cross_encoder_score field
2. memory_engine.py result dict has cross_encoder_score key
3. eval_cogmem.py uses cross_encoder_ok from trace (not cross_encoder_score from results)
"""

import ast
import sys


def test_recall_result_has_cross_encoder_score():
    path = "cogmem_api/api/http.py"
    with open(path, "r", encoding="utf-8") as f:
        source = f.read()

    tree = ast.parse(source)

    found = False
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == "RecallResult":
            for item in node.body:
                if isinstance(item, ast.AnnAssign) and getattr(item.target, "id", None) == "cross_encoder_score":
                    found = True
                    break

    assert found, "RecallResult.cross_encoder_score not found in http.py"


def test_memory_engine_result_dict_has_cross_encoder_score():
    path = "cogmem_api/engine/memory_engine.py"
    with open(path, "r", encoding="utf-8") as f:
        source = f.read()

    assert '"cross_encoder_score": float(scored_result.cross_encoder_score)' in source, (
        "cross_encoder_score not added to result dict in memory_engine.py"
    )


def test_eval_script_uses_trace_cross_encoder_ok():
    path = "scripts/eval_cogmem.py"
    with open(path, "r", encoding="utf-8") as f:
        source = f.read()

    assert 'cross_encoder_ok' in source, (
        "eval_cogmem.py should check trace.cross_encoder_ok for reranker_used"
    )

    assert '.get("cross_encoder_score", 0)' not in source, (
        "eval_cogmem.py should not check cross_encoder_score from results "
        "— reranker_used must come from trace.cross_encoder_ok"
    )


if __name__ == "__main__":
    test_recall_result_has_cross_encoder_score()
    test_memory_engine_result_dict_has_cross_encoder_score()
    test_eval_script_uses_trace_cross_encoder_ok()
    print("3/3 PASS")
    sys.exit(0)