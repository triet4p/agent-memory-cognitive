"""S35-T8 probe artifact: sparse LoCoMo batch eval indices.

Verifies the LoCoMo batch script supports targeted probes without running a
contiguous START_INDEX..END_INDEX range.

Run: uv run python tests/artifacts/test_task_s35_t8_probe_subset.py
"""

from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT = REPO_ROOT / "scripts" / "eval_cogmem_batch_locomo.ps1"


def test_sparse_indices_parameter_exists() -> None:
    text = SCRIPT.read_text(encoding="utf-8")
    assert "[int[]]$INDICES" in text
    assert "QA_INDICES" in text
    print("[ok] batch script exposes -INDICES sparse probe parameter")


def test_sparse_indices_override_range_loop() -> None:
    text = SCRIPT.read_text(encoding="utf-8")
    assert '$evalIndices = if ($INDICES.Count -gt 0) { $INDICES } else { $START_INDEX..$END_INDEX }' in text
    assert "foreach ($N in $evalIndices)" in text
    assert "for ($N = $START_INDEX" not in text
    print("[ok] sparse -INDICES overrides contiguous START_INDEX..END_INDEX loop")


def main() -> int:
    test_sparse_indices_parameter_exists()
    test_sparse_indices_override_range_loop()
    print("\nS35-T8 PROBE SUBSET PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
