"""Standalone gate script (manual) — docs/Ablation-Flow.md step 3.

Runs the embedding + discrimination gates over already-generated (frozen) fixtures and
writes a yield report. Needs a running cogmem-api with Ministral (COGMEM_API_LLM_*).
Run cogmem_bench.generate first.

  uv run python -m cogmem_bench.gate                            # gate pilot work fixtures
  uv run python -m cogmem_bench.gate --specs-dir <dir> --out-dir <dir> --api-base-url ...
  uv run python -m cogmem_bench.gate --only pilot_habit_01
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

from .datasets import DEFAULT_OUT_DIR, DEFAULT_REPORT, PILOT_SPECS_DIR, load_specs, work_fixture_path
from .schema import GateResult, ScenarioSpec


def write_report(results: list[GateResult], specs: list[ScenarioSpec], report_path: Path) -> None:
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
        "| Case | Type | Embedding | E7 | E11 | Accepted |",
        "|------|------|-----------|----|----|----------|",
    ]
    for r in results:
        d = r.discrimination_gate
        lines.append(
            f"| {r.scenario_id} | {spec_type.get(r.scenario_id, '?')} | "
            f"{'PASS' if r.embedding_gate.passed else 'FAIL'} | "
            f"{'PASS' if d and d.full_correct else 'FAIL'} | "
            f"{'PASS' if d and d.weo_correct else 'FAIL'} | "
            f"{'YES' if r.accepted else 'no'} |"
        )
    by_type: dict[str, list[GateResult]] = {}
    for r in results:
        by_type.setdefault(spec_type.get(r.scenario_id, "?"), []).append(r)
    lines += ["", "## Per-type yield", "", "| Type | Gated | Accepted |", "|------|-------|----------|"]
    for t, rs in sorted(by_type.items()):
        lines.append(f"| {t} | {len(rs)} | {sum(1 for r in rs if r.accepted)} |")
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"[report] wrote {report_path}")


def gate_all(specs_dir: Path, out_dir: Path, api_base_url: str, report_path: Path, *, only: str | None) -> int:
    from .gates import run_case_gates  # lazy: imports requests/eval harness only when gating

    specs = load_specs(specs_dir)
    if only:
        specs = [s for s in specs if s.scenario_id == only]
        if not specs:
            print(f"no spec with scenario_id={only}")
            return 1

    accepted_dir = out_dir / "accepted"
    accepted_dir.mkdir(parents=True, exist_ok=True)

    results: list[GateResult] = []
    for spec in specs:
        fixture_path = work_fixture_path(out_dir, spec.scenario_id)
        if not fixture_path.exists():
            print(f"[skip] {spec.scenario_id}: no work fixture at {fixture_path} (run generate first)")
            continue
        print(f"\n=== gating {spec.scenario_id} ({spec.target_type}) ===")
        bank_id = f"COGMEM_BENCH_{spec.scenario_id}"
        result = run_case_gates(spec, str(fixture_path), api_base_url=api_base_url, bank_id=bank_id)
        results.append(result)
        print(f"  embedding: {result.embedding_gate.detail}")
        if result.discrimination_gate:
            print(f"  discrimination: {result.discrimination_gate.detail}")
        print(f"  ACCEPTED={result.accepted}")
        if result.accepted:
            # freeze the accepted fixture by copying the work fixture content
            accepted_path = accepted_dir / f"{spec.scenario_id}.json"
            accepted_path.write_text(fixture_path.read_text(encoding="utf-8"), encoding="utf-8")

    if results:
        write_report(results, specs, report_path)
        (out_dir / "gate_results.json").write_text(
            json.dumps([r.model_dump() for r in results], ensure_ascii=False, indent=2), encoding="utf-8"
        )
    print(f"\nGated {len(results)} cases — {sum(1 for r in results if r.accepted)} accepted")
    return 0


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Gate generated benchmark conversations (manual).")
    ap.add_argument("--specs-dir", default=str(PILOT_SPECS_DIR))
    ap.add_argument("--out-dir", default=str(DEFAULT_OUT_DIR))
    ap.add_argument("--api-base-url", default="http://localhost:8888")
    ap.add_argument("--report", default=str(DEFAULT_REPORT))
    ap.add_argument("--only", default=None, help="gate a single scenario_id")
    args = ap.parse_args(argv)
    return gate_all(Path(args.specs_dir), Path(args.out_dir), args.api_base_url, Path(args.report), only=args.only)


if __name__ == "__main__":
    sys.exit(main())
