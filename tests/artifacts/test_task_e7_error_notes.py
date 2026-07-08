from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def assert_contains(path: Path, snippets: list[str]) -> None:
    text = path.read_text(encoding="utf-8")
    for snippet in snippets:
        assert snippet in text, f"{path} missing expected snippet: {snippet}"


def main() -> None:
    longmem = ROOT / "experiments/longmemval-distill/01_full_six_nodes_v15_e7_31_35/ERROR_ANALYSIS_E7_FULL.md"
    locomo = ROOT / "experiments/locomo-distill/01_t8g_evidence_guard_119_161/ERROR_ANALYSIS_E7_FULL.md"

    assert longmem.exists(), longmem
    assert locomo.exists(), locomo

    assert_contains(
        longmem,
        [
            "Scope: LongMemEval-Distill, E7 full CogMem",
            "c000",
            "c003",
            "c007",
            "c024",
            "c029",
            "c030",
            "auto-judge false negative",
        ],
    )
    assert_contains(
        locomo,
        [
            "Scope: LoCoMo-Distill, E7 full CogMem",
            "PASS + PARTIAL",
            "Enumeration and List Completeness",
            "Specific-Detail Substitution or Count Error",
            "Temporal Span and Event Count",
            "c093",
        ],
    )


if __name__ == "__main__":
    main()
