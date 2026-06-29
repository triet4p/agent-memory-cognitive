from __future__ import annotations

import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
CH4 = ROOT / "reports" / "final_reports" / "src" / "Chapter" / "5_Numerical_results.tex"
CH5 = ROOT / "reports" / "final_reports" / "src" / "Chapter" / "6_Conclusions.tex"
APPENDIX_A = ROOT / "reports" / "final_reports" / "src" / "Chapter" / "Appendix_A.tex"
APPENDIX_B = ROOT / "reports" / "final_reports" / "src" / "Chapter" / "Appendix_B.tex"
APPENDIX_C = ROOT / "reports" / "final_reports" / "src" / "Chapter" / "Appendix_C.tex"
SUMMARY = ROOT / "logs" / "task_heading_appendix_polish_summary.md"


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_headings_are_nominal_not_sentence_like() -> None:
    ch4 = _read(CH4)
    ch5 = _read(CH5)

    for old_heading in [
        r"\subsubsection{Tại sao cần chắt lọc dữ liệu}",
        r"\subsection{Node ý định: khi kế hoạch chưa hoàn thành là thông tin quyết định}",
        r"\subsection{Node hành động--kết quả: khi cần nhớ quan hệ điều kiện, hành động và kết quả}",
        r"\subsection{Đối chiếu với mục tiêu đồ án}",
        r"\subsection{Cải thiện suy luận thời gian và danh sách}",
        r"\subsection{Triển khai trong tác nhân AI thực tế}",
    ]:
        assert old_heading not in ch4 + ch5, f"old sentence-like heading remains: {old_heading}"

    for new_heading in [
        r"\subsubsection{Lý do chắt lọc dữ liệu}",
        r"\subsection{Nút ý định và kế hoạch chưa hoàn thành}",
        r"\subsection{Nút hành động--kết quả và quan hệ can thiệp}",
        r"\subsection{Mức độ hoàn thành mục tiêu}",
        r"\subsection{Suy luận thời gian và truy vấn danh sách}",
        r"\subsection{Ứng dụng trong tác nhân AI}",
    ]:
        assert new_heading in ch4 + ch5, f"missing polished heading: {new_heading}"


def test_appendices_do_not_self_number_subsections() -> None:
    appendix_text = "\n".join([_read(APPENDIX_A), _read(APPENDIX_B), _read(APPENDIX_C)])
    assert not re.search(r"\\subsection\{[ABC]\.\d+\.", appendix_text)

    for heading in [
        r"\subsection{Prompt Trích xuất Pass 1 (Fact Extraction)}",
        r"\subsection{Prompt Tinh chỉnh Pass 2 (Persona-Focused Revision)}",
        r"\subsection{Prompt Tổng hợp Câu trả lời (Reflection \& Generation)}",
        r"\subsection{Prompt Chấm điểm Tự động (LLM-as-a-Judge)}",
        r"\subsection{Ý định chưa hoàn thành: composting}",
        r"\subsection{Ý định đã hoàn tất: bàn đứng}",
        r"\subsection{Hành động--kết quả: HTTP 429 với Retry-After}",
    ]:
        assert heading in appendix_text, f"missing unnumbered appendix heading: {heading}"


def test_cogmem_bench_dialogue_and_appendix_structure_are_explicit() -> None:
    ch4 = _read(CH4)
    appendix_c = _read(APPENDIX_C)

    for phrase in [
        r"\label{tab:cogmem_bench_dialogue_structure}",
        "Ví dụ cấu trúc hội thoại được sinh",
        "Phiên nêu kế hoạch",
        "Phiên gây nhiễu",
        "Phiên cập nhật trạng thái",
    ]:
        assert phrase in ch4, f"missing generated-dialogue structure in Chapter 4: {phrase}"

    for phrase in [
        r"\label{tab:appendix_cogmem_bench_case_structure}",
        "Cấu trúc đọc một kịch bản CogMem Bench",
        "Điều kiện phân biệt",
        "Cấu trúc kịch bản",
        "điều kiện--hành động--kết quả",
    ]:
        assert phrase in appendix_c, f"missing Appendix C case-structure detail: {phrase}"


def test_required_summary_log_exists() -> None:
    assert SUMMARY.exists(), "missing required task summary log"
    summary = _read(SUMMARY)
    assert "Coverage Gate" in summary
    assert "Appendix_C.tex" in summary
    assert "5_Numerical_results.tex" in summary


def main() -> None:
    test_headings_are_nominal_not_sentence_like()
    test_appendices_do_not_self_number_subsections()
    test_cogmem_bench_dialogue_and_appendix_structure_are_explicit()
    test_required_summary_log_exists()
    print("task_heading_appendix_polish checks passed")


if __name__ == "__main__":
    main()
