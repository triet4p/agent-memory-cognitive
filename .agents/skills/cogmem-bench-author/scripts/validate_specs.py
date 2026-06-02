"""Validate ScenarioSpec JSON files against the schema.

Usage: uv run python .claude/skills/cogmem-bench-author/scripts/validate_specs.py --dir cogmem_bench/specs/pilot
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[4]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from pydantic import ValidationError

from cogmem_bench.schema import ScenarioSpec


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dir", required=True, help="directory of ScenarioSpec JSON files")
    args = ap.parse_args()

    files = sorted(Path(args.dir).glob("*.json"))
    if not files:
        print(f"no JSON files in {args.dir}")
        return 1

    ok = 0
    for f in files:
        try:
            spec = ScenarioSpec.model_validate_json(f.read_text(encoding="utf-8"))
        except ValidationError as exc:
            print(f"[FAIL] {f.name}\n{exc}\n")
            continue
        ok += 1
        print(f"[ok] {f.name:32} type={spec.target_type:13} sessions={spec.session_plan.total_sessions}")
    print(f"\n{ok}/{len(files)} specs valid")
    return 0 if ok == len(files) else 1


if __name__ == "__main__":
    sys.exit(main())
