from __future__ import annotations

import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
CONCLUSION = ROOT / "reports" / "final_reports" / "src" / "Chapter" / "6_Conclusions.tex"
SUMMARY = ROOT / "logs" / "task_conclusion_qualitative_summary.md"


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _section_between(text: str, start: str, end: str) -> str:
    match = re.search(
        rf"{re.escape(start)}(.*?){re.escape(end)}",
        text,
        flags=re.DOTALL,
    )
    assert match, f"missing section between {start} and {end}"
    return match.group(1)


def test_conclusion_is_expanded_for_thesis_style() -> None:
    text = _read(CONCLUSION)

    required_headings = [
        r"\section{Kết luận}",
        r"\subsection{Mức độ hoàn thành mục tiêu}",
        r"\subsection{Các đóng góp chính}",
        r"\subsection{Diễn giải kết quả thực nghiệm}",
        r"\subsection{Bài học thiết kế}",
        r"\section{Hạn chế}",
        r"\subsection{Biểu diễn bộ nhớ}",
        r"\subsection{Truy vấn và xếp hạng bằng chứng}",
        r"\subsection{Tổng hợp câu trả lời}",
        r"\subsection{Thiết kế đánh giá}",
        r"\section{Hướng phát triển}",
        r"\subsection{Đánh giá quan hệ chuyển giao}",
        r"\subsection{Suy luận thời gian và truy vấn danh sách}",
        r"\subsection{CogMem Bench mở rộng}",
        r"\subsection{Ứng dụng trong tác nhân AI}",
        r"\subsection{Hiệu năng vận hành}",
    ]
    for heading in required_headings:
        assert heading in text, f"missing thesis-style heading: {heading}"

    assert r"\subsection{Kết quả chính}" not in text, "old concise conclusion heading remains"


def test_conclusion_synthesis_is_not_chapter4_metric_recap() -> None:
    text = _read(CONCLUSION)
    section = _section_between(text, r"\section{Kết luận}", r"\section{Hạn chế}")

    for repeated_metric in [
        "30/35",
        "31/35",
        "119/161",
        "105/161",
        "0,762",
        "0,805",
        "90--120",
        "1500 node",
    ]:
        assert repeated_metric not in section, f"metric repetition leaked: {repeated_metric}"

    required_qualitative_points = [
        "không chỉ là xây dựng một hệ thống có thể lưu thêm nhiều đoạn hội thoại cũ",
        "tầng biểu diễn và truy vấn độc lập",
        "giá trị theo điều kiện",
        "CogMem Bench không chỉ đóng vai trò phụ trợ",
        "không nên đánh đồng ``nhớ'' với ``tìm lại đoạn văn giống câu hỏi''",
    ]
    for phrase in required_qualitative_points:
        assert phrase in section, f"missing qualitative conclusion: {phrase}"


def test_limitations_and_future_work_are_substantive() -> None:
    text = _read(CONCLUSION)
    limitations = _section_between(text, r"\section{Hạn chế}", r"\section{Hướng phát triển}")
    future = text[text.index(r"\section{Hướng phát triển}") :]

    for phrase in [
        "quan hệ chuyển giao",
        "experience--intention",
        "intention--experience",
        "suy luận thời gian",
        "tầng tổng hợp",
        "phạm vi đánh giá",
    ]:
        assert phrase in limitations, f"missing limitation detail: {phrase}"

    for phrase in [
        "quan hệ chuyển giao giữa các loại fact",
        "câu hỏi dạng danh sách",
        "rò rỉ thông tin",
        "retain tăng dần",
        "cache",
        "CrossEncoder",
    ]:
        assert phrase in future, f"missing future-work detail: {phrase}"


def test_required_summary_log_exists() -> None:
    assert SUMMARY.exists(), "missing required task summary log"
    summary = _read(SUMMARY)
    assert "Coverage Gate" in summary
    assert "6_Conclusions.tex" in summary


def main() -> None:
    test_conclusion_is_expanded_for_thesis_style()
    test_conclusion_synthesis_is_not_chapter4_metric_recap()
    test_limitations_and_future_work_are_substantive()
    test_required_summary_log_exists()
    print("task_conclusion_qualitative checks passed")


if __name__ == "__main__":
    main()
