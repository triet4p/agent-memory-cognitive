from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
CHAPTER2 = ROOT / "reports" / "final_reports" / "src" / "Chapter" / "2_Literature_review.tex"
SUMMARY = ROOT / "logs" / "task_report_ch2_reranking_summary.md"


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_chapter2_adds_crossencoder_theory_section() -> None:
    text = _read(CHAPTER2)
    heading = r"\subsection{Xếp hạng lại bằng CrossEncoder trong truy vấn bộ nhớ}"
    assert text.count(heading) == 1

    graph_section = text.index(r"\subsection{Đồ thị tri thức và truy vấn nhiều bước}")
    rerank_section = text.index(heading)
    related_section = text.index(r"\section{Các hướng nghiên cứu liên quan}")
    assert graph_section < rerank_section < related_section


def test_chapter2_explains_reranking_and_crossencoder_terms() -> None:
    text = _read(CHAPTER2)
    required_phrases = [
        "truy vấn thường được chia thành hai tầng",
        "Tầng đầu tiên có nhiệm vụ tìm nhanh một tập ứng viên rộng",
        "\\textbf{Xếp hạng lại} (reranking)",
        "sắp xếp chúng theo mức độ phù hợp với câu hỏi",
        "Reciprocal Rank Fusion",
        "đánh giá trực tiếp từng cặp \\textit{câu hỏi--bằng chứng}",
        "mô hình hai bộ mã hóa",
        "câu hỏi và bằng chứng được mã hóa riêng thành hai vector",
        "CrossEncoder đưa cả câu hỏi và bằng chứng vào cùng một mô hình",
        "phủ định, trạng thái đã hoàn thành hay chưa hoàn thành",
        "mỗi cặp câu hỏi--bằng chứng phải được chạy qua mô hình một lần",
        "đứng sau tầng truy vấn nhanh",
        "đưa vào prompt cho LLM",
    ]
    for phrase in required_phrases:
        assert phrase in text, f"missing explanation phrase: {phrase}"


def test_chapter2_reranking_section_avoids_code_jargon() -> None:
    text = _read(CHAPTER2)
    start = text.index(r"\subsection{Xếp hạng lại bằng CrossEncoder trong truy vấn bộ nhớ}")
    end = text.index(r"\section{Các hướng nghiên cứu liên quan}")
    section = text[start:end]

    for banned in ["top_k", "reranker_used", "CE score", "arm nội bộ", "field"]:
        assert banned not in section, f"code-oriented wording leaked: {banned}"


def test_required_summary_log_exists() -> None:
    assert SUMMARY.exists(), "missing required task summary log"
    summary = _read(SUMMARY)
    assert "2_Literature_review.tex" in summary
    assert "Coverage Gate" in summary


def main() -> None:
    test_chapter2_adds_crossencoder_theory_section()
    test_chapter2_explains_reranking_and_crossencoder_terms()
    test_chapter2_reranking_section_avoids_code_jargon()
    test_required_summary_log_exists()
    print("task_report_ch2_reranking checks passed")


if __name__ == "__main__":
    main()
