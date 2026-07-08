"""Validate the reorganized LongMemEval distill experiment folder.

Run with:
    uv run python tests/artifacts/test_task_longmemval_distill_experiment.py
"""

from __future__ import annotations

import json
import runpy
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
OUT_DIR = ROOT / "experiments" / "longmemval-distill"


EXPECTED = {
    "00_baseline_v16_e7_30_35": ("E7", "experiments\\v16\\checkpoints", 30),
    "01_full_six_nodes_v15_e7_31_35": ("E7", "experiments\\v15\\checkpoints-s29-wave2e", 31),
    "02_ablation_no_habit_v16_e8_29_35": ("E8", "experiments\\v16\\checkpoints-cross-fact-type", 29),
    "03_ablation_no_action_effect_v16_e10_29_35": ("E10", "experiments\\v16\\checkpoints-cross-fact-type", 29),
    "04_ablation_no_intention_v16_e9_29_35": ("E9", "experiments\\v16\\checkpoints-cross-fact-type", 29),
    "05_graph_only_full_six_nodes_v16_e7g_25_35": ("E7G", "experiments\\v16\\checkpoints-cross-fact-type", 25),
    "06_graph_only_no_habit_v16_e8g_28_35": ("E8G", "experiments\\v16\\checkpoints-cross-fact-type", 28),
    "07_graph_only_no_action_effect_v16_e10g_28_35": ("E10G", "experiments\\v16\\checkpoints-cross-fact-type", 28),
    "08_graph_only_no_intention_v16_e9g_29_35": ("E9G", "experiments\\v16\\checkpoints-cross-fact-type", 29),
    "09_graph_only_original_three_types_v16_e11g_27_35": ("E11G", "experiments\\v16\\checkpoints-cross-fact-type", 27),
}


def judge_correct(data: dict) -> bool:
    question = data.get("questions", [data])[0] if data.get("questions") else data
    judge = question.get("judge") or data.get("judge") or {}
    if isinstance(judge.get("correct"), bool):
        return judge["correct"]
    score = judge.get("score", question.get("judge_score", data.get("judge_score")))
    return bool(isinstance(score, (int, float)) and score >= 0.7)


def main() -> None:
    runpy.run_path(str(ROOT / "scripts" / "build_longmemval_distill_experiment.py"), run_name="__main__")

    manifest = json.loads((OUT_DIR / "manifest.json").read_text(encoding="utf-8"))
    assert manifest["copied_without_judge_edits"] is True
    assert len(manifest["configs"]) == len(EXPECTED)

    folders = {item["folder"]: item for item in manifest["configs"]}
    assert set(folders) == set(EXPECTED)

    for folder, (profile, source_dir, expected_correct) in EXPECTED.items():
        summary = folders[folder]
        assert summary["profile"] == profile
        assert summary["source_dir"] == source_dir
        assert summary["copied_without_judge_edits"] is True
        assert summary["total"] == 35
        assert summary["correct"] == expected_correct

        checkpoint_dir = OUT_DIR / folder / "checkpoints"
        files = sorted(checkpoint_dir.glob(f"{profile}_full_c*.json"))
        assert len(files) == 35, f"{folder} should contain 35 checkpoint files"

        recomputed_correct = 0
        for path in files:
            data = json.loads(path.read_text(encoding="utf-8"))
            assert data.get("profile", {}).get("profile_id") == profile
            recomputed_correct += int(judge_correct(data))
        assert recomputed_correct == expected_correct, folder

        readme = (OUT_DIR / folder / "README.md").read_text(encoding="utf-8")
        assert "Copied without judge edits: true" in readme
        assert "Ablation:" in readme

    print("longmemval-distill experiment folder verified")


if __name__ == "__main__":
    main()
