"""Artifact check for the T8G full evaluation checkpoints and manual metrics."""

from __future__ import annotations

import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
CHECKPOINT_DIR = ROOT / "experiments" / "v20_t8g_evidence_guard" / "checkpoints"
CSV_PATH = ROOT / "logs" / "task_s35_t8g_accuracy_results.csv"
VERDICTS_PATH = ROOT / "logs" / "task_s35_t8g_full_manual_verdicts.md"


def _assert_checkpoints_complete() -> None:
    expected_names = [f"E7_full_c{index:03d}.json" for index in range(161)]
    missing = [name for name in expected_names if not (CHECKPOINT_DIR / name).exists()]
    assert not missing, f"Missing T8G full checkpoints: {missing}"

    for name in expected_names:
        path = CHECKPOINT_DIR / name
        with path.open("r", encoding="utf-8") as handle:
            json.load(handle)


def _load_metric_rows() -> dict[tuple[str, str], dict[str, str]]:
    assert CSV_PATH.exists(), f"Missing accuracy CSV: {CSV_PATH}"
    with CSV_PATH.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        rows = {(row["scope"], row["category"]): row for row in reader}
    assert rows, "Accuracy CSV has no rows"
    return rows


def _assert_manual_metrics() -> None:
    rows = _load_metric_rows()
    full = rows[("full", "all")]
    single_hop = rows[("full", "single-hop")]
    multi_hop = rows[("full", "multi-hop")]

    assert int(full["total"]) == 161
    assert int(full["pass_plus_partial"]) == 119
    assert int(full["pass_plus_partial"]) >= 113
    assert full["pass_plus_partial_accuracy"] == "73.9%"

    assert int(single_hop["pass_plus_partial"]) == 78
    assert int(single_hop["pass_plus_partial"]) > 62

    assert int(multi_hop["pass_plus_partial"]) == 11
    assert int(multi_hop["pass_plus_partial"]) > 8


def _assert_manual_verdict_log() -> None:
    assert VERDICTS_PATH.exists(), f"Missing manual verdict log: {VERDICTS_PATH}"
    text = VERDICTS_PATH.read_text(encoding="utf-8")
    for marker in (
        "| c000 | PASS |",
        "| c063 | PASS |",
        "| c077 | PARTIAL |",
        "| c094 | PASS |",
        "| c123 | PASS |",
        "| c124 | PASS |",
        "| c160 | PASS |",
    ):
        assert marker in text, f"Missing verdict marker: {marker}"


def main() -> int:
    _assert_checkpoints_complete()
    _assert_manual_metrics()
    _assert_manual_verdict_log()
    print("T8G full checkpoint completeness artifact passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
