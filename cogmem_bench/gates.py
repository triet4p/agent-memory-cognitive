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

_EMBED_COVERAGE_THRESHOLD = 0.4


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
    accepted = embedding.passed and discrimination is not None and discrimination.passed
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
    timeout_seconds: float = 600.0,
    post_json_fn: Callable[[str, dict, float], dict] | None = None,
) -> GateResult:
    """Retain once (E7), run embedding + discrimination gates, return the verdict.

    `fixture_path` must be a single-item distilled fixture for this spec (conv_index=0).
    Requires a running cogmem-api with Ministral.
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

    # 1) E7 full: retain + recall + judge.
    res_e7 = run_pipeline(
        "full", api_base_url, bank_id, "E7", "longmemeval",
        skip_retain=False, timeout_seconds=timeout_seconds,
        post_json_fn=post, fixture_override=mini,
    )
    full_correct = bool((res_e7["questions"][0].get("judge") or {}).get("correct"))

    # 2) Embedding gate against the now-retained bank.
    recall_resp = post(
        f"{api_base_url}/v1/default/banks/{bank_id}/memories/recall",
        {"query": spec.gold_fact.text, "types": [spec.target_type], "top_k": 50, "trace": False},
        timeout_seconds,
    )
    embedding = evaluate_embedding_gate(
        spec.gold_fact.text, spec.target_type, list(recall_resp.get("results", []))
    )

    # 3) E11 (w/e/o-only) on the SAME bank — recall-time type filter, no re-retain.
    res_e11 = run_pipeline(
        "full", api_base_url, bank_id, "E11", "longmemeval",
        skip_retain=True, timeout_seconds=timeout_seconds,
        post_json_fn=post, fixture_override=mini,
    )
    weo_correct = bool((res_e11["questions"][0].get("judge") or {}).get("correct"))

    discrimination = evaluate_discrimination(full_correct, weo_correct)
    return decide_acceptance(spec.scenario_id, embedding, discrimination)
