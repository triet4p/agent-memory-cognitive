"""Shared paths + spec loading for the benchmark scripts (generate / gate)."""

from __future__ import annotations

from pathlib import Path

from .schema import ScenarioSpec

REPO_ROOT = Path(__file__).resolve().parents[1]
SPECS_ROOT = REPO_ROOT / "cogmem_bench" / "specs"
PILOT_SPECS_DIR = SPECS_ROOT / "pilot"
DEFAULT_DATA_DIR = REPO_ROOT / "data" / "bench"
DEFAULT_EXPERIMENT_DIR = REPO_ROOT / "experiments" / "cogmem_bench"
DEFAULT_OUT_DIR = DEFAULT_DATA_DIR
WORK_DIR = DEFAULT_DATA_DIR / "work"
ACCEPTED_DIR = DEFAULT_EXPERIMENT_DIR / "accepted"
DEFAULT_REPORT = DEFAULT_EXPERIMENT_DIR / "bench_gate_report.md"


def load_specs(specs_dir: str | Path) -> list[ScenarioSpec]:
    files = sorted(Path(specs_dir).glob("*.json"))
    if not files:
        raise FileNotFoundError(f"no spec JSON files found in {specs_dir}")
    return [ScenarioSpec.model_validate_json(f.read_text(encoding="utf-8")) for f in files]


def work_fixture_path(out_dir: str | Path, scenario_id: str) -> Path:
    return Path(out_dir) / "work" / f"{scenario_id}.json"
