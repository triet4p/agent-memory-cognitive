from __future__ import annotations

import struct
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
ASSET_DIR = ROOT / "docs" / "slides" / "assets"


REDRAWN_STEMS = [
    "final_defense_01_title_icon_strip",
    "final_defense_02_toc_progress",
    "final_defense_03_problem_timeline",
    "final_defense_04_common_approaches",
    "final_defense_05_related_work_landscape",
    "final_defense_07_four_contributions",
    "final_defense_08_typed_memory_networks",
    "final_defense_09_typed_graph_enables",
    "final_defense_10_fact_snippet",
    "final_defense_11_four_recall_channels",
    "final_defense_12_rrf_crossencoder",
    "final_defense_13_adaptive_routing",
    "final_defense_14_sum_vs_max",
    "final_defense_15_cycle_guards",
    "final_defense_16_experiment_overview",
    "final_defense_17_longmemeval_structure",
    "final_defense_18_locomo_structure",
    "final_defense_19_cogmem_bench_motivation",
    "final_defense_20_cogmem_bench_pipeline",
    "final_defense_21_longmemeval_summax_results",
    "final_defense_22_locomo_results",
    "final_defense_23_intention_case_summary",
    "final_defense_24_action_effect_case_summary",
    "final_defense_25_conclusion_pillars",
    "final_defense_26_limitations_future",
    "final_defense_27_qa",
]


FORBIDDEN_SLIDE_TITLES = [
    "Problem: long conversations",
    "Common approaches",
    "Related work landscape",
    "Four contributions",
    "Six typed memory networks",
    "Structured fact + raw snippet",
    "Four recall channels",
    "Adaptive query routing",
    "SUM vs MAX graph activation",
    "Experiment overview",
    "LongMemEval structure",
    "LoCoMo structure",
    "CogMem Bench pipeline",
    "What CogMem demonstrates",
    "What remains",
    "Q&A",
]


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _png_header(path: Path) -> tuple[int, int, int]:
    data = path.read_bytes()
    assert data[:8] == b"\x89PNG\r\n\x1a\n", f"not a PNG: {path.name}"
    width, height = struct.unpack(">II", data[16:24])
    color_type = data[25]
    return width, height, color_type


def test_redrawn_assets_are_illustrations_not_slide_canvases() -> None:
    for stem in REDRAWN_STEMS:
        svg = ASSET_DIR / f"{stem}.svg"
        assert svg.exists(), f"missing SVG source: {svg.name}"
        text = _read(svg)

        for forbidden in FORBIDDEN_SLIDE_TITLES:
            assert forbidden not in text, f"{svg.name} still embeds slide title text: {forbidden}"

        assert "#f6f9fc" not in text, f"{svg.name} still contains slide-like background fill"
        assert "#dfe7ef" not in text, f"{svg.name} still contains slide-like grid lines"
        assert '<g transform="translate(0,-64)">' in text, f"{svg.name} was not converted to content-only layout"


def test_redrawn_pngs_have_alpha_backgrounds() -> None:
    for stem in REDRAWN_STEMS:
        png = ASSET_DIR / f"{stem}.png"
        assert png.exists(), f"missing PNG render: {png.name}"
        width, height, color_type = _png_header(png)
        assert (width, height) == (1600, 900), f"unexpected render size for {png.name}: {width}x{height}"
        assert color_type in {4, 6}, f"{png.name} is not rendered with an alpha channel"


def test_graph_crops_are_content_figures_without_slide_headers() -> None:
    crop_names = [
        "final_defense_23_intention_graph_crop.png",
        "final_defense_24_action_effect_graph_crop.png",
    ]
    for name in crop_names:
        path = ASSET_DIR / name
        assert path.exists(), f"missing graph crop: {name}"
        width, height, _ = _png_header(path)
        assert (width, height) == (1600, 900), f"unexpected crop size for {name}: {width}x{height}"


def test_contact_sheet_is_available_for_visual_review() -> None:
    sheet = ASSET_DIR / "final_defense_contact_sheet.png"
    assert sheet.exists(), "missing final defense contact sheet"
    width, height, _ = _png_header(sheet)
    assert width >= 1200 and height >= 1600


if __name__ == "__main__":
    test_redrawn_assets_are_illustrations_not_slide_canvases()
    test_redrawn_pngs_have_alpha_backgrounds()
    test_graph_crops_are_content_figures_without_slide_headers()
    test_contact_sheet_is_available_for_visual_review()
    print("task_s46_final_defense_asset_illustrations artifact checks passed")

