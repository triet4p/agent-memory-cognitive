from __future__ import annotations

import hashlib
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "reports" / "final_reports" / "src"
OUT = ROOT / "reports" / "final_reports" / "pdf" / "LeMinhTriet-FinalReport.pdf"


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_abstract_body_is_english() -> None:
    abstract = _read(SRC / "Chapter" / "0_3_Abstract.tex")
    body = abstract.split(r"\begin{flushright}", 1)[0]

    required_english_phrases = [
        "Long-term conversational agents",
        "This thesis presents",
        "The final evaluation uses manually verified answers",
        "These results suggest",
    ]
    for phrase in required_english_phrases:
        assert phrase in body, f"missing English abstract phrase: {phrase}"

    vietnamese_chars = "àáạảãâầấậẩẫăằắặẳẵèéẹẻẽêềếệểễìíịỉĩòóọỏõôồốộổỗơờớợởỡùúụủũưừứựửữỳýỵỷỹđ"
    assert not re.search(f"[{vietnamese_chars}{vietnamese_chars.upper()}]", body), "abstract body contains Vietnamese text"


def test_reference_stub_removed_and_appendices_restored() -> None:
    main = _read(SRC / "main.tex")
    toc = _read(SRC / "main.toc")

    assert "SHORT NOTICES ON REFERENCE" not in main + toc
    assert "Chapter/7_Reference" not in main
    assert r"\printbibliography" in main
    assert r"\appendix" in main
    assert "Chapter/Appendix_A" in main
    assert "Chapter/Appendix_B" in main

    assert "REFERENCE" in toc
    assert "Knowledge Extraction Prompts (Retain Pipeline)" in toc
    assert "Evaluation and Reflection Prompts" in toc


def test_no_text_box_figure_placeholders_remain() -> None:
    methodology = _read(SRC / "Chapter" / "3_Methodology.tex")
    theory = _read(SRC / "Chapter" / "4_Theoretical_analysis.tex")
    core = methodology + theory

    forbidden = [
        r"\fbox{\parbox",
        "FIGURE PLACEHOLDER",
        "PLACEHOLDER",
        "TBD",
        "placeholder",
        "chưa có sẵn",
    ]
    for token in forbidden:
        assert token not in core, f"unfinished figure marker remains: {token}"

    for label in [
        "fig:ch3_sr_vs_ao",
        "fig:ch3_edge_types",
        "fig:ch3_two_layer_schema",
        "fig:ch3_cycle_guards",
        "fig:ch3_adaptive_routing",
        "fig:ch4_semantic_memory",
        "fig:ch4_habit_memory",
        "fig:ch4_intention_lifecycle",
        "fig:ch4_tec_network",
        "fig:ch4_fuzzy_trace",
        "fig:ch4_episodic_buffer",
        "fig:ch4_attentional_selection",
    ]:
        assert label in core, f"missing upgraded figure label: {label}"

    assert methodology.count(r"\begin{tikzpicture}") >= 7
    assert theory.count(r"\begin{tikzpicture}") >= 9


def test_compiled_outputs_include_required_figure_numbers() -> None:
    built_pdf = SRC / "main.pdf"
    assert built_pdf.exists()
    assert OUT.exists()
    assert built_pdf.stat().st_size > 5_000_000
    assert _sha256(built_pdf) == _sha256(OUT), "exported PDF differs from built PDF"

    lof = _read(SRC / "main.lof")
    for number in ["3.3", "3.4", "3.5", "3.6", "3.7", "4.1", "4.3", "4.4", "4.6", "4.7", "4.8", "4.9"]:
        assert f"{{{number}}}" in lof, f"missing figure {number} from List of Figures"


if __name__ == "__main__":
    test_abstract_body_is_english()
    test_reference_stub_removed_and_appendices_restored()
    test_no_text_box_figure_placeholders_remain()
    test_compiled_outputs_include_required_figure_numbers()
    print("task_s40_report_appendix_figures artifact checks passed")
