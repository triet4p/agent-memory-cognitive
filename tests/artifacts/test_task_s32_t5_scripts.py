"""S32-T5 artifact: pilot specs load + standalone generate/gate script wiring (offline).

The live runs (generation via Minimax; gating via Ministral + API) are manual:
  uv run python -m cogmem_bench.generate
  uv run python -m cogmem_bench.gate

Run: uv run python tests/artifacts/test_task_s32_t5_scripts.py
"""

from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from cogmem_bench.datasets import PILOT_SPECS_DIR, load_specs, work_fixture_path
from cogmem_bench.generate import generate_all


def test_six_pilot_specs_valid() -> None:
    specs = load_specs(PILOT_SPECS_DIR)
    assert len(specs) == 6, f"expected 6 pilot specs, got {len(specs)}"
    by_type: dict[str, int] = {}
    for s in specs:
        by_type[s.target_type] = by_type.get(s.target_type, 0) + 1
    assert by_type == {"intention": 2, "action_effect": 2, "habit": 2}, by_type
    print(f"[ok] 6 valid pilot specs, 2 per type: {by_type}")


def test_generate_dry_run() -> None:
    rc = generate_all(PILOT_SPECS_DIR, REPO_ROOT / "data" / "bench", only=None, dry_run=True)
    assert rc == 0
    print("[ok] generate.py dry-run renders all per-session prompts")


def test_work_fixture_path_helper() -> None:
    p = work_fixture_path(REPO_ROOT / "data" / "bench", "pilot_habit_01")
    assert p.name == "pilot_habit_01.json"
    assert p.parent.name == "work"
    print("[ok] work_fixture_path resolves correctly")


def main() -> int:
    test_six_pilot_specs_valid()
    test_generate_dry_run()
    test_work_fixture_path_helper()
    print("\nS32-T5 PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
