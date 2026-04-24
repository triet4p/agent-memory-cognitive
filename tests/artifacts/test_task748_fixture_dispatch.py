"""Task 748: S21.3 — Fixture dispatch CLI wiring.

Verifies:
- --fixture accepts short, longmemeval, locomo
- --fixture-path is accepted
- get_fixture("short") returns SHORT_DIALOGUE_FIXTURE (regression)
- run_pipeline() accepts fixture_path argument
"""

from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.eval_cogmem import get_fixture, run_pipeline, SHORT_DIALOGUE_FIXTURE, parse_args


def test_short_fixture_regression():
    fixture = get_fixture("short")
    assert fixture is SHORT_DIALOGUE_FIXTURE, "short should return SHORT_DIALOGUE_FIXTURE"
    assert "turns" in fixture
    assert len(fixture["turns"]) == 3
    assert len(fixture["questions"]) == 2


def test_longmemeval_via_get_fixture():
    fixture = get_fixture("longmemeval")
    assert fixture["name"] == "longmemeval_benchmark"
    assert len(fixture["questions"]) == 12


def test_locomo_via_get_fixture():
    fixture = get_fixture("locomo")
    assert fixture["name"] == "locomo_benchmark"
    assert len(fixture["questions"]) > 0


def test_parse_args_accepts_fixtures():
    import sys as _sys
    original_argv = _sys.argv
    try:
        _sys.argv = ["eval_cogmem.py", "--fixture", "longmemeval", "--pipeline", "recall", "--profile", "E1"]
        args = parse_args()
        assert args.fixture == "longmemeval"
        assert args.fixture_path is None

        _sys.argv = ["eval_cogmem.py", "--fixture", "short", "--pipeline", "full", "--profile", "E7"]
        args = parse_args()
        assert args.fixture == "short"

        _sys.argv = ["eval_cogmem.py", "--fixture", "longmemeval", "--fixture-path", "/custom/path.json", "--pipeline", "recall"]
        args = parse_args()
        assert args.fixture == "longmemeval"
        assert args.fixture_path == "/custom/path.json"

        _sys.argv = ["eval_cogmem.py", "--fixture", "locomo", "--pipeline", "recall", "--profile", "E1"]
        args = parse_args()
        assert args.fixture == "locomo"
    finally:
        _sys.argv = original_argv


def test_run_pipeline_with_fixture_path():
    def fake_post_json(url, payload, timeout):
        return {"results": [], "trace": {}}

    result = run_pipeline(
        pipeline="recall",
        api_base_url="http://fake:8888",
        bank_id="bank_test",
        profile_id="E1",
        fixture_name="longmemeval",
        skip_retain=True,
        timeout_seconds=5.0,
        post_json_fn=fake_post_json,
        fixture_path=None,
    )
    assert result["pipeline"] == "recall_only"
    assert result["fixture"] == "longmemeval_benchmark"
    assert result["metrics"]["question_count"] == 12


def main() -> None:
    test_short_fixture_regression()
    test_longmemeval_via_get_fixture()
    test_locomo_via_get_fixture()
    test_parse_args_accepts_fixtures()
    test_run_pipeline_with_fixture_path()
    print("Task 748 fixture dispatch gate passed.")


if __name__ == "__main__":
    main()
