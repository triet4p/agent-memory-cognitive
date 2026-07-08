from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
CHAPTER = ROOT / "reports" / "final_reports" / "src" / "Chapter" / "5_Numerical_results.tex"


def main() -> None:
    text = CHAPTER.read_text(encoding="utf-8")

    section = "\\section{Thiết kế thực nghiệm}"
    config = "\\subsection{Cấu hình thực nghiệm và mô hình sử dụng}"
    eval_flow = "\\subsection{Luồng đánh giá tổng quát}"
    assert section in text
    assert config in text
    assert eval_flow in text
    assert text.index(section) < text.index(config) < text.index(eval_flow)

    for token in [
        "\\label{tab:experiment_runtime_config}",
        "Ministral3-3B",
        "BAAI/bge-small-en-v1.5",
        "cross-encoder/ms-marco-MiniLM-L-6-v2",
        "MiniMax-M2.7",
        "BFS + SUM activation",
        "LLM-as-a-Judge",
        "tắt bước này để cô lập ảnh hưởng của cơ chế đồ thị",
        "các memory bank đã nạp sẵn",
    ]:
        assert token in text, token

    for inconsistent_name in ["minimax-m2.7", "Minimax-M2.7"]:
        assert inconsistent_name not in text, inconsistent_name

    # The new subsection should be additive and should not remove existing early content.
    for existing in [
        "Toàn bộ thí nghiệm được thiết kế theo luồng đánh giá ngoại tuyến",
        "\\subsection{Chắt lọc dữ liệu}",
        "\\section{Kết quả trên LongMemEval}",
    ]:
        assert existing in text, existing


if __name__ == "__main__":
    main()
