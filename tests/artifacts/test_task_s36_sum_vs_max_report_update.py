from __future__ import annotations

import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "reports" / "final_reports" / "src"
SUMMARY = ROOT / "experiments" / "v21_sum_vs_max_graph_only" / "sum_vs_max_graph_only_summary.json"


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _summary() -> dict:
    return json.loads(SUMMARY.read_text(encoding="utf-8"))


def test_sum_vs_max_numbers_are_in_thesis() -> None:
    assert SUMMARY.exists(), "missing SUM/MAX live experiment summary"
    summary = _summary()
    profiles = {item["profile_id"]: item for item in summary["profiles"]}
    comparison = summary["comparison"]

    chapter_5 = _read(SRC / "Chapter" / "5_Numerical_results.tex")
    chapter_6 = _read(SRC / "Chapter" / "6_Conclusions.tex")
    abstract = _read(SRC / "Chapter" / "0_3_Abstract.tex")
    report = abstract + chapter_5 + chapter_6

    expected_values = [
        profiles["E7G"]["mean_session_recall_at_5"],
        profiles["E7GM"]["mean_session_recall_at_5"],
        profiles["E7G"]["mean_session_recall_at_10"],
        comparison["delta_mean_session_recall_at_5"],
    ]
    for value in expected_values:
        assert f"{value:.4f}" in report, f"missing SUM/MAX value in thesis: {value:.4f}"

    assert "SUM tốt hơn MAX ở 2 câu" in chapter_5
    assert "MAX không tốt hơn SUM ở câu nào" in chapter_5 + chapter_6
    assert "12/35" in chapter_5


def test_thesis_claim_is_scoped_to_graph_only_channel() -> None:
    chapter_3 = _read(SRC / "Chapter" / "3_Methodology.tex")
    chapter_5 = _read(SRC / "Chapter" / "5_Numerical_results.tex")
    chapter_6 = _read(SRC / "Chapter" / "6_Conclusions.tex")
    report = chapter_3 + chapter_5 + chapter_6

    for token in [
        "cùng graph-only recall",
        "chỉ dùng graph channel",
        "graph-only channel",
        "không phủ định kết luận lớn hơn",
        "multi-channel retrieval",
    ]:
        assert token in report, f"missing scoped claim language: {token}"


def test_no_internal_sum_max_ids_leak_into_thesis() -> None:
    report = "\n".join(
        _read(path)
        for path in [
            SRC / "Chapter" / "0_3_Abstract.tex",
            SRC / "Chapter" / "3_Methodology.tex",
            SRC / "Chapter" / "5_Numerical_results.tex",
            SRC / "Chapter" / "6_Conclusions.tex",
        ]
    )
    assert "E7G" not in report
    assert "E7GM" not in report
    assert not re.search(r"\bc[0-9]{3}\b", report), "internal case id leaked into thesis"


if __name__ == "__main__":
    test_sum_vs_max_numbers_are_in_thesis()
    test_thesis_claim_is_scoped_to_graph_only_channel()
    test_no_internal_sum_max_ids_leak_into_thesis()
    print("task_s36_sum_vs_max_report_update artifact checks passed")
