from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
RESULTS = ROOT / "reports" / "final_reports" / "src" / "Chapter" / "5_Numerical_results.tex"
CONCLUSION = ROOT / "reports" / "final_reports" / "src" / "Chapter" / "6_Conclusions.tex"
APPENDIX_C = ROOT / "reports" / "final_reports" / "src" / "Chapter" / "Appendix_C.tex"
MAIN = ROOT / "reports" / "final_reports" / "src" / "main.tex"
SUMMARY = ROOT / "logs" / "task_report_final_polish_summary.md"


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_locomo_hindsight_baseline_and_improvement_are_reported() -> None:
    text = _read(RESULTS)
    assert "HINDSIGHT baseline & 161 & 105 & 65,2\\% \\\\" in text
    assert "CogMem tăng thêm 14 câu đạt" in text
    assert "cải thiện 8,7 điểm phần trăm" in text

    conclusion = _read(CONCLUSION)
    assert "baseline HINDSIGHT" in conclusion


def test_cogmem_bench_figure_explanations_are_inline_not_separate_subsection() -> None:
    text = _read(RESULTS)
    assert r"\subsection{Ý nghĩa của các hình minh họa CogMem Bench}" not in text

    intention_label = text.index(r"\label{fig:ch4_cogmem_bench_intention}")
    next_subsection = text.index(r"\subsection{Nút hành động--kết quả", intention_label)
    intention_block = text[intention_label:next_subsection]
    assert r"Hình \ref{fig:ch4_cogmem_bench_intention}" in intention_block
    assert "mất không gian biểu diễn cho trạng thái kế hoạch" in intention_block

    ae_label = text.index(r"\label{fig:ch4_cogmem_bench_action_effect}")
    following_summary = text.index("Trong số 12 kịch bản agentic", ae_label)
    ae_block = text[ae_label:following_summary]
    assert r"Hình \ref{fig:ch4_cogmem_bench_action_effect}" in ae_block
    assert "cấu trúc can thiệp cần thiết" in ae_block


def test_cogmem_bench_spec_structure_is_present() -> None:
    text = _read(RESULTS)
    assert r"\label{tab:cogmem_bench_spec_structure}" in text
    for phrase in [
        "Cấu trúc một đặc tả CogMem Bench",
        "Ví dụ cấu trúc hội thoại được sinh",
        r"\label{tab:cogmem_bench_dialogue_structure}",
        "Loại node mục tiêu",
        "Fact trung tâm",
        "Mảnh hội thoại bắt buộc",
        "Bẫy gây nhiễu",
        "ngân hàng loại bỏ không được tạo node",
    ]:
        assert phrase in text


def test_relation_transition_limitation_is_stated_in_results_and_conclusion() -> None:
    results = _read(RESULTS)
    conclusion = _read(CONCLUSION)
    for text in [results, conclusion]:
        assert "cô lập đóng góp theo" in text
        assert "experience--intention" in text
        assert "intention--experience" in text
        assert "kế hoạch" in text and "nhiều phiên" in text


def test_appendix_success_cases_are_added_and_referenced() -> None:
    results = _read(RESULTS)
    appendix = _read(APPENDIX_C)
    main = _read(MAIN)

    assert r"\ref{app:cogmem_bench_success_cases}" in results
    assert r"\subfile{Chapter/Appendix_C}" in main
    assert r"\label{app:cogmem_bench_success_cases}" in appendix

    for phrase in [
        "Cấu trúc đọc một kịch bản CogMem Bench",
        "Cấu trúc chung của một kịch bản CogMem Bench",
        "neg\\_intention\\_14",
        "pilot\\_intention\\_02",
        "agentic\\_ae\\_01\\_http\\_429",
        "composting",
        "bàn đứng",
        "HTTP 429",
        "Retry-After",
    ]:
        assert phrase in appendix


def test_required_summary_log_exists() -> None:
    assert SUMMARY.exists(), "missing required task summary log"
    summary = _read(SUMMARY)
    assert "Coverage Gate" in summary
    assert "5_Numerical_results.tex" in summary
    assert "Appendix_C.tex" in summary


def main() -> None:
    test_locomo_hindsight_baseline_and_improvement_are_reported()
    test_cogmem_bench_figure_explanations_are_inline_not_separate_subsection()
    test_cogmem_bench_spec_structure_is_present()
    test_relation_transition_limitation_is_stated_in_results_and_conclusion()
    test_appendix_success_cases_are_added_and_referenced()
    test_required_summary_log_exists()
    print("task_report_final_polish checks passed")


if __name__ == "__main__":
    main()
