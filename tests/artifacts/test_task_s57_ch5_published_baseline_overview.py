from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
CHAPTER = ROOT / "reports" / "final_reports" / "src" / "Chapter" / "5_Numerical_results.tex"


def main() -> None:
    text = CHAPTER.read_text(encoding="utf-8")

    config_groups = "\\subsection{Các cấu hình so sánh}"
    overview = "\\section{Kết quả tổng quan}"
    longmem = "\\section{Kết quả trên LongMemEval}"
    assert config_groups in text
    assert overview in text
    assert longmem in text
    assert text.index(config_groups) < text.index(overview) < text.index(longmem)

    for token in [
        "không nhằm khẳng định một so sánh trực tiếp tuyệt đối",
        "Full benchmark công bố",
        "Tập chắt lọc trong đồ án",
        "\\label{tab:longmemeval_published_overall_context}",
        "\\label{tab:locomo_published_overall_context}",
        "Full-context (GPT-4o)",
        "Supermemory (GPT-5)",
        "HINDSIGHT (OSS-120B) & Full benchmark công bố & -- & 89,0\\%",
        "CogMem multi-channel đầy đủ & Tập chắt lọc trong đồ án & 31/35 & 88,6\\%",
        "Backboard & Full benchmark công bố & -- & 90,00\\%",
        "Mem0-Graph & Full benchmark công bố & -- & 68,44\\%",
        "HINDSIGHT (Gemini-3) & Full benchmark công bố & -- & 89,61\\%",
        "CogMem cấu hình cuối & Tập chắt lọc trong đồ án & 119/161 & 73,9\\%",
    ]:
        assert token in text, token

    # The existing detailed dataset sections should remain present after the overview.
    for token in [
        "\\subsection{So sánh tổng quan các cấu hình}",
        "\\section{Kết quả trên LoCoMo}",
        "\\section{Đánh giá định tính trên CogMem Bench}",
    ]:
        assert token in text, token


if __name__ == "__main__":
    main()
