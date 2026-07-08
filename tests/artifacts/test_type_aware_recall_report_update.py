from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def require_text(path: Path, snippets: list[str]) -> None:
    text = path.read_text(encoding="utf-8")
    missing = [snippet for snippet in snippets if snippet not in text]
    if missing:
        raise AssertionError(f"{path} is missing expected snippets: {missing}")


def main() -> None:
    chapter5 = ROOT / "reports/final_reports/src/Chapter/5_Numerical_results.tex"
    chapter6 = ROOT / "reports/final_reports/src/Chapter/6_Conclusions.tex"

    require_text(
        chapter5,
        [
            "\\subsection{Kiểm tra bằng chứng theo riêng từng loại node}",
            "nếu chỉ giữ riêng các fact thuộc loại node mục tiêu",
            "\\textit{action\\_effect}",
            "không nên tuyệt đối hóa từng loại node",
        ],
    )
    require_text(
        chapter6,
        [
            "\\subsection{Truy vấn ưu tiên theo loại node}",
            "ưu tiên hoặc mở rộng tìm kiếm trên những fact type tương ứng thay vì cào bằng mọi node",
            "truy vấn \\textit{prospective}",
            "truy vấn \\textit{causal}",
        ],
    )

    print("type-aware recall report update checks passed")


if __name__ == "__main__":
    main()
