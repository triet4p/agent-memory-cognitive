from __future__ import annotations

import hashlib
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "reports" / "final_reports" / "src"
OUT = ROOT / "reports" / "final_reports" / "pdf" / "LeMinhTriet-FinalReport.pdf"

MAIN = SRC / "main.tex"
CORE_TEX_FILES = [
    MAIN,
    SRC / "Chapter" / "0_3_Abstract.tex",
    SRC / "Chapter" / "3_Methodology.tex",
    SRC / "Chapter" / "4_Theoretical_analysis.tex",
    SRC / "Chapter" / "5_Numerical_results.tex",
    SRC / "Chapter" / "6_Conclusions.tex",
    SRC / "Chapter" / "Appendix_A.tex",
    SRC / "Chapter" / "Appendix_B.tex",
]
FIGURE_FILES = [
    SRC / "Images" / "cogmem_pipeline_overview.png",
    SRC / "Images" / "cogmem_memory_graph.png",
    SRC / "Images" / "manual_evaluation_flow.png",
    SRC / "Images" / "agentic_action_effect_trace.png",
    SRC / "Images" / "habit_diary_workload.png",
]


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_required_files_exist() -> None:
    for path in CORE_TEX_FILES:
        assert path.exists(), f"missing report source: {path}"

    built_pdf = SRC / "main.pdf"
    assert built_pdf.exists(), "missing built PDF at src/main.pdf"
    assert OUT.exists(), "missing final exported PDF"
    assert built_pdf.stat().st_size > 300_000, "built PDF is unexpectedly small"
    assert OUT.stat().st_size > 300_000, "exported PDF is unexpectedly small"
    assert _sha256(built_pdf) == _sha256(OUT), "exported PDF differs from built PDF"

    for path in FIGURE_FILES:
        assert path.exists(), f"missing generated report figure: {path}"
        assert path.stat().st_size > 500_000, f"generated figure is unexpectedly small: {path}"


def test_no_empty_appendix_or_placeholders_in_core_report() -> None:
    main_text = _read(MAIN)
    for token in ["\\appendix", "Appendix_A", "Appendix_B"]:
        assert token in main_text, f"appendix token missing: {token}"
    assert "SHORT NOTICES ON REFERENCE" not in main_text
    assert "Chapter/7_Reference" not in main_text

    core_text = "\n".join(_read(path) for path in CORE_TEX_FILES)
    for token in [
        "[FIGURE PLACEHOLDER]",
        "PLACEHOLDER",
        "TBD",
        "placeholder",
        "dự kiến",
        "chưa có sẵn",
    ]:
        assert token not in core_text, f"unfinished marker still present: {token}"
    assert r"\fbox{\parbox" not in core_text, "text-box figure placeholder remains"


def test_final_results_are_reported() -> None:
    abstract = _read(SRC / "Chapter" / "0_3_Abstract.tex")
    chapter_5 = _read(SRC / "Chapter" / "5_Numerical_results.tex")
    chapter_6 = _read(SRC / "Chapter" / "6_Conclusions.tex")

    for token in [
        "LongMemEval v16",
        "29/35",
        "82.9",
        "26/35",
        "74.3",
        "0.8052",
        "0.7624",
        "119/161",
        "73.9",
    ]:
        assert token in abstract + chapter_5 + chapter_6, f"missing reported result: {token}"

    for token in ["baseline", "60.2", "multi-hop", "temporal", "habit", "action-effect", "MAX control"]:
        assert token in chapter_5 + chapter_6, f"missing analysis detail: {token}"


def test_report_uses_reader_friendly_experiment_names() -> None:
    core_text = "\n".join(_read(path) for path in CORE_TEX_FILES)

    assert not re.search(r"\bE[0-9]+G?\b", core_text), "internal LongMemEval profile id leaked"
    assert not re.search(r"\bT8[A-Z]?\b", core_text), "internal LoCoMo run id leaked"
    assert not re.search(r"\bc[0-9]{3}\b", core_text), "internal case id leaked"
    assert "PASS+PARTIAL" not in core_text, "LoCoMo metric should be reported as manual PASS"


def test_diagrams_and_generated_figures_are_present() -> None:
    methodology = _read(SRC / "Chapter" / "3_Methodology.tex")
    theory = _read(SRC / "Chapter" / "4_Theoretical_analysis.tex")

    assert methodology.count(r"\begin{tikzpicture}") >= 7, "methodology diagrams were not materialized"
    assert theory.count(r"\begin{tikzpicture}") >= 9, "theoretical diagrams were not materialized"
    assert "Images/cogmem_pipeline_overview.png" in methodology, "pipeline image is not referenced"
    assert "Images/cogmem_memory_graph.png" in methodology, "memory graph image is not referenced"
    chapter_4 = _read(SRC / "Chapter" / "4_Theoretical_analysis.tex")
    chapter_5 = _read(SRC / "Chapter" / "5_Numerical_results.tex")
    assert "Images/habit_diary_workload.png" in chapter_4, "habit diary image is not referenced"
    assert "Images/agentic_action_effect_trace.png" in chapter_4, "agentic action-effect image is not referenced"
    assert "Images/manual_evaluation_flow.png" in chapter_5, "manual evaluation image is not referenced"
    for label in ["Conversation", "Memory Graph", "Manual Verdict", "Tool Action", "Routine Pattern"]:
        assert label in methodology + chapter_4 + chapter_5, f"missing figure overlay label: {label}"
    assert "raw_snippet" in methodology, "raw snippet evidence path is missing"
    assert "SUM spreading" in methodology + theory, "SUM activation discussion is missing"
    assert "Graph-only LongMemEval v16: SUM reducer so với MAX control" in _read(
        SRC / "Chapter" / "5_Numerical_results.tex"
    ), "SUM vs MAX graph-only results table is missing"

    lof = _read(SRC / "main.lof")
    for figure_number in ["3.3", "3.4", "3.5", "3.6", "3.7", "4.1", "4.3", "4.4", "4.6", "4.7", "4.8", "4.9"]:
        assert f"{{{figure_number}}}" in lof, f"missing figure number in list of figures: {figure_number}"


if __name__ == "__main__":
    test_required_files_exist()
    test_no_empty_appendix_or_placeholders_in_core_report()
    test_final_results_are_reported()
    test_report_uses_reader_friendly_experiment_names()
    test_diagrams_and_generated_figures_are_present()
    print("task_s35_final_report artifact checks passed")
