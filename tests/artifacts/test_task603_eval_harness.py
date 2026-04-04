from __future__ import annotations

import sys
from pathlib import Path


def assert_required_files(repo_root: Path) -> None:
    required = [
        repo_root / "scripts" / "eval_cogmem.py",
        repo_root / "scripts" / "ablation_runner.py",
        repo_root / "logs" / "task_603_summary.md",
        repo_root / "tests" / "artifacts" / "test_task603_eval_harness.py",
    ]
    missing = [str(path.relative_to(repo_root)) for path in required if not path.exists()]
    assert not missing, f"Missing T6.3 files: {missing}"


def assert_isolation(repo_root: Path) -> None:
    scope = [
        repo_root / "scripts" / "eval_cogmem.py",
        repo_root / "scripts" / "ablation_runner.py",
    ]
    violations: list[str] = []
    for path in scope:
        text = path.read_text(encoding="utf-8")
        if "hindsight_api" in text:
            violations.append(str(path.relative_to(repo_root)))
    assert not violations, f"Isolation violation: {violations}"


def assert_dual_pipeline_contract(repo_root: Path) -> None:
    eval_text = (repo_root / "scripts" / "eval_cogmem.py").read_text(encoding="utf-8")
    required_markers = [
        "def run_recall_only_pipeline",
        "def run_full_pipeline",
        "ABLATION_PROFILES",
        "resolve_eval_llm_config",
        "COGMEM_EVAL_LLM_BASE_URL",
        "COGMEM_API_LLM_BASE_URL",
    ]
    missing = [marker for marker in required_markers if marker not in eval_text]
    assert not missing, f"Dual pipeline or LLM compatibility markers missing: {missing}"


def run_behavior_test(repo_root: Path) -> None:
    repo_root_str = str(repo_root)
    if repo_root_str not in sys.path:
        sys.path.insert(0, repo_root_str)

    from scripts import ablation_runner as ablation
    from scripts import eval_cogmem as eval_cogmem

    def fake_post_json(url: str, payload: dict, timeout_seconds: float):
        assert timeout_seconds > 0
        if url.endswith("/memories"):
            return {
                "success": True,
                "bank_id": "fake",
                "items_count": len(payload.get("items", [])),
                "unit_ids": [["u1"], ["u2"]],
            }

        if url.endswith("/memories/recall"):
            query = str(payload.get("query", "")).lower()
            if "kế hoạch" in query:
                results = [
                    {"id": "1", "text": "User có kế hoạch học Rust trước Q3, deadline cuối tháng 9", "fact_type": "intention"}
                ]
            else:
                results = [
                    {
                        "id": "2",
                        "text": "Khi latency vượt 100ms user chuyển sang int8 và latency giảm còn khoảng 45ms",
                        "fact_type": "action_effect",
                    }
                ]
            return {"results": results, "trace": {"mock": True}}

        raise AssertionError(f"Unexpected URL: {url}")

    def fake_llm_call(llm_config, messages, max_completion_tokens=None):
        system_prompt = str(messages[0].get("content", ""))
        user_prompt = str(messages[1].get("content", "")) if len(messages) > 1 else ""

        if "evaluation judge" in system_prompt.lower():
            return '{"correct": true, "score": 1.0, "reason": "matched"}'

        if "kế hoạch" in user_prompt.lower():
            return "User có kế hoạch học Rust trước Q3, deadline cuối tháng 9."

        return "Khi latency vượt 100ms user chuyển sang int8 và latency giảm còn khoảng 45ms."

    recall_result = eval_cogmem.run_pipeline(
        pipeline="recall",
        api_base_url="http://fake:8888",
        bank_id="bank_recall",
        profile_id="E1",
        fixture_name="short",
        skip_retain=False,
        timeout_seconds=5.0,
        post_json_fn=fake_post_json,
        llm_call_fn=fake_llm_call,
    )
    assert recall_result["pipeline"] == "recall_only"
    assert recall_result["metrics"]["recall_keyword_accuracy"] > 0.5

    full_result = eval_cogmem.run_pipeline(
        pipeline="full",
        api_base_url="http://fake:8888",
        bank_id="bank_full",
        profile_id="E7",
        fixture_name="short",
        skip_retain=False,
        timeout_seconds=5.0,
        post_json_fn=fake_post_json,
        llm_call_fn=fake_llm_call,
    )
    assert full_result["pipeline"] == "full_e2e"
    assert full_result["metrics"]["judge_accuracy"] == 1.0
    assert full_result["ablation_hooks"]["adaptive_router_enabled"] is True
    assert full_result["ablation_hooks"]["sum_activation_enabled"] is True

    def runner(**kwargs):
        return eval_cogmem.run_pipeline(
            post_json_fn=fake_post_json,
            llm_call_fn=fake_llm_call,
            **kwargs,
        )

    suite = ablation.run_ablation_suite(
        profiles=["E1", "E7"],
        pipelines=["recall", "full"],
        fixture_name="short",
        api_base_url="http://fake:8888",
        skip_retain=False,
        timeout_seconds=5.0,
        pipeline_runner=runner,
    )
    assert len(suite["runs"]) == 4
    assert len(suite["summary"]) == 4


def main() -> None:
    repo_root = Path(__file__).resolve().parents[2]
    assert_required_files(repo_root)
    assert_isolation(repo_root)
    assert_dual_pipeline_contract(repo_root)
    run_behavior_test(repo_root)
    print("Task 603 eval harness check passed.")


if __name__ == "__main__":
    main()
