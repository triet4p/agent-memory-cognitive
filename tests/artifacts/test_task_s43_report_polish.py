from __future__ import annotations

import hashlib
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "reports" / "final_reports" / "src"
OUT = ROOT / "reports" / "final_reports" / "pdf" / "LeMinhTriet-FinalReport.pdf"


def _read(relative: str) -> str:
    return (SRC / relative).read_text(encoding="utf-8")


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_abstract_stays_overview_only() -> None:
    abstract = _read("Chapter/0_3_Abstract.tex")

    for token in [
        "cognitive graph",
        "chiều hướng cải thiện tích cực",
        "long-term memory API",
    ]:
        assert token in abstract, f"missing revised abstract theme: {token}"

    for token in [
        "30/35",
        "31/35",
        "119/161",
        "90--120 phút",
        "700 node",
        "semantic, BM25, graph và temporal channels",
        "world, experience, opinion, habit, intention, action\\_effect",
    ]:
        assert token not in abstract, f"abstract should avoid detailed metrics/implementation detail: {token}"


def test_sum_max_notation_is_explained() -> None:
    methodology = _read("Chapter/3_Methodology.tex")

    for token in [
        "$A(v,t)$ là mức activation",
        "$N(v)$ là tập các node láng giềng",
        "$w(u,v)$ là trọng số cạnh",
        "$\\delta$ là hệ số suy giảm activation",
        "$\\mu(\\ell)$ là hệ số điều chỉnh theo loại liên kết",
        "$A_{\\max}$ là ngưỡng bão hòa",
    ]:
        assert token in methodology, f"missing notation explanation: {token}"


def test_reworked_figures_and_pdf_outputs_exist() -> None:
    methodology = _read("Chapter/3_Methodology.tex")

    for token in [
        "{Habit}",
        "{Action-effect}",
        "three guards jointly prevent",
        "evidence profile by query type",
    ]:
        assert token in methodology, f"missing revised figure content: {token}"

    built_pdf = SRC / "main.pdf"
    assert built_pdf.exists(), "missing rebuilt main.pdf"
    assert OUT.exists(), "missing exported report PDF"
    assert _sha256(built_pdf) == _sha256(OUT), "exported PDF differs from rebuilt main.pdf"


if __name__ == "__main__":
    test_abstract_stays_overview_only()
    test_sum_max_notation_is_explained()
    test_reworked_figures_and_pdf_outputs_exist()
    print("task_s43_report_polish artifact checks passed")
