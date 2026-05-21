"""S32-T4 artifact: verification-gate decision logic (offline) + guarded live smoke.

Offline: the pure gate functions. Live smoke runs only if a cogmem-api server is
reachable at COGMEM_API_BASE_URL (default http://localhost:8888); otherwise it SKIPS.

Run: uv run python tests/artifacts/test_task_s32_t4_gates.py
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from cogmem_bench.gates import (
    decide_acceptance,
    evaluate_discrimination,
    evaluate_embedding_gate,
)

GOLD = "User planned to finish the Rust async course by end of September but abandoned it."


def test_embedding_gate_pass() -> None:
    recalled = [
        {"type": "intention", "text": "User abandoned the planned Rust async course from September."},
        {"type": "experience", "text": "totally unrelated cooking note"},
    ]
    res = evaluate_embedding_gate(GOLD, "intention", recalled)
    assert res.passed, res.detail
    assert res.found_fact_type == "intention"
    print(f"[ok] embedding gate PASS — {res.detail}")


def test_embedding_gate_fail_wrong_type() -> None:
    # Same text but stored as experience, not intention -> must fail (type matters).
    recalled = [{"type": "experience", "text": "User planned to finish the Rust async course by September abandoned"}]
    res = evaluate_embedding_gate(GOLD, "intention", recalled)
    assert not res.passed, "should fail when gold text is only present under the wrong type"
    print(f"[ok] embedding gate FAIL on wrong type — {res.detail}")


def test_discrimination_logic() -> None:
    assert evaluate_discrimination(True, False).passed, "E7 PASS / E11 FAIL must discriminate"
    assert not evaluate_discrimination(True, True).passed, "both PASS -> not discriminative"
    assert not evaluate_discrimination(False, False).passed, "both FAIL -> not discriminative"
    assert not evaluate_discrimination(False, True).passed, "E7 FAIL -> reject"
    print("[ok] discrimination gate truth table correct")


def test_decide_acceptance() -> None:
    emb = evaluate_embedding_gate(GOLD, "intention", [{"type": "intention", "text": GOLD}])
    disc = evaluate_discrimination(True, False)
    accepted = decide_acceptance("c1", emb, disc)
    assert accepted.accepted
    # Embedding pass but no discrimination -> reject
    rejected = decide_acceptance("c2", emb, evaluate_discrimination(True, True))
    assert not rejected.accepted
    # Discrimination pass but embedding fail -> reject
    bad_emb = evaluate_embedding_gate(GOLD, "intention", [])
    assert not decide_acceptance("c3", bad_emb, disc).accepted
    print("[ok] acceptance requires BOTH gates")


def test_live_smoke() -> None:
    base = os.getenv("COGMEM_API_BASE_URL", "http://localhost:8888")
    try:
        import requests

        requests.get(f"{base}/v1/banks", timeout=2)
    except Exception as exc:  # noqa: BLE001
        print(f"[skip] live smoke — no server at {base} ({type(exc).__name__})")
        return
    # Server reachable: confirm run_case_gates is importable/wired (no full run here).
    from cogmem_bench.gates import run_case_gates  # noqa: F401

    print("[ok] live server reachable; run_case_gates importable (full live run via runner --pilot)")


def main() -> int:
    test_embedding_gate_pass()
    test_embedding_gate_fail_wrong_type()
    test_discrimination_logic()
    test_decide_acceptance()
    test_live_smoke()
    print("\nS32-T4 PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
