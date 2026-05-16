"""Sprint S29 G-5 artifact test — cross-session semantic link cap.

Run:  uv run python tests/artifacts/test_s29_g5_semantic_cap.py
"""
from __future__ import annotations

import sys


def test_g5_threshold_default():
    """Cross-session semantic threshold default raised to 0.75."""
    import os
    # Unset env var to test hardcoded default
    old = os.environ.pop("COGMEM_API_RETAIN_CROSS_BANK_SEMANTIC_THRESHOLD", None)
    try:
        from cogmem_api.engine.retain.link_creation import _CROSS_BANK_SEMANTIC_THRESHOLD
        assert _CROSS_BANK_SEMANTIC_THRESHOLD == 0.75, \
            f"Expected 0.75, got {_CROSS_BANK_SEMANTIC_THRESHOLD}"
    finally:
        if old is not None:
            os.environ["COGMEM_API_RETAIN_CROSS_BANK_SEMANTIC_THRESHOLD"] = old
    print("G-5 PASS: cross-session semantic threshold default = 0.75")


def test_g5_top_k_default():
    """Cross-session semantic top_k default reduced to 4."""
    import os
    old = os.environ.pop("COGMEM_API_RETAIN_CROSS_BANK_SEMANTIC_TOP_K", None)
    try:
        from cogmem_api.engine.retain.link_creation import _CROSS_BANK_SEMANTIC_TOP_K
        assert _CROSS_BANK_SEMANTIC_TOP_K == 4, \
            f"Expected 4, got {_CROSS_BANK_SEMANTIC_TOP_K}"
    finally:
        if old is not None:
            os.environ["COGMEM_API_RETAIN_CROSS_BANK_SEMANTIC_TOP_K"] = old
    print("G-5 PASS: cross-session semantic top_k default = 4")


def test_g5_bfs_semantic_squaring():
    """BFS propagation squares semantic link weights."""
    import inspect
    import cogmem_api.engine.search.graph_retrieval as gr

    src = inspect.getsource(gr)
    assert "link_type == \"semantic\"" in src, "semantic weight squaring not found"
    assert "link_boost = base_weight" in src, "semantic squaring via link_boost not found"
    assert "link_type == \"causal\"" in src, "causal boost reference not found"
    print("G-5 PASS: BFS semantic weight squaring present")


def test_g5_env_var_override():
    """Env vars can still override defaults."""
    import os
    old_t = os.environ.pop("COGMEM_API_RETAIN_CROSS_BANK_SEMANTIC_THRESHOLD", None)
    old_k = os.environ.pop("COGMEM_API_RETAIN_CROSS_BANK_SEMANTIC_TOP_K", None)
    try:
        os.environ["COGMEM_API_RETAIN_CROSS_BANK_SEMANTIC_THRESHOLD"] = "0.8"
        os.environ["COGMEM_API_RETAIN_CROSS_BANK_SEMANTIC_TOP_K"] = "6"
        # Reimport to pick up env change — use importlib
        import importlib
        from cogmem_api.engine.retain import link_creation as lc_mod
        importlib.reload(lc_mod)
        assert lc_mod._CROSS_BANK_SEMANTIC_THRESHOLD == 0.8, \
            f"Expected 0.8, got {lc_mod._CROSS_BANK_SEMANTIC_THRESHOLD}"
        assert lc_mod._CROSS_BANK_SEMANTIC_TOP_K == 6, \
            f"Expected 6, got {lc_mod._CROSS_BANK_SEMANTIC_TOP_K}"
    finally:
        # Restore
        if old_t is not None:
            os.environ["COGMEM_API_RETAIN_CROSS_BANK_SEMANTIC_THRESHOLD"] = old_t
        else:
            os.environ.pop("COGMEM_API_RETAIN_CROSS_BANK_SEMANTIC_THRESHOLD", None)
        if old_k is not None:
            os.environ["COGMEM_API_RETAIN_CROSS_BANK_SEMANTIC_TOP_K"] = old_k
        else:
            os.environ.pop("COGMEM_API_RETAIN_CROSS_BANK_SEMANTIC_TOP_K", None)
        importlib.reload(lc_mod)
    print("G-5 PASS: env var override works correctly")


if __name__ == "__main__":
    tests = [
        ("threshold-default", test_g5_threshold_default),
        ("topk-default", test_g5_top_k_default),
        ("bfs-squaring", test_g5_bfs_semantic_squaring),
        ("env-override", test_g5_env_var_override),
    ]

    failures = 0
    for name, fn in tests:
        try:
            fn()
        except Exception as e:
            print(f"FAIL G-5/{name}: {e}")
            failures += 1

    print()
    if failures:
        print(f"RESULT: {len(tests) - failures}/{len(tests)} PASS, {failures} FAIL")
        sys.exit(1)
    else:
        print(f"RESULT: {len(tests)}/{len(tests)} PASS — G-5 semantic cap gates PASS")
        sys.exit(0)
