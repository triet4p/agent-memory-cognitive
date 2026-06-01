"""Validate the hardcoded QA-to-conversation mapping in eval_cogmem_batch_locomo.ps1
against the actual data/locomo_distilled.json.

Run: uv run python scripts/locomo_mapping_dryrun.py

Exits 0 if the table matches; non-zero (with diff) if dataset has shifted and the
batch script needs an update.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
DATA = REPO_ROOT / "data" / "locomo_distilled.json"
SCRIPT = REPO_ROOT / "scripts" / "eval_cogmem_batch_locomo.ps1"


# The truth in the .ps1 (kept in sync manually). If you change one, change the other.
HARDCODED = [
    ("conv-30", 0, 13),
    ("conv-26", 14, 47),
    ("conv-43", 48, 93),
    ("conv-50", 94, 131),
    ("conv-47", 132, 160),
]


def derive_from_data() -> list[tuple[str, int, int]]:
    convs = json.loads(DATA.read_text(encoding="utf-8"))
    rows: list[tuple[str, int, int]] = []
    cursor = 0
    for c in convs:
        sid = c.get("sample_id", "?")
        n_qa = len(c.get("qa", []))
        if n_qa == 0:
            continue
        rows.append((sid, cursor, cursor + n_qa - 1))
        cursor += n_qa
    return rows


def main() -> int:
    derived = derive_from_data()

    print(f"Loaded {DATA.relative_to(REPO_ROOT)}")
    print()
    print(f"{'sample_id':12}  {'first':>5}  {'last':>5}  {'#qa':>4}")
    print("-" * 36)
    total = 0
    for sid, first, last in derived:
        n = last - first + 1
        total += n
        print(f"{sid:12}  {first:5d}  {last:5d}  {n:4d}")
    print(f"{'TOTAL':12}  {'':5}  {'':5}  {total:4d}")
    print()

    if derived == HARDCODED:
        print("OK — derived mapping matches hardcoded table in eval_cogmem_batch_locomo.ps1.")
        return 0

    print("MISMATCH — hardcoded table in .ps1 is stale!", file=sys.stderr)
    print(f"  hardcoded: {HARDCODED}", file=sys.stderr)
    print(f"  derived:   {derived}", file=sys.stderr)
    print(file=sys.stderr)
    print("Update the $CONV_RANGES array in scripts/eval_cogmem_batch_locomo.ps1 to:", file=sys.stderr)
    print("  $CONV_RANGES = @(", file=sys.stderr)
    for sid, first, last in derived:
        print(f'      @{{ SampleId = "{sid}"; First = {first};  Last = {last}  }},', file=sys.stderr)
    print("  )", file=sys.stderr)
    return 1


if __name__ == "__main__":
    sys.exit(main())
