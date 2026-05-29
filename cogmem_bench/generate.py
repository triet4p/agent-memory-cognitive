"""Standalone generation script (manual, long-running) — docs/Ablation-Flow.md step 2.

Generates conversations session-by-session via Minimax and freezes them as distilled
fixtures. Needs ONLY the Minimax generator endpoint (COGMEM_BENCH_GEN_LLM_*); no Ministral
/ running API. Gating is a separate step (cogmem_bench.gate).

  uv run python -m cogmem_bench.generate                       # pilot specs -> data/bench/work
  uv run python -m cogmem_bench.generate --specs-dir <dir> --out-dir <dir>
  uv run python -m cogmem_bench.generate --dry-run             # render prompts only, no LLM
  uv run python -m cogmem_bench.generate --only pilot_habit_01 # one scenario
"""

from __future__ import annotations

import argparse
import asyncio
import sys
from pathlib import Path

from .datasets import DEFAULT_OUT_DIR, PILOT_SPECS_DIR, load_specs
from .fixtures import write_distilled_fixture
from .generation import generate_conversation, soft_validate_embedding
from .prompts import build_session_prompt, session_role
from .schema import ScenarioSpec


def _dry_run(specs: list[ScenarioSpec]) -> int:
    print(f"[dry-run] {len(specs)} specs — rendering per-session prompts (no LLM calls)")
    for s in specs:
        roles = [session_role(s, i) for i in range(s.session_plan.total_sessions)]
        # render every session prompt to catch template errors
        for i, role in enumerate(roles):
            build_session_prompt(s, i, role, [f"recap {j}" for j in range(i)], recent_sessions=[])
        print(f"  - {s.scenario_id:24} type={s.target_type:13} sessions={len(roles)} roles={roles}")
    print("\nGENERATE DRY-RUN OK")
    return 0


def generate_all(
    specs_dir: Path,
    out_dir: Path,
    *,
    only: str | None,
    dry_run: bool,
    last_k: int | None = None,
    max_tokens: int | None = None,
    filler_max_tokens: int | None = None,
    max_retries: int | None = None,
) -> int:
    specs = load_specs(specs_dir)
    if only:
        specs = [s for s in specs if s.scenario_id == only]
        if not specs:
            print(f"no spec with scenario_id={only}")
            return 1
    if dry_run:
        return _dry_run(specs)

    from .config import resolve_generation_llm, resolve_last_k_verbatim, resolve_max_retries, resolve_max_tokens

    gen_llm = resolve_generation_llm()
    last_k_verbatim = resolve_last_k_verbatim(last_k)
    gold_tokens, filler_tokens = resolve_max_tokens(max_tokens, filler_max_tokens)
    retries = resolve_max_retries(max_retries)
    print(f"[config] last_k_verbatim={last_k_verbatim}, gold_tokens={gold_tokens}, filler_tokens={filler_tokens}, max_retries={retries}, llm={gen_llm}")
    work_dir = out_dir / "work"
    work_dir.mkdir(parents=True, exist_ok=True)

    written = 0
    failed: list[str] = []
    for spec in specs:
        print(f"\n=== generating {spec.scenario_id} ({spec.target_type}, {spec.session_plan.total_sessions} sessions) ===")
        try:
            conv = asyncio.run(
                generate_conversation(
                    spec, gen_llm,
                    gold_tokens=gold_tokens, filler_tokens=filler_tokens,
                    last_k_verbatim=last_k_verbatim, max_retries=retries,
                )
            )
        except Exception as exc:  # noqa: BLE001 — keep going; report at the end
            print(f"  !! {spec.scenario_id} FAILED after retries: {type(exc).__name__}: {exc}")
            failed.append(spec.scenario_id)
            continue
        ok, detail = soft_validate_embedding(conv, spec)
        path = write_distilled_fixture([conv], work_dir / f"{spec.scenario_id}.json")
        written += 1
        flag = "ok" if ok else "DRIFT — review/regenerate"
        print(f"  soft embedding: {flag} — {detail}")
        print(f"  wrote {path}")
    print(f"\nGenerated {written}/{len(specs)} conversations into {work_dir}")
    if failed:
        print(f"FAILED ({len(failed)}): {', '.join(failed)} — re-run with --only <id> or raise --max-retries / --max-tokens")
    print("Next: uv run python -m cogmem_bench.gate")
    return 1 if failed else 0


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Generate benchmark conversations (Minimax, manual).")
    ap.add_argument("--specs-dir", default=str(PILOT_SPECS_DIR))
    ap.add_argument("--out-dir", default=str(DEFAULT_OUT_DIR))
    ap.add_argument("--only", default=None, help="generate a single scenario_id")
    ap.add_argument("--last-k", type=int, default=None,
                    help="recent sessions passed verbatim (overrides COGMEM_BENCH_GEN_LAST_K_VERBATIM; default 2)")
    ap.add_argument("--max-tokens", type=int, default=None,
                    help="max completion tokens for gold/trap sessions (overrides COGMEM_BENCH_GEN_MAX_TOKENS; default 16000)")
    ap.add_argument("--filler-max-tokens", type=int, default=None,
                    help="max completion tokens for filler sessions (overrides COGMEM_BENCH_GEN_FILLER_MAX_TOKENS; default 8000)")
    ap.add_argument("--max-retries", type=int, default=None,
                    help="per-session retry attempts (overrides COGMEM_BENCH_GEN_MAX_RETRIES; default 3)")
    ap.add_argument("--dry-run", action="store_true", help="render prompts only; no LLM calls")
    args = ap.parse_args(argv)
    return generate_all(
        Path(args.specs_dir), Path(args.out_dir), only=args.only, dry_run=args.dry_run,
        last_k=args.last_k, max_tokens=args.max_tokens, filler_max_tokens=args.filler_max_tokens,
        max_retries=args.max_retries,
    )


if __name__ == "__main__":
    sys.exit(main())
