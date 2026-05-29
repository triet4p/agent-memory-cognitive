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
    assert decide_acceptance("c1", emb, disc).accepted
    # Discrimination fails -> reject (regardless of embedding)
    assert not decide_acceptance("c2", emb, evaluate_discrimination(True, True)).accepted
    # Embedding FAILS but discrimination passes -> still ACCEPTED (embedding is advisory only)
    bad_emb = evaluate_embedding_gate(GOLD, "intention", [])
    res = decide_acceptance("c3", bad_emb, disc)
    assert res.accepted, "embedding gate must be non-blocking; discrimination is the sole criterion"
    assert not res.embedding_gate.passed, "embedding result still recorded for diagnosis"
    print("[ok] acceptance hinges on discrimination only; embedding advisory")


def test_retain_strict_typing_addendum() -> None:
    """S33 plug-in: strict-typing addendum is empty by default (backward-compat) and
    activates only when both the env flag and enabled_fact_types are set."""
    from cogmem_api.engine.retain.fact_extraction import _strict_typing_addendum

    # Default: no addendum (production behavior unchanged)
    assert _strict_typing_addendum(None, False) == ""
    assert _strict_typing_addendum(("world", "experience"), False) == ""
    assert _strict_typing_addendum(None, True) == ""
    # All types allowed → also empty (nothing to forbid)
    assert _strict_typing_addendum(
        ("world", "experience", "opinion", "habit", "intention", "action_effect"), True
    ) == ""
    # Real ablation: intention disabled → addendum names disabled type + forbids recasting
    ad = _strict_typing_addendum(("world", "experience", "opinion", "habit", "action_effect"), True)
    assert "STRICT TYPING" in ad and "intention" in ad and "do NOT recast" in ad.lower() or "do not recast" in ad.lower()
    print("[ok] strict-typing addendum: empty by default, non-empty only when both flags set")


def test_retain_llm_env_precedence() -> None:
    """S33 plug-in: COGMEM_API_RETAIN_LLM_* overrides main LLM, falls back when unset."""
    import importlib
    import os
    import cogmem_api.config as cfg
    importlib.reload(cfg)
    # Default: retain LLM fields unset → fall back to main LLM (verified by None defaults)
    for k in ("COGMEM_API_RETAIN_LLM_BASE_URL", "COGMEM_API_RETAIN_LLM_MODEL", "COGMEM_API_RETAIN_LLM_API_KEY", "COGMEM_API_RETAIN_STRICT_TYPING"):
        os.environ.pop(k, None)
    runtime = cfg._get_raw_config()
    assert runtime.retain_llm_base_url is None
    assert runtime.retain_strict_typing is False
    # Set env → fields populated
    os.environ["COGMEM_API_RETAIN_LLM_BASE_URL"] = "https://minimax.example/v1"
    os.environ["COGMEM_API_RETAIN_LLM_MODEL"] = "minimax-m2"
    os.environ["COGMEM_API_RETAIN_STRICT_TYPING"] = "true"
    runtime2 = cfg._get_raw_config()
    assert runtime2.retain_llm_base_url == "https://minimax.example/v1"
    assert runtime2.retain_llm_model == "minimax-m2"
    assert runtime2.retain_strict_typing is True
    # cleanup
    for k in ("COGMEM_API_RETAIN_LLM_BASE_URL", "COGMEM_API_RETAIN_LLM_MODEL", "COGMEM_API_RETAIN_STRICT_TYPING"):
        os.environ.pop(k, None)
    print("[ok] retain LLM env: unset -> None (fallback); set -> populated")


def test_gate_signature_supports_retain_level_ablation() -> None:
    """S33 plug-in: run_case_gates accepts retain_level_ablation flag (default False)."""
    import inspect
    from cogmem_bench.gates import run_case_gates

    params = inspect.signature(run_case_gates).parameters
    assert "retain_level_ablation" in params
    assert params["retain_level_ablation"].default is False, "must default to False (backward-compat)"
    print("[ok] run_case_gates exposes retain_level_ablation (default False)")


def test_retain_request_accepts_enabled_fact_types() -> None:
    """S33 plug-in: HTTP RetainRequest accepts enabled_fact_types (optional, default None)."""
    from cogmem_api.api.http import RetainRequest

    r_default = RetainRequest.model_validate({"items": []})
    assert r_default.enabled_fact_types is None, "default must be None (no filter)"
    r_set = RetainRequest.model_validate({"items": [], "enabled_fact_types": ["world", "experience"]})
    assert r_set.enabled_fact_types == ["world", "experience"]
    print("[ok] RetainRequest.enabled_fact_types: optional, default None")


def test_router_fallback() -> None:
    from cogmem_api.engine.search.retrieval import _select_fact_types_for_query

    # full set: prospective routes to intention-only (unchanged)
    full = ["world", "experience", "opinion", "habit", "intention", "action_effect"]
    assert _select_fact_types_for_query("prospective", full) == ["intention"]
    # ablated set (no intention): must FALL BACK to all available types, not []
    ablated = ["world", "experience", "opinion", "habit", "action_effect"]
    routed = _select_fact_types_for_query("prospective", ablated)
    assert routed == ablated, f"expected fallback to all types, got {routed}"
    print("[ok] router fallback: prospective with no intention -> all remaining types (not [])")


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
    test_retain_strict_typing_addendum()
    test_retain_llm_env_precedence()
    test_gate_signature_supports_retain_level_ablation()
    test_retain_request_accepts_enabled_fact_types()
    test_router_fallback()
    test_live_smoke()
    print("\nS32-T4 PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
