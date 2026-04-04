from __future__ import annotations

import argparse
import json
import time
import uuid
from pathlib import Path
from typing import Any, Callable

from scripts.eval_cogmem import ABLATION_PROFILES, resolve_api_base_url, run_pipeline


JsonDict = dict[str, Any]


def run_ablation_suite(
    profiles: list[str],
    pipelines: list[str],
    *,
    fixture_name: str,
    api_base_url: str,
    skip_retain: bool,
    timeout_seconds: float,
    pipeline_runner: Callable[..., JsonDict] = run_pipeline,
) -> JsonDict:
    started_at = time.time()
    runs: list[JsonDict] = []

    for profile_id in profiles:
        if profile_id not in ABLATION_PROFILES:
            raise ValueError(f"Unknown profile: {profile_id}")

        for pipeline in pipelines:
            bank_id = f"cogmem_ablation_{profile_id.lower()}_{pipeline}_{uuid.uuid4().hex[:8]}"
            result = pipeline_runner(
                pipeline=pipeline,
                api_base_url=api_base_url,
                bank_id=bank_id,
                profile_id=profile_id,
                fixture_name=fixture_name,
                skip_retain=skip_retain,
                timeout_seconds=timeout_seconds,
            )
            runs.append(result)

    summary: list[JsonDict] = []
    for run in runs:
        summary.append(
            {
                "profile": run["profile"]["profile_id"],
                "pipeline": run["pipeline"],
                "bank_id": run["bank_id"],
                "recall_keyword_accuracy": run["metrics"].get("recall_keyword_accuracy", 0.0),
                "recall_strict_accuracy": run["metrics"].get("recall_strict_accuracy", 0.0),
                "judge_accuracy": run["metrics"].get("judge_accuracy"),
                "judge_score_mean": run["metrics"].get("judge_score_mean"),
            }
        )

    return {
        "suite": "T6.3_ablation_runner",
        "fixture": fixture_name,
        "api_base_url": api_base_url,
        "profiles": profiles,
        "pipelines": pipelines,
        "duration_seconds": time.time() - started_at,
        "runs": runs,
        "summary": summary,
    }


def save_suite_result(result: JsonDict, output_dir: Path) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    stamp = int(time.time())
    file_path = output_dir / f"ablation_suite_{stamp}.json"
    file_path.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    return file_path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run CogMem T6.3 ablation suite")
    parser.add_argument("--profiles", default="E1,E2,E3,E4,E5,E6,E7")
    parser.add_argument("--pipeline", choices=["recall", "full", "both"], default="both")
    parser.add_argument("--fixture", choices=["short"], default="short")
    parser.add_argument("--base-url", default=None, help="CogMem API base URL")
    parser.add_argument("--skip-retain", action="store_true")
    parser.add_argument("--api-timeout", type=float, default=120.0)
    parser.add_argument("--output", default="logs/eval")
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    profile_tokens = [token.strip() for token in args.profiles.split(",") if token.strip()]
    if not profile_tokens:
        raise ValueError("profiles cannot be empty")

    pipelines = ["recall", "full"] if args.pipeline == "both" else [args.pipeline]

    result = run_ablation_suite(
        profiles=profile_tokens,
        pipelines=pipelines,
        fixture_name=args.fixture,
        api_base_url=resolve_api_base_url(args.base_url),
        skip_retain=args.skip_retain,
        timeout_seconds=max(1.0, float(args.api_timeout)),
    )

    out_path = save_suite_result(result, Path(args.output))
    print(f"Ablation suite completed: {out_path.as_posix()}")
    for item in result["summary"]:
        print(
            f"{item['profile']} | {item['pipeline']} | "
            f"recall={item['recall_keyword_accuracy']:.3f} | "
            f"judge={item['judge_accuracy']}"
        )


if __name__ == "__main__":
    main()
