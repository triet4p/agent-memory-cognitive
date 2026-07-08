from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def assert_exists(path: Path) -> None:
    if not path.exists():
        raise AssertionError(f"missing expected path: {path}")


def assert_not_exists(path: Path) -> None:
    if path.exists():
        raise AssertionError(f"path should have moved out of data/bench: {path}")


def main() -> None:
    data_root = ROOT / "data" / "bench"
    exp_root = ROOT / "experiments" / "cogmem_bench"

    assert_exists(data_root / "work")
    assert_exists(data_root / "locomo_verdict")
    assert_exists(data_root / "README.md")

    for old_name in ["accepted", "gate_detail", "visualization", "gate_results.json"]:
        assert_not_exists(data_root / old_name)

    for new_name in [
        "README.md",
        "bench_gate_report.md",
        "gate_results.json",
        "accepted",
        "gate_detail",
        "visualization",
    ]:
        assert_exists(exp_root / new_name)

    gate_py = (ROOT / "cogmem_bench" / "gate.py").read_text(encoding="utf-8")
    visualize_py = (ROOT / "cogmem_bench" / "visualize.py").read_text(encoding="utf-8")
    datasets_py = (ROOT / "cogmem_bench" / "datasets.py").read_text(encoding="utf-8")

    required_snippets = [
        "DEFAULT_DATA_DIR = REPO_ROOT / \"data\" / \"bench\"",
        "DEFAULT_EXPERIMENT_DIR = REPO_ROOT / \"experiments\" / \"cogmem_bench\"",
        "work_fixture_path(data_dir, spec.scenario_id)",
        "experiments/cogmem_bench/gate_detail",
        "experiments\" / \"cogmem_bench\" / \"visualization",
    ]
    combined = "\n".join([gate_py, visualize_py, datasets_py])
    missing = [snippet for snippet in required_snippets if snippet not in combined]
    if missing:
        raise AssertionError(f"missing expected code snippets: {missing}")

    print("CogMem Bench experiment layout checks passed")


if __name__ == "__main__":
    main()
