from __future__ import annotations

import re
import struct
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
ASSET_DIR = ROOT / "docs" / "slides" / "assets"
OUTLINE = ROOT / "docs" / "slides" / "DATN_Final_Defense_Detailed_Outline.md"


SLIDE_ASSETS = {
    1: "final_defense_01_title_icon_strip",
    2: "final_defense_02_toc_progress",
    3: "final_defense_03_problem_timeline",
    4: "final_defense_04_common_approaches",
    5: "final_defense_05_related_work_landscape",
    6: "final_defense_reuse_cogmem_pipeline_overview",
    7: "final_defense_07_four_contributions",
    8: "final_defense_08_typed_memory_networks",
    9: "final_defense_09_typed_graph_enables",
    10: "final_defense_10_fact_snippet",
    11: "final_defense_11_four_recall_channels",
    12: "final_defense_12_rrf_crossencoder",
    13: "final_defense_13_adaptive_routing",
    14: "final_defense_14_sum_vs_max",
    15: "final_defense_15_cycle_guards",
    16: "final_defense_16_experiment_overview",
    17: "final_defense_17_longmemeval_structure",
    18: "final_defense_18_locomo_structure",
    19: "final_defense_19_cogmem_bench_motivation",
    20: "final_defense_20_cogmem_bench_pipeline",
    21: "final_defense_21_longmemeval_summax_results",
    22: "final_defense_22_locomo_results",
    23: "final_defense_23_intention_case_summary",
    24: "final_defense_24_action_effect_case_summary",
    25: "final_defense_25_conclusion_pillars",
    26: "final_defense_26_limitations_future",
    27: "final_defense_27_qa",
}


def _png_size(path: Path) -> tuple[int, int]:
    data = path.read_bytes()
    assert data[:8] == b"\x89PNG\r\n\x1a\n", f"Not a PNG: {path}"
    width, height = struct.unpack(">II", data[16:24])
    return width, height


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_outline_exists_and_assets_directory_is_populated() -> None:
    assert OUTLINE.exists(), f"missing outline: {OUTLINE}"
    assert ASSET_DIR.exists(), f"missing asset dir: {ASSET_DIR}"
    assert len(list(ASSET_DIR.glob("final_defense_*"))) >= 50


def test_each_main_slide_has_a_visual_asset() -> None:
    for slide_no, stem in SLIDE_ASSETS.items():
        png = ASSET_DIR / f"{stem}.png"
        assert png.exists(), f"Slide {slide_no} missing PNG asset: {png.name}"
        width, height = _png_size(png)
        ratio = width / height
        assert 1.70 <= ratio <= 1.85, f"Slide {slide_no} asset is not widescreen: {png.name} {width}x{height}"
        assert width >= 1280 and height >= 720, f"Slide {slide_no} asset too small: {png.name} {width}x{height}"


def test_svg_sources_exist_for_redrawn_assets() -> None:
    for slide_no, stem in SLIDE_ASSETS.items():
        if stem.startswith("final_defense_reuse_"):
            continue
        svg = ASSET_DIR / f"{stem}.svg"
        assert svg.exists(), f"Slide {slide_no} missing editable SVG source: {svg.name}"
        text = _read(svg)
        assert 'width="1600"' in text and 'height="900"' in text
        assert 'viewBox="0 0 1600 900"' in text


def test_reused_report_assets_are_available() -> None:
    required = [
        "final_defense_reuse_cogmem_pipeline_overview.png",
        "final_defense_reuse_cogmem_memory_graph.png",
        "final_defense_reuse_manual_evaluation_flow.png",
        "final_defense_reuse_agentic_action_effect_trace.png",
        "final_defense_reuse_habit_diary_workload.png",
        "final_defense_reuse_cogmem_bench_intention_full.png",
        "final_defense_reuse_cogmem_bench_action_effect_full.png",
    ]
    for name in required:
        path = ASSET_DIR / name
        assert path.exists(), f"missing reused report asset: {name}"
        width, height = _png_size(path)
        assert width >= 1280 and height >= 720


def test_quantitative_assets_use_updated_report_numbers() -> None:
    longmem = _read(ASSET_DIR / "final_defense_21_longmemeval_summax_results.svg")
    locomo = _read(ASSET_DIR / "final_defense_22_locomo_results.svg")
    for expected in ["88.6%", "85.7%", "82.9%", "74.3%", "62.9%", "0.805", "0.762", "0.848"]:
        assert expected in longmem, f"missing LongMemEval/SUM-MAX value: {expected}"
    for expected in ["60.2%", "65.2%", "73.9%", "97/161", "105/161", "119/161", "91.7%", "41.7%"]:
        assert expected in locomo, f"missing LoCoMo value: {expected}"


def test_cogmem_bench_assets_include_summary_and_graph_crops() -> None:
    required_pngs = [
        ASSET_DIR / "final_defense_23_intention_case_summary.png",
        ASSET_DIR / "final_defense_23_intention_graph_crop.png",
        ASSET_DIR / "final_defense_24_action_effect_case_summary.png",
        ASSET_DIR / "final_defense_24_action_effect_graph_crop.png",
    ]
    for path in required_pngs:
        assert path.exists(), f"missing CogMem Bench visual: {path.name}"
        assert _png_size(path) == (1600, 900)

    intention_svg = _read(ASSET_DIR / "final_defense_23_intention_case_summary.svg")
    action_svg = _read(ASSET_DIR / "final_defense_24_action_effect_case_summary.svg")
    for expected in ["37 facts", "4 intention nodes", "Answer: Composting", "Wrong: rainwater"]:
        assert expected in intention_svg
    for expected in ["HTTP 429", "Retry-After", "returns 200", "5/12 clean discriminations"]:
        assert expected in action_svg


def test_slide_copy_is_phrase_oriented_not_paragraph_like() -> None:
    for svg in ASSET_DIR.glob("final_defense_*.svg"):
        text = _read(svg)
        visible_text = re.findall(r">([^<>]{40,})<", text)
        long_runs = [run for run in visible_text if len(run.split()) > 14]
        assert not long_runs, f"Long paragraph-like text in {svg.name}: {long_runs[:2]}"


if __name__ == "__main__":
    test_outline_exists_and_assets_directory_is_populated()
    test_each_main_slide_has_a_visual_asset()
    test_svg_sources_exist_for_redrawn_assets()
    test_reused_report_assets_are_available()
    test_quantitative_assets_use_updated_report_numbers()
    test_cogmem_bench_assets_include_summary_and_graph_crops()
    test_slide_copy_is_phrase_oriented_not_paragraph_like()
    print("task_s45_final_defense_assets artifact checks passed")

