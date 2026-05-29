"""Verification gates — the reject/regenerate loop (docs/Ablation-Flow.md step 3).

Embedding gate:   did retain store the gold fact AS the intended fact_type?
Discrimination gate: does the full system (E7) PASS while world/experience/opinion-only
                     (E11) FAILS? Keep the case only if it discriminates.

Decision logic is pure and unit-tested offline. The live helpers (`run_case_gates`) drive
the running API + the existing eval harness, retaining ONCE (E7) and reusing the bank for
E11 via skip_retain (recall-time type filtering — see the S32 architectural finding).
"""

from __future__ import annotations

import re
from typing import Any, Callable

from .schema import (
    DiscriminationGateResult,
    EmbeddingGateResult,
    GateResult,
    ScenarioSpec,
)

_EMBED_COVERAGE_THRESHOLD = 0.25

# Full-recall arm: E7F is E7 with adaptive_router_enabled=False — removes the
# "prospective → intention-only" router rule that would otherwise bias the comparison
# (E7 wins because the router was hard-coded to use intention for prospective Qs). The
# flat router makes E7 search all types via semantic similarity, like the ablated arm.
_FULL_ARM: str = "E7F"

# Single-type ablation arm per target type (FLAT-ROUTER variants): remove ONLY that type
# so a failure is attributable to that specific network. Flat router on both arms so any
# discrimination is content-level, not a router-policy artifact.
_ABLATION_ARM: dict[str, str] = {"intention": "E9F", "action_effect": "E10F", "habit": "E8F"}


def _keywords(text: str) -> set[str]:
    return {w for w in re.findall(r"[a-z0-9]+", text.lower()) if len(w) >= 4}


# ── Pure decision logic (offline-testable) ──────────────────────────────────


def evaluate_embedding_gate(
    gold_text: str,
    expected_type: str,
    recalled_facts: list[dict[str, Any]],
) -> EmbeddingGateResult:
    """Pass if some recalled fact of `expected_type` covers the gold fact's keywords."""
    gold_kw = _keywords(gold_text)
    typed = [f for f in recalled_facts if str(f.get("type") or f.get("fact_type") or "") == expected_type]
    if not gold_kw:
        return EmbeddingGateResult(
            passed=bool(typed), gold_fact_found=bool(typed), expected_fact_type=expected_type,
            found_fact_type=expected_type if typed else None, detail="no gold keywords; presence-only check",
        )
    best_cov = 0.0
    for f in typed:
        cov = len(gold_kw & _keywords(str(f.get("text", "")))) / len(gold_kw)
        best_cov = max(best_cov, cov)
    passed = best_cov >= _EMBED_COVERAGE_THRESHOLD
    return EmbeddingGateResult(
        passed=passed,
        gold_fact_found=passed,
        expected_fact_type=expected_type,
        found_fact_type=expected_type if passed else None,
        detail=f"best {expected_type}-typed coverage {best_cov:.0%} (threshold {_EMBED_COVERAGE_THRESHOLD:.0%})",
    )


def evaluate_discrimination(full_correct: bool, weo_correct: bool) -> DiscriminationGateResult:
    """Pass only if full (E7) is correct AND world/experience/opinion-only (E11) is wrong."""
    passed = bool(full_correct) and not bool(weo_correct)
    return DiscriminationGateResult(
        passed=passed,
        full_correct=bool(full_correct),
        weo_correct=bool(weo_correct),
        detail=f"E7={'PASS' if full_correct else 'FAIL'} / E11={'PASS' if weo_correct else 'FAIL'}",
    )


def decide_acceptance(
    scenario_id: str,
    embedding: EmbeddingGateResult,
    discrimination: DiscriminationGateResult | None,
) -> GateResult:
    """Acceptance hinges ONLY on discrimination (full PASS / w-e-o FAIL).

    The embedding gate is advisory: its keyword metric produced false negatives (it failed a
    genuinely discriminating case), so it must not reject. It is still recorded for diagnosis.
    """
    accepted = discrimination is not None and discrimination.passed
    return GateResult(
        scenario_id=scenario_id,
        embedding_gate=embedding,
        discrimination_gate=discrimination,
        accepted=accepted,
    )


# ── Live orchestration (drives API + eval harness) ──────────────────────────


def run_case_gates(
    spec: ScenarioSpec,
    fixture_path: str,
    *,
    api_base_url: str,
    bank_id: str,
    timeout_seconds: float = 3600.0,
    skip_retain: bool = False,
    retain_level_ablation: bool = False,
    post_json_fn: Callable[[str, dict, float], dict] | None = None,
) -> tuple[GateResult, dict[str, Any]]:
    """Retain (one or two banks) + embedding + discrimination gates → (verdict, detail).

    `fixture_path` must be a single-item distilled fixture for this spec (conv_index=0).
    Requires a running cogmem-api. `skip_retain=True` to re-gate against already-populated
    banks (recall + judge only).

    `retain_level_ablation=False` (default): single bank `<bank_id>`, both arms recall against
    it, ablation happens recall-side via the ablated profile's `recall_fact_types`. Fast,
    backward-compatible with previous gate runs.

    `retain_level_ablation=True` (S33 cách B): TWO banks — `<bank_id>_full` (all types) and
    `<bank_id>_ablated` (the ablated profile's allowed types passed as `enabled_fact_types`
    to retain so the disabled type's facts are dropped at extraction). Closes the
    "edges-still-existed" loophole. Costs ~2x retain time per case.

    The returned `detail` dict carries the FULL evidence for manual inspection — both runs'
    recall_results and generated_answer (judge.correct is unreliable; verify the answer
    against the gold by hand, cogmem-verify style).
    """
    # Imported lazily so the module stays importable offline (no requests at import time).
    from scripts.eval_cogmem import (  # type: ignore
        _benchmark_item_as_fixture,
        get_fixture,
        post_json,
        run_pipeline,
    )

    post = post_json_fn or post_json
    fixture = get_fixture("longmemeval", fixture_path=fixture_path)
    mini = _benchmark_item_as_fixture(fixture, 0)

    ablation_profile = _ABLATION_ARM.get(spec.target_type, "E11")

    # Resolve bank ids per mode and pre-retain the ablated bank if needed (S33 cách B).
    if retain_level_ablation:
        bank_full = f"{bank_id}_full"
        bank_ablated = f"{bank_id}_ablated"
        if not skip_retain:
            # Pre-retain ablated bank with enabled_fact_types = the ablated profile's
            # allowed type list, so disabled-type facts are dropped at extraction.
            from scripts.eval_cogmem import ABLATION_PROFILES  # type: ignore

            allowed = list(ABLATION_PROFILES[ablation_profile].recall_fact_types)
            items_data = mini.get("_messages") or [
                (sid, [{"role": "", "content": t} for t in turns]) for sid, turns in mini.get("_sessions", [])
            ]
            payload = {
                "items": [{"messages": msgs, "document_id": sid} for sid, msgs in items_data],
                "async": False,
                "enabled_fact_types": allowed,
            }
            post(f"{api_base_url}/v1/default/banks/{bank_ablated}/memories", payload, timeout_seconds)
    else:
        bank_full = bank_id
        bank_ablated = bank_id

    # 1) Full arm (E7F = E7 with flat router): retain (unless skip_retain) + recall + judge.
    res_e7 = run_pipeline(
        "full", api_base_url, bank_full, _FULL_ARM, "longmemeval",
        skip_retain=skip_retain, timeout_seconds=timeout_seconds,
        post_json_fn=post, fixture_override=mini,
    )
    q_e7 = res_e7["questions"][0]
    full_correct = bool((q_e7.get("judge") or {}).get("correct"))

    # 2) Embedding gate against the full bank.
    recall_resp = post(
        f"{api_base_url}/v1/default/banks/{bank_full}/memories/recall",
        {"query": spec.gold_fact.text, "types": [spec.target_type], "top_k": 50, "trace": False},
        timeout_seconds,
    )
    embedding = evaluate_embedding_gate(
        spec.gold_fact.text, spec.target_type, list(recall_resp.get("results", []))
    )

    # 3) Single-type ablation arm. In default mode, hits the same bank with recall-time
    #    type filter. In retain-level mode, hits the separately-retained ablated bank where
    #    the disabled type's facts were never stored. Always skip_retain=True (already done).
    res_abl = run_pipeline(
        "full", api_base_url, bank_ablated, ablation_profile, "longmemeval",
        skip_retain=True, timeout_seconds=timeout_seconds,
        post_json_fn=post, fixture_override=mini,
    )
    q_abl = res_abl["questions"][0]
    ablated_correct = bool((q_abl.get("judge") or {}).get("correct"))

    discrimination = evaluate_discrimination(full_correct, ablated_correct)
    result = decide_acceptance(spec.scenario_id, embedding, discrimination)

    detail: dict[str, Any] = {
        "scenario_id": spec.scenario_id,
        "target_type": spec.target_type,
        "ablation_profile": ablation_profile,
        "question": spec.question,
        "gold_answer": spec.gold_answer,
        "gold_fact": spec.gold_fact.text,
        "embedding_gate": {
            "passed": embedding.passed,
            "detail": embedding.detail,
            "recall": list(recall_resp.get("results", [])),
        },
        # Both runs' answers + recall — verify the answer vs gold by hand; judge.correct is unreliable.
        "E7": {
            "judge_correct": full_correct,
            "generated_answer": q_e7.get("generated_answer", ""),
            "judge": q_e7.get("judge"),
            "recall_results": q_e7.get("recall_results", []),
        },
        "ablated": {
            "profile": ablation_profile,
            "judge_correct": ablated_correct,
            "generated_answer": q_abl.get("generated_answer", ""),
            "judge": q_abl.get("judge"),
            "recall_results": q_abl.get("recall_results", []),
        },
    }
    return result, detail
