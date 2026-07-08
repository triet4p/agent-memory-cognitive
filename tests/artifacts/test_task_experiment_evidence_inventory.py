"""Validate evidence files used by the experiment evidence inventory.

Run:
    uv run python tests/artifacts/test_task_experiment_evidence_inventory.py
"""

from __future__ import annotations

import csv
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def read_csv(path: str) -> list[dict[str, str]]:
    with (ROOT / path).open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def row_for(rows: list[dict[str, str]], scope: str, category: str) -> dict[str, str]:
    for row in rows:
        if row["scope"] == scope and row["category"] == category:
            return row
    raise AssertionError(f"missing row scope={scope!r} category={category!r}")


def judge_pass_count(directory: str, profile_id: str = "E7") -> tuple[int, int]:
    total = 0
    passed = 0
    for path in sorted((ROOT / directory).glob(f"{profile_id}_full_c*.json")):
        total += 1
        payload = json.loads(path.read_text(encoding="utf-8"))
        question = payload.get("questions", [{}])[0]
        judge = question.get("judge", {})
        score = judge.get("score")
        if judge.get("correct") is True or (
            isinstance(score, (int, float)) and score >= 0.7
        ):
            passed += 1
    return passed, total


def test_locomo_t8g_manual_accuracy_matches_chapter_table() -> None:
    rows = read_csv("logs/task_s35_t8g_accuracy_results.csv")
    full = row_for(rows, "full", "all")
    assert full["total"] == "161"
    assert full["pass_plus_partial"] == "119"
    assert full["pass_plus_partial_accuracy"] == "73.9%"

    expected = {
        "causal": ("11", "10", "90.9%"),
        "multi-hop": ("12", "11", "91.7%"),
        "preference": ("17", "15", "88.2%"),
        "single-hop": ("109", "78", "71.6%"),
        "temporal": ("12", "5", "41.7%"),
    }
    for category, (total, pass_plus_partial, accuracy) in expected.items():
        row = row_for(rows, "full", category)
        assert row["total"] == total
        assert row["pass_plus_partial"] == pass_plus_partial
        assert row["pass_plus_partial_accuracy"] == accuracy


def test_locomo_t8e_previous_baseline_is_available() -> None:
    rows = read_csv("logs/task_s35_t8e_accuracy_results.csv")
    full = row_for(rows, "full", "all")
    assert full["total"] == "161"
    assert full["pass_plus_partial"] == "97"
    assert full["pass_plus_partial_accuracy"] == "60.2%"


def test_sum_vs_max_summary_matches_chapter_table() -> None:
    path = ROOT / "experiments/v21_sum_vs_max_graph_only/sum_vs_max_graph_only_summary.json"
    payload = json.loads(path.read_text(encoding="utf-8"))
    profiles = {profile["profile_id"]: profile for profile in payload["profiles"]}
    assert profiles["E7G"]["case_count"] == 35
    assert round(profiles["E7G"]["mean_session_recall_at_5"], 3) == 0.805
    assert round(profiles["E7GM"]["mean_session_recall_at_5"], 3) == 0.762
    assert round(profiles["E7G"]["mean_session_recall_at_10"], 3) == 0.848
    assert round(profiles["E7GM"]["mean_session_recall_at_10"], 3) == 0.848
    assert payload["comparison"]["sum_better_at_5"] == 2
    assert payload["comparison"]["max_better_at_5"] == 0
    assert payload["comparison"]["tied_at_5"] == 33


def test_action_effect_agentic_report_contains_headline_numbers() -> None:
    text = (ROOT / "experiments/v19/action_effect_agentic/REPORT.md").read_text(
        encoding="utf-8"
    )
    assert "5/12 cases discriminate" in text
    assert "p ≈ 0.22" in text or "p ~= 0.22" in text
    assert "Manual" in text or "manual" in text


def test_longmemeval_auto_judge_and_verified_manual_are_distinct() -> None:
    auto_pass, auto_total = judge_pass_count("experiments/v15/checkpoints-s29-wave2e")
    assert (auto_pass, auto_total) == (31, 35)

    verdict = (
        ROOT / "experiments/v15/diagnose-s29-wave2e/VERDICTS.md"
    ).read_text(encoding="utf-8")
    assert re.search(r"35 total.*30 PASS", verdict)


if __name__ == "__main__":
    test_locomo_t8g_manual_accuracy_matches_chapter_table()
    test_locomo_t8e_previous_baseline_is_available()
    test_sum_vs_max_summary_matches_chapter_table()
    test_action_effect_agentic_report_contains_headline_numbers()
    test_longmemeval_auto_judge_and_verified_manual_are_distinct()
    print("experiment evidence inventory checks passed")
