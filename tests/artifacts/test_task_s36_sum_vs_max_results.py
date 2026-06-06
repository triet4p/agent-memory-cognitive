from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
EXP = ROOT / "experiments" / "v21_sum_vs_max_graph_only"
SUMMARY_JSON = EXP / "sum_vs_max_graph_only_summary.json"
SUMMARY_MD = EXP / "SUM_VS_MAX_GRAPH_ONLY.md"
CHECKPOINT_DIR = EXP / "checkpoints"
SCRIPT = ROOT / "scripts" / "compare_sum_max_graph_only.py"
LOG = ROOT / "logs" / "task_s36_sum_vs_max_graph_only_summary.md"


def _read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def test_live_sum_vs_max_outputs_exist() -> None:
    assert SCRIPT.exists(), "missing reusable SUM/MAX comparison runner"
    assert SUMMARY_JSON.exists(), "missing live summary JSON"
    assert SUMMARY_MD.exists(), "missing live summary markdown"
    assert LOG.exists(), "missing task summary log"

    checkpoints = sorted(CHECKPOINT_DIR.glob("*_recall_c*.json"))
    assert len(checkpoints) == 70, f"expected 70 recall checkpoints, got {len(checkpoints)}"
    assert len(list(CHECKPOINT_DIR.glob("E7G_recall_c*.json"))) == 35
    assert len(list(CHECKPOINT_DIR.glob("E7GM_recall_c*.json"))) == 35


def test_live_sum_beats_max_at_top5_and_never_loses() -> None:
    summary = _read_json(SUMMARY_JSON)
    profiles = {item["profile_id"]: item for item in summary["profiles"]}
    comparison = summary["comparison"]

    assert profiles["E7G"]["case_count"] == 35
    assert profiles["E7GM"]["case_count"] == 35
    assert profiles["E7G"]["mean_session_recall_at_5"] > profiles["E7GM"]["mean_session_recall_at_5"]
    assert comparison["delta_mean_session_recall_at_5"] > 0.0
    assert comparison["sum_better_at_5"] == 2
    assert comparison["max_better_at_5"] == 0
    assert comparison["different_top10_doc_order_cases"] >= 10


def test_case_studies_capture_sum_advantage() -> None:
    summary = _read_json(SUMMARY_JSON)
    cases = {row["index"]: row for row in summary["per_case"]}

    assert cases[11]["delta_session_recall_at_5"] == 0.5
    assert cases[30]["delta_session_recall_at_5"] == 1.0
    assert cases[11]["top10_doc_order_differs"] is True
    assert cases[30]["top10_doc_order_differs"] is True

    report_text = SUMMARY_MD.read_text(encoding="utf-8")
    assert "Mean session recall@5" in report_text
    assert "SUM better cases@5: `2`" in report_text
    assert "MAX better cases@5: `0`" in report_text


if __name__ == "__main__":
    test_live_sum_vs_max_outputs_exist()
    test_live_sum_beats_max_at_top5_and_never_loses()
    test_case_studies_capture_sum_advantage()
    print("task_s36_sum_vs_max_results artifact checks passed")
