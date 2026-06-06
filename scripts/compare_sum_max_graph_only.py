"""Compare graph-only SUM vs MAX activation on existing benchmark banks.

This runner is intentionally recall-only: it isolates the graph channel by using
the E7G profile (BFS SUM) and E7GM profile (BFS MAX control) against the same
retained banks. It does not write to data/ and does not run retain.
"""

from __future__ import annotations

import argparse
import json
import statistics
import sys
import time
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.eval_cogmem import (
    _benchmark_item_as_fixture,
    get_fixture,
    resolve_api_base_url,
    run_pipeline,
)


JsonDict = dict[str, Any]


def _metric(question: JsonDict, name: str) -> float | None:
    value = question.get(name)
    if not isinstance(value, dict):
        return None
    recall = value.get("recall_at_k")
    if recall is None:
        return None
    return float(recall)


def _mean(values: list[float | None]) -> float | None:
    clean = [value for value in values if value is not None]
    if not clean:
        return None
    return float(statistics.fmean(clean))


def _top_docs(question: JsonDict, limit: int = 10) -> list[str]:
    results = question.get("recall_results") or []
    docs: list[str] = []
    for item in results[:limit]:
        doc = item.get("document_id")
        docs.append(str(doc) if doc is not None else "")
    return docs


def _question(result: JsonDict) -> JsonDict:
    questions = result.get("questions") or []
    if not questions:
        return {}
    first = questions[0]
    return first if isinstance(first, dict) else {}


def _load_or_run(
    *,
    checkpoint_path: Path,
    force: bool,
    api_base_url: str,
    bank_id: str,
    profile_id: str,
    fixture_name: str,
    fixture_override: JsonDict,
    timeout_seconds: float,
) -> JsonDict:
    if checkpoint_path.exists() and not force:
        return json.loads(checkpoint_path.read_text(encoding="utf-8"))

    result = run_pipeline(
        pipeline="recall",
        api_base_url=api_base_url,
        bank_id=bank_id,
        profile_id=profile_id,
        fixture_name=fixture_name,
        skip_retain=True,
        timeout_seconds=timeout_seconds,
        fixture_override=fixture_override,
    )
    checkpoint_path.parent.mkdir(parents=True, exist_ok=True)
    checkpoint_path.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    return result


def _profile_summary(rows: list[JsonDict], profile_id: str) -> JsonDict:
    profile_rows = [row for row in rows if row["profile_id"] == profile_id]
    at5 = [_metric(row["question"], "session_recall_at_5") for row in profile_rows]
    at10 = [_metric(row["question"], "session_recall_at_10") for row in profile_rows]
    return {
        "profile_id": profile_id,
        "case_count": len(profile_rows),
        "mean_session_recall_at_5": _mean(at5),
        "mean_session_recall_at_10": _mean(at10),
        "hit_cases_at_5": sum(1 for value in at5 if value and value > 0.0),
        "hit_cases_at_10": sum(1 for value in at10 if value and value > 0.0),
    }


def _write_markdown(summary: JsonDict, path: Path) -> None:
    profiles = summary["profiles"]
    comparison = summary["comparison"]
    lines = [
        "# SUM vs MAX Graph-Only Recall Comparison",
        "",
        f"- Generated: `{summary['generated_at']}`",
        f"- Fixture: `{summary['fixture']}`",
        f"- Bank prefix: `{summary['bank_prefix']}`",
        f"- Case range: `{summary['start_index']}..{summary['end_index']}`",
        f"- API base URL: `{summary['api_base_url']}`",
        "",
        "## Profile Metrics",
        "",
        "| Profile | Cases | Mean session recall@5 | Mean session recall@10 | Hit cases@5 | Hit cases@10 |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for item in profiles:
        lines.append(
            "| {profile_id} | {case_count} | {at5:.4f} | {at10:.4f} | {hit5} | {hit10} |".format(
                profile_id=item["profile_id"],
                case_count=item["case_count"],
                at5=item["mean_session_recall_at_5"] or 0.0,
                at10=item["mean_session_recall_at_10"] or 0.0,
                hit5=item["hit_cases_at_5"],
                hit10=item["hit_cases_at_10"],
            )
        )
    lines.extend(
        [
            "",
            "## SUM Minus MAX",
            "",
            f"- Delta mean session recall@5: `{comparison['delta_mean_session_recall_at_5']:.4f}`",
            f"- Delta mean session recall@10: `{comparison['delta_mean_session_recall_at_10']:.4f}`",
            f"- SUM better cases@5: `{comparison['sum_better_at_5']}`",
            f"- MAX better cases@5: `{comparison['max_better_at_5']}`",
            f"- Tied cases@5: `{comparison['tied_at_5']}`",
            f"- Different top-10 doc order cases: `{comparison['different_top10_doc_order_cases']}`",
            "",
            "## Per-Case Deltas",
            "",
            "| Case | Category | SUM@5 | MAX@5 | Delta@5 | Top-10 docs differ |",
            "|---|---|---:|---:|---:|---|",
        ]
    )
    for row in summary["per_case"]:
        lines.append(
            "| c{idx:03d} | {category} | {sum5:.4f} | {max5:.4f} | {delta5:.4f} | {diff} |".format(
                idx=row["index"],
                category=row["category"],
                sum5=row["sum_session_recall_at_5"] or 0.0,
                max5=row["max_session_recall_at_5"] or 0.0,
                delta5=row["delta_session_recall_at_5"] or 0.0,
                diff="yes" if row["top10_doc_order_differs"] else "no",
            )
        )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Compare E7G SUM vs E7GM MAX graph-only recall.")
    parser.add_argument("--fixture", choices=["longmemeval", "locomo"], default="longmemeval")
    parser.add_argument("--base-url", default=None)
    parser.add_argument("--bank-prefix", default="COGMEM_v16")
    parser.add_argument("--start-index", type=int, default=0)
    parser.add_argument("--end-index", type=int, default=34)
    parser.add_argument("--output-dir", default="experiments/v21_sum_vs_max_graph_only")
    parser.add_argument("--api-timeout", type=float, default=600.0)
    parser.add_argument("--force", action="store_true")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    api_base_url = resolve_api_base_url(args.base_url)
    fixture = get_fixture(args.fixture)
    output_dir = Path(args.output_dir)
    checkpoint_dir = output_dir / "checkpoints"

    rows: list[JsonDict] = []
    profiles = ("E7G", "E7GM")
    for idx in range(args.start_index, args.end_index + 1):
        mini = _benchmark_item_as_fixture(fixture, idx)
        bank_id = f"{args.bank_prefix}_c{idx:03d}"
        for profile_id in profiles:
            ckpt = checkpoint_dir / f"{profile_id}_recall_c{idx:03d}.json"
            result = _load_or_run(
                checkpoint_path=ckpt,
                force=args.force,
                api_base_url=api_base_url,
                bank_id=bank_id,
                profile_id=profile_id,
                fixture_name=args.fixture,
                fixture_override=mini,
                timeout_seconds=args.api_timeout,
            )
            q = _question(result)
            rows.append(
                {
                    "index": idx,
                    "profile_id": profile_id,
                    "category": q.get("category") or "unknown",
                    "question": q,
                    "top10_docs": _top_docs(q),
                }
            )
            at5 = _metric(q, "session_recall_at_5")
            print(f"{profile_id} c{idx:03d}: session_recall@5={at5 if at5 is not None else 'null'}")

    by_case: dict[int, dict[str, JsonDict]] = {}
    for row in rows:
        by_case.setdefault(row["index"], {})[row["profile_id"]] = row

    per_case: list[JsonDict] = []
    for idx in sorted(by_case):
        sum_row = by_case[idx]["E7G"]
        max_row = by_case[idx]["E7GM"]
        sum5 = _metric(sum_row["question"], "session_recall_at_5")
        max5 = _metric(max_row["question"], "session_recall_at_5")
        sum10 = _metric(sum_row["question"], "session_recall_at_10")
        max10 = _metric(max_row["question"], "session_recall_at_10")
        per_case.append(
            {
                "index": idx,
                "category": sum_row["category"],
                "sum_session_recall_at_5": sum5,
                "max_session_recall_at_5": max5,
                "delta_session_recall_at_5": None if sum5 is None or max5 is None else sum5 - max5,
                "sum_session_recall_at_10": sum10,
                "max_session_recall_at_10": max10,
                "delta_session_recall_at_10": None if sum10 is None or max10 is None else sum10 - max10,
                "top10_doc_order_differs": sum_row["top10_docs"] != max_row["top10_docs"],
            }
        )

    delta5 = [row["delta_session_recall_at_5"] for row in per_case if row["delta_session_recall_at_5"] is not None]
    delta10 = [row["delta_session_recall_at_10"] for row in per_case if row["delta_session_recall_at_10"] is not None]
    comparison = {
        "delta_mean_session_recall_at_5": float(statistics.fmean(delta5)) if delta5 else 0.0,
        "delta_mean_session_recall_at_10": float(statistics.fmean(delta10)) if delta10 else 0.0,
        "sum_better_at_5": sum(1 for value in delta5 if value > 0.0),
        "max_better_at_5": sum(1 for value in delta5 if value < 0.0),
        "tied_at_5": sum(1 for value in delta5 if value == 0.0),
        "different_top10_doc_order_cases": sum(1 for row in per_case if row["top10_doc_order_differs"]),
    }
    summary = {
        "generated_at": time.strftime("%Y-%m-%d %H:%M:%S"),
        "fixture": args.fixture,
        "api_base_url": api_base_url,
        "bank_prefix": args.bank_prefix,
        "start_index": args.start_index,
        "end_index": args.end_index,
        "profiles": [_profile_summary(rows, profile_id) for profile_id in profiles],
        "comparison": comparison,
        "per_case": per_case,
    }

    output_dir.mkdir(parents=True, exist_ok=True)
    summary_json = output_dir / "sum_vs_max_graph_only_summary.json"
    summary_md = output_dir / "SUM_VS_MAX_GRAPH_ONLY.md"
    summary_json.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    _write_markdown(summary, summary_md)
    print(f"summary_json={summary_json.as_posix()}")
    print(f"summary_md={summary_md.as_posix()}")


if __name__ == "__main__":
    main()
