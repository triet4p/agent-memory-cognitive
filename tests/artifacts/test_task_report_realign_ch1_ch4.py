from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
REPORT_SRC = ROOT / "reports" / "final_reports" / "src"


def read(rel_path: str) -> str:
    return (ROOT / rel_path).read_text(encoding="utf-8", errors="replace")


def assert_main_tex_cleanup() -> None:
    main_tex = read("reports/final_reports/src/main.tex")
    assert "\\include{lstlisting}" not in main_tex, "Broken preamble include must be removed"
    assert "\\lstdefinestyle{cogmem}" in main_tex, "Global listings style must exist"
    assert "\\lstset{style=cogmem}" in main_tex, "Global listings style must be activated"
    assert "\\tcbuselibrary{breakable,listings,skins}" in main_tex, "tcolorbox listing libraries must be enabled"
    print("[ok] main.tex uses global cogmem listing style and no broken lstlisting include")


def assert_appendix_listing_mode() -> None:
    appendix_a = read("reports/final_reports/src/Chapter/Appendix_A.tex")
    appendix_b = read("reports/final_reports/src/Chapter/Appendix_B.tex")
    for label, content in [("Appendix_A", appendix_a), ("Appendix_B", appendix_b)]:
        assert "\\begin{verbatim}" not in content, f"{label} should not use verbatim blocks anymore"
        assert "\\begin{tcblisting}{" in content, f"{label} should use tcblisting for wrapped prompt boxes"
    print("[ok] appendices use tcblisting instead of verbatim blocks")


def assert_methodology_realignment() -> None:
    chapter3 = read("reports/final_reports/src/Chapter/3_Methodology.tex")
    chapter4 = read("reports/final_reports/src/Chapter/4_Theoretical_analysis.tex")

    assert "abandoned, triggered" not in chapter3, "Abandoned must not be described as a transition edge"
    assert "\\textit{abandoned} là một \\textit{intention\\_status}" in chapter3, "Methodology must clarify abandoned status semantics"
    assert "preference" in chapter3 and "multi\\_hop" in chapter3, "Adaptive routing should document current query types"
    assert "Entity" not in chapter3.split("\\label{tab:adaptive_rrf}")[1], "Stale Entity query type row must be removed"
    assert "\\sum_i w_i(q) = 1" not in chapter3, "Adaptive RRF weights should not be falsely documented as normalized"
    assert "không phải lúc nào cũng tạo lợi thế đồng đều" in chapter4, "Theoretical analysis should soften typed-network claim strength"
    assert "mang tính điều kiện" in chapter4, "Theoretical analysis should frame typed-network gains as conditional"
    assert "luôn tạo ra cải thiện đồng đều" in chapter3, "Methodology should explicitly reject universal typed-network gains"
    print("[ok] methodology/theory chapters reflect current transition semantics and adaptive routing")


def assert_build_log_targets() -> None:
    main_log = read("reports/final_reports/src/main.log")
    assert "No file lstlisting." not in main_log, "Build log should no longer report missing lstlisting include"
    assert "\\include should only be used after \\begin{document}" not in main_log, "Build log should not report preamble include misuse"
    assert "Package pgfkeys Error" not in main_log, "Appendix listing mode should compile without pgfkeys errors"
    assert "Output written on main.pdf" in main_log, "LaTeX build should emit a PDF"
    print("[ok] build log is free of the targeted listing/config regressions and produced main.pdf")


def main() -> None:
    assert REPORT_SRC.exists(), "report source directory missing"
    assert_main_tex_cleanup()
    assert_appendix_listing_mode()
    assert_methodology_realignment()
    assert_build_log_targets()
    print("PASS: report realignment and LaTeX listing fixes are locked in")


if __name__ == "__main__":
    main()
