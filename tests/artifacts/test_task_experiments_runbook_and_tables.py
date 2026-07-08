from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def require_text(path: Path, snippets: list[str]) -> None:
    text = path.read_text(encoding="utf-8")
    missing = [snippet for snippet in snippets if snippet not in text]
    if missing:
        raise AssertionError(f"{path} missing snippets: {missing}")


def require_file(path: Path, required_header: str) -> None:
    if not path.exists():
        raise AssertionError(f"missing expected file: {path}")
    header = path.read_text(encoding="utf-8").splitlines()[0]
    if header != required_header:
        raise AssertionError(f"unexpected CSV header for {path}: {header}")


def main() -> None:
    require_text(
        ROOT / "Experiments.txt",
        [
            "LongMemEval flow",
            "LoCoMo flow",
            "CogMem Bench flow",
            "python scripts/build_report_experiment_tables.py",
            "ti_le = correct / total",
            "đạt = pass_plus_partial = pass + partial",
        ],
    )
    require_text(
        ROOT / "Node.txt",
        [
            "Experiments.txt",
            "Keep this file focused on setting up and running the source code itself.",
        ],
    )

    require_file(
        ROOT / "experiments/longmemval-distill/report_table_longmemeval_results.csv",
        "cau_hinh,profile,dat,tong,dat_tong,ti_le,accuracy_numeric,source",
    )
    require_file(
        ROOT / "experiments/longmemval-distill/report_table_sum_vs_max_graph_only.csv",
        "co_che,profile,so_cau,trung_binh_at5,trung_binh_at10,so_cau_dat_at5,so_cau_dat_at10,source",
    )
    require_file(
        ROOT / "experiments/locomo-distill/report_table_locomo_full_accuracy.csv",
        "cau_hinh,tong_so_cau,dat,ti_le,source",
    )
    require_file(
        ROOT / "experiments/locomo-distill/report_table_locomo_category_breakdown.csv",
        "nhom_cau_hoi,category,tong_so_cau,dat,ti_le_dat,pass,partial,fail,source",
    )
    require_file(
        ROOT / "experiments/cogmem_bench/report_table_cogmem_bench_manual_outcomes.csv",
        "nhom_ket_qua,dien_giai,so_case,tong,ti_le,cases,source",
    )

    print("experiments runbook and report-table CSV checks passed")


if __name__ == "__main__":
    main()
