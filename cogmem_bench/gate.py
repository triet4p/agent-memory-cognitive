"""Standalone gate script (manual) — docs/Ablation-Flow.md step 3.

Runs the embedding + discrimination gates over already-generated (frozen) fixtures and
writes a yield report. Needs a running cogmem-api with Ministral (COGMEM_API_LLM_*).
Run cogmem_bench.generate first.

  uv run python -m cogmem_bench.gate                            # gate data fixtures -> experiments/cogmem_bench
  uv run python -m cogmem_bench.gate --specs-dir <dir> --data-dir <dir> --out-dir <dir> --api-base-url ...
  uv run python -m cogmem_bench.gate --only pilot_habit_01
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

from .datasets import DEFAULT_DATA_DIR, DEFAULT_EXPERIMENT_DIR, DEFAULT_REPORT, PILOT_SPECS_DIR, load_specs, work_fixture_path
from .schema import GateResult, ScenarioSpec


def write_report(
    results: list[GateResult],
    specs: list[ScenarioSpec],
    report_path: Path,
    details: dict[str, dict] | None = None,
) -> None:
    spec_type = {s.scenario_id: s.target_type for s in specs}
    total = len(results)
    accepted = sum(1 for r in results if r.accepted)
    yield_line = f"Cases gated: {total} | Accepted: {accepted} | Yield: {accepted/total:.0%}" if total else "Cases gated: 0"
    lines = [
        "# CogMem bench — gate yield report",
        "",
        f"Generated: {datetime.now(timezone.utc).date().isoformat()}",
        yield_line,
        "",
        "| Case | Type | Embedding | E7F (full, flat router) | Ablated (flat router) | Accepted |",
        "|------|------|-----------|------------------------|-----------------------|----------|",
    ]
    for r in results:
        d = r.discrimination_gate
        abl = (details or {}).get(r.scenario_id, {}).get("ablation_profile", "")
        lines.append(
            f"| {r.scenario_id} | {spec_type.get(r.scenario_id, '?')} | "
            f"{'PASS' if r.embedding_gate.passed else 'FAIL'} | "
            f"{'PASS' if d and d.full_correct else 'FAIL'} | "
            f"{'PASS' if d and d.weo_correct else 'FAIL'} ({abl}) | "
            f"{'YES' if r.accepted else 'no'} |"
        )
    by_type: dict[str, list[GateResult]] = {}
    for r in results:
        by_type.setdefault(spec_type.get(r.scenario_id, "?"), []).append(r)
    lines += ["", "## Per-type yield", "", "| Type | Gated | Accepted |", "|------|-------|----------|"]
    for t, rs in sorted(by_type.items()):
        lines.append(f"| {t} | {len(rs)} | {sum(1 for r in rs if r.accepted)} |")

    if details:
        lines += [
            "",
            "## Manual verification (judge.correct is unreliable — compare answers to gold yourself)",
            "",
        "Full recall + answers per case: `experiments/cogmem_bench/gate_detail/<scenario_id>.json`.",
        ]
        for r in results:
            d = details.get(r.scenario_id)
            if not d:
                continue
            lines += [
                "",
                f"### {r.scenario_id} ({spec_type.get(r.scenario_id, '?')})",
                f"- **gold**: {d.get('gold_answer','')}",
                f"- **E7** (judge={d['E7'].get('judge_correct')}): {str(d['E7'].get('generated_answer',''))[:500]}",
                f"- **{d['ablated'].get('profile','ablated')}** (judge={d['ablated'].get('judge_correct')}): {str(d['ablated'].get('generated_answer',''))[:500]}",
            ]

    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"[report] wrote {report_path}")


def gate_all(
    specs_dir: Path,
    data_dir: Path,
    out_dir: Path,
    api_base_url: str,
    report_path: Path,
    *,
    only: str | None,
    skip_retain: bool = False,
    retain_level_ablation: bool = False,
    timeout_seconds: float = 3600.0,
) -> int:
    from .gates import run_case_gates  # lazy: imports requests/eval harness only when gating

    specs = load_specs(specs_dir)
    if only:
        specs = [s for s in specs if s.scenario_id == only]
        if not specs:
            print(f"no spec with scenario_id={only}")
            return 1

    accepted_dir = out_dir / "accepted"
    detail_dir = out_dir / "gate_detail"
    accepted_dir.mkdir(parents=True, exist_ok=True)
    detail_dir.mkdir(parents=True, exist_ok=True)

    results: list[GateResult] = []
    details: dict[str, dict] = {}
    for spec in specs:
        fixture_path = work_fixture_path(data_dir, spec.scenario_id)
        if not fixture_path.exists():
            print(f"[skip] {spec.scenario_id}: no work fixture at {fixture_path} (run generate first)")
            continue
        print(f"\n=== gating {spec.scenario_id} ({spec.target_type}) ===")
        bank_id = f"COGMEM_BENCH_{spec.scenario_id}"
        result, detail = run_case_gates(
            spec, str(fixture_path), api_base_url=api_base_url, bank_id=bank_id,
            skip_retain=skip_retain, retain_level_ablation=retain_level_ablation,
            timeout_seconds=timeout_seconds,
        )
        results.append(result)
        details[spec.scenario_id] = detail
        # Persist full evidence (recall + generated answers) for manual verification.
        (detail_dir / f"{spec.scenario_id}.json").write_text(
            json.dumps(detail, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        print(f"  embedding: {result.embedding_gate.detail}")
        if result.discrimination_gate:
            print(f"  discrimination: {result.discrimination_gate.detail}")
        abl = detail["ablated"]["profile"]
        print(f"  E7   answer : {str(detail['E7']['generated_answer'])[:160]}")
        print(f"  {abl:<4} answer : {str(detail['ablated']['generated_answer'])[:160]}")
        print(f"  gold        : {spec.gold_answer}")
        print(f"  ACCEPTED={result.accepted}  (judge-based; verify answers above vs gold by hand)")
        if result.accepted:
            # freeze the accepted fixture by copying the work fixture content
            accepted_path = accepted_dir / f"{spec.scenario_id}.json"
            accepted_path.write_text(fixture_path.read_text(encoding="utf-8"), encoding="utf-8")

    if results:
        write_report(results, specs, report_path, details)
        (out_dir / "gate_results.json").write_text(
            json.dumps([r.model_dump() for r in results], ensure_ascii=False, indent=2), encoding="utf-8"
        )
    print(f"\nGated {len(results)} cases — {sum(1 for r in results if r.accepted)} accepted")
    return 0


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Gate generated benchmark conversations (manual).")
    ap.add_argument("--specs-dir", default=str(PILOT_SPECS_DIR))
    ap.add_argument("--data-dir", default=str(DEFAULT_DATA_DIR),
                    help="benchmark fixture root containing work/<scenario_id>.json (default data/bench)")
    ap.add_argument("--out-dir", default=str(DEFAULT_EXPERIMENT_DIR),
                    help="experiment output root for gate_results, gate_detail, accepted fixtures")
    ap.add_argument("--api-base-url", default="http://localhost:8888")
    ap.add_argument("--report", default=str(DEFAULT_REPORT))
    ap.add_argument("--only", default=None, help="gate a single scenario_id")
    ap.add_argument("--skip-retain", action="store_true",
                    help="re-gate against already-retained banks (recall + judge only; no re-ingest)")
    ap.add_argument("--retain-level-ablation", action="store_true",
                    help="S33 cách B: retain TWO banks per case (<bank>_full + <bank>_ablated, "
                         "the ablated bank uses enabled_fact_types to drop disabled-type facts at "
                         "extraction). Closes the 'edges-still-existed' loophole. ~2x retain cost.")
    ap.add_argument("--timeout", type=float, default=3600.0,
                    help="HTTP read timeout in seconds for retain/recall/generate/judge (default 3600).")
    args = ap.parse_args(argv)
    return gate_all(
        Path(args.specs_dir), Path(args.data_dir), Path(args.out_dir), args.api_base_url, Path(args.report),
        only=args.only, skip_retain=args.skip_retain,
        retain_level_ablation=args.retain_level_ablation,
        timeout_seconds=args.timeout,
    )


if __name__ == "__main__":
    sys.exit(main())
