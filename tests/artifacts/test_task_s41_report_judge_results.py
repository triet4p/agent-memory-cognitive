from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "reports" / "final_reports" / "src"


def _read(relative: str) -> str:
    return (SRC / relative).read_text(encoding="utf-8")


def test_abstract_is_vietnamese_and_keeps_high_level_scope() -> None:
    abstract = _read("Chapter/0_3_Abstract.tex")

    for token in ["TÓM TẮT", "Agent hội thoại dài hạn", "Đồ án này trình bày", "chiều hướng cải thiện tích cực"]:
        assert token in abstract, f"missing abstract requirement: {token}"

    forbidden = [
        "30/35",
        "31/35",
        "119/161",
        "90--120 phút",
        "700 node",
        "semantic, BM25, graph và temporal channels",
        "world, experience, opinion, habit, intention, action\\_effect",
    ]
    for token in forbidden:
        assert token not in abstract, f"abstract should stay high-level, but still contains: {token}"


def test_chapter_5_uses_judge_metric_without_internal_versions() -> None:
    chapter_5 = _read("Chapter/5_Numerical_results.tex")

    forbidden = [
        "LongMemEval v16",
        "manual PASS",
        "Manual PASS",
        "judge.correct ignored",
        "Manual Verdict",
        "PASS+PARTIAL",
        "Images/manual_evaluation_flow.png",
    ]
    for token in forbidden:
        assert token not in chapter_5, f"forbidden chapter 5 wording remains: {token}"

    for token in [
        "PASS theo LLM-as-a-judge",
        "nhãn judge là nguồn đánh giá chính",
        "HINDSIGHT baseline & 30/35 & 85.7\\%",
        "Multi-channel + 6 node types & 31/35 & 88.6\\%",
        "Multi-channel + 5 node types, bỏ habit & 31/35 & 88.6\\%",
        "Multi-channel + 5 node types, bỏ action-effect & 29/35 & 82.9\\%",
        "Multi-channel + 5 node types, bỏ intention & 29/35 & 82.9\\%",
        "Graph-only + 6 node types & 26/35 & 74.3\\%",
        "Graph-only + 5 node types, bỏ habit & 27/35 & 77.1\\%",
        "Graph-only + 5 node types, bỏ action-effect & 24/35 & 68.6\\%",
        "Graph-only + 5 node types, bỏ intention & 24/35 & 68.6\\%",
        "Graph-only + 3 node types gốc kiểu HINDSIGHT & 22/35 & 62.9\\%",
    ]:
        assert token in chapter_5, f"missing requested chapter 5 result: {token}"


def test_retain_efficiency_comparison_is_reported() -> None:
    chapter_5 = _read("Chapter/5_Numerical_results.tex")
    chapter_6 = _read("Chapter/6_Conclusions.tex")
    combined = chapter_5 + "\n" + chapter_6

    for token in [
        "So sánh hiệu năng retain",
        "Ministral3-3B",
        "90--120 phút",
        "khoảng 30 phút",
        "khoảng 1500 node",
        "khoảng 700 node",
        "nhanh hơn khoảng ba lần",
        "dưới một nửa",
    ]:
        assert token in combined, f"missing retain efficiency detail: {token}"


if __name__ == "__main__":
    test_abstract_is_vietnamese_and_keeps_high_level_scope()
    test_chapter_5_uses_judge_metric_without_internal_versions()
    test_retain_efficiency_comparison_is_reported()
    print("task_s41_report_judge_results artifact checks passed")
