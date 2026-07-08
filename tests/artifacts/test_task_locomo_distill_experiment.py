"""Validate the reorganized LoCoMo distill experiment folder.

Run with:
    uv run python tests/artifacts/test_task_locomo_distill_experiment.py
"""

from __future__ import annotations

import csv
import json
import runpy
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
OUT_DIR = ROOT / "experiments" / "locomo-distill"


EXPECTED = {
    "00_t8e_3bank_97_161": {
        "csv": "task_s35_t8e_accuracy_results.csv",
        "source": "experiments\\v20_t8e_3bank",
        "pass_plus_partial": 97,
    },
    "01_t8g_evidence_guard_119_161": {
        "csv": "task_s35_t8g_accuracy_results.csv",
        "source": "experiments\\v20_t8g_evidence_guard",
        "pass_plus_partial": 119,
    },
}


def full_all_row(path: Path) -> dict[str, str]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    matches = [row for row in rows if row["scope"] == "full" and row["category"] == "all"]
    assert len(matches) == 1
    return matches[0]


def main() -> None:
    runpy.run_path(str(ROOT / "scripts" / "build_locomo_distill_experiment.py"), run_name="__main__")

    manifest = json.loads((OUT_DIR / "manifest.json").read_text(encoding="utf-8"))
    assert manifest["copied_without_edits"] is True
    assert len(manifest["runs"]) == 2

    runs = {run["folder"]: run for run in manifest["runs"]}
    assert set(runs) == set(EXPECTED)

    for folder, expected in EXPECTED.items():
        run = runs[folder]
        assert run["source_experiment"] == expected["source"]
        assert run["copied_csv"] == expected["csv"]
        assert run["checkpoint_count"] == 161
        assert run["pass_plus_partial"] == expected["pass_plus_partial"]
        assert run["total"] == 161

        checkpoint_files = sorted((OUT_DIR / folder / "checkpoints").glob("E7_full_c*.json"))
        assert len(checkpoint_files) == 161

        row = full_all_row(OUT_DIR / folder / expected["csv"])
        assert int(row["total"]) == 161
        assert int(row["pass_plus_partial"]) == expected["pass_plus_partial"]

        summary = json.loads((OUT_DIR / folder / "summary.json").read_text(encoding="utf-8"))
        assert summary["copied_without_edits"] is True
        assert summary["pass_plus_partial"] == expected["pass_plus_partial"]

    print("locomo-distill experiment folder verified")


if __name__ == "__main__":
    main()
