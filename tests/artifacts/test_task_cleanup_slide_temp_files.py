from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


REMOVED_TEMP_FILES = [
    "_plan_hindsight.py",
    "scripts/build_final_defense_assets.py",
    "scripts/build_final_defense_draft_deck.mjs",
    "scripts/build_final_defense_graph_crops.ps1",
    "scripts/build_qualitative_case_graph_visuals.py",
    "scripts/build_recall_mechanism_visuals.py",
    "scripts/build_retain_extraction_step_images.py",
    "scripts/build_retain_six_node_extraction_animation.py",
]


REQUIRED_GITIGNORE_PATTERNS = [
    "docs/slides/DATN_Final_Defense_*.md",
    "docs/slides/DATN_Final_Defense_*.pptx",
    "docs/slides/DATN_Proposal - Copy (2).pptx",
    "docs/slides/assets/final_defense_*",
    "docs/slides/assets/retain_six_node_extraction_*",
    "docs/slides/assets/retain_extraction_steps/",
    "docs/slides/assets/recall_mechanism_visuals/",
    "docs/slides/assets/qualitative_case_graphs/",
    "_plan_*.py",
]


def main() -> None:
    for relative_path in REMOVED_TEMP_FILES:
        assert not (ROOT / relative_path).exists(), f"temporary file still exists: {relative_path}"

    gitignore = (ROOT / ".gitignore").read_text(encoding="utf-8")
    for pattern in REQUIRED_GITIGNORE_PATTERNS:
        assert pattern in gitignore, f"missing .gitignore pattern: {pattern}"


if __name__ == "__main__":
    main()
