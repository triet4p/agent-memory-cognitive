from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
STEP_DIR = ROOT / "docs" / "slides" / "assets" / "retain_extraction_steps"
MANIFEST = STEP_DIR / "manifest.json"
SCRIPT = ROOT / "scripts" / "build_retain_extraction_step_images.py"


def _manifest() -> dict:
    return json.loads(MANIFEST.read_text(encoding="utf-8"))


def test_every_node_has_a_specific_fact_not_just_a_type_label() -> None:
    manifest = _manifest()
    nodes = manifest["nodes"]
    assert len(nodes) == 10

    required_phrases = {
        "world_home": ["Da Nang"],
        "world_rules": ["compost", "rules"],
        "opinion_hotel": ["quiet", "hotels"],
        "intention_apr1": ["Apr 1"],
        "habit_coffee": ["coffee", "coding"],
        "experience_8am": ["Mar 15", "8 AM"],
        "opinion_deepwork": ["Deep work", "meetings"],
        "experience_bags": ["Apr 10", "compost bags"],
        "intention_pending": ["Apr 10", "still not started"],
        "action_effect_429": ["429", "Retry-After", "200"],
    }

    by_id = {node["id"]: node for node in nodes}
    assert set(by_id) == set(required_phrases)

    node_types = {"world", "experience", "opinion", "habit", "intention", "action-effect"}
    for node_id, phrases in required_phrases.items():
        node = by_id[node_id]
        label = node["label"]
        fact = node["fact"]
        assert fact.endswith(".")
        assert len(fact.split()) >= 4
        assert label.split(" / ", 1)[0] in node_types
        assert label not in node_types
        for phrase in phrases:
            assert phrase in f"{label} {fact}", f"{node_id} is missing {phrase!r}"


def test_renderer_draws_fact_label_separately_from_type_badge() -> None:
    source = SCRIPT.read_text(encoding="utf-8")
    for expected in [
        '"fact_label"',
        '"type"',
        'spec["fact_label"]',
        'spec["type"]',
        '"node_fact"',
    ]:
        assert expected in source


def main() -> None:
    test_every_node_has_a_specific_fact_not_just_a_type_label()
    test_renderer_draws_fact_label_separately_from_type_badge()
    print("PASS: retain extraction nodes include concrete fact text")


if __name__ == "__main__":
    main()
