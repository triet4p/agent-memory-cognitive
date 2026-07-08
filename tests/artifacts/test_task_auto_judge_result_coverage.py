"""Validate final-report auto-judge coverage artifacts.

Run with:
    uv run python tests/artifacts/test_task_auto_judge_result_coverage.py
"""

from __future__ import annotations

import csv
import json
import runpy
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
OUT_DIR = ROOT / "experiments" / "final_report_auto_judge_coverage"


def read_csv(name: str) -> list[dict[str, str]]:
    with (OUT_DIR / name).open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def assert_row(rows: list[dict[str, str]], key: str, value: str) -> dict[str, str]:
    matches = [row for row in rows if row[key] == value]
    assert len(matches) == 1, f"expected one row where {key}={value!r}, got {len(matches)}"
    return matches[0]


def main() -> None:
    runpy.run_path(str(ROOT / "scripts" / "build_auto_judge_result_coverage.py"), run_name="__main__")

    coverage = json.loads((OUT_DIR / "auto_judge_table_coverage.json").read_text(encoding="utf-8"))
    assert coverage["excluded"] == ["tab:retain_efficiency_comparison"]
    assert "tab:longmemeval_results" in coverage["covered_tables"]
    assert "tab:locomo_full_accuracy" in coverage["covered_tables"]
    assert "tab:locomo_category_breakdown" in coverage["covered_tables"]
    assert "tab:sum_vs_max_graph_only" in coverage["covered_tables"]

    long_rows = read_csv("longmemeval_ablation_auto_judge.csv")
    assert len(long_rows) == 10
    full = assert_row(long_rows, "report_row", "Multi-channel full six fact types")
    assert (full["auto_pass"], full["auto_total"], full["coverage_status"]) == ("31", "35", "direct_match")
    no_ae = assert_row(long_rows, "report_row", "Multi-channel without action_effect")
    assert (no_ae["auto_pass"], no_ae["auto_total"], no_ae["coverage_status"]) == ("29", "35", "direct_match")
    graph_full = assert_row(long_rows, "report_row", "Graph-only full six fact types")
    assert (graph_full["auto_pass"], graph_full["auto_total"]) == ("25", "35")

    locomo_rows = read_csv("locomo_full_accuracy_auto_judge.csv")
    final = assert_row(locomo_rows, "report_row", "CogMem evidence-guard final")
    assert (final["auto_pass"], final["auto_total"]) == ("115", "161")

    category_rows = read_csv("locomo_category_breakdown_auto_judge.csv")
    assert sum(int(row["auto_pass"]) for row in category_rows) == 115
    assert sum(int(row["auto_total"]) for row in category_rows) == 161

    bench_rows = read_csv("cogmem_bench_auto_judge.csv")
    action = assert_row(bench_rows, "scenario", "all_agentic_ae")
    assert action["auto_judge_result"] == "3/12 discriminating"
    neg_all = assert_row(bench_rows, "scenario", "all_neg_intention")
    assert neg_all["auto_judge_result"] == "2/16 discriminating"
    neg14 = assert_row(bench_rows, "scenario", "neg_intention_14")
    assert neg14["auto_judge_result"] == "E7=True; E9F=False"

    sum_rows = read_csv("sum_vs_max_graph_only.csv")
    sum_variant = assert_row(sum_rows, "profile", "E7G")
    max_variant = assert_row(sum_rows, "profile", "E7GM")
    assert sum_variant["mean_session_recall_at_5"] == "0.805238"
    assert max_variant["mean_session_recall_at_5"] == "0.762381"

    print("auto-judge result coverage artifacts verified")


if __name__ == "__main__":
    main()
