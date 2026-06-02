"""
Phase 2 orchestrator: runs BOTH recall calls (top-25 + top-300) with trace=True,
then merges results into a single structured JSON for the agent to analyze.

The agent no longer needs to call recall.py manually — this script guarantees
both calls are made with --trace and outputs clean data for classification.

Usage:
    uv run python .claude/skills/cogmem-audit/scripts/run_phase2.py \
        --bank-id COGMEM_EXP_v14_e567_c001 \
        --query "How many model kits have I worked on or bought?" \
        --gold-session-ids "answer_593bdffd_1,answer_593bdffd_2,answer_593bdffd_3,answer_593bdffd_4"

Output JSON structure:
    {
      "trace": {"query_type": "...", "rrf_weights": {...}},
      "top25": [...],              # ranks 1-25, full channel_ranks
      "top300_extended": [...],   # ranks 26-300 only (not in top25)
      "facts_by_id": {...},       # keyed by fact id for instant lookup
    }

Each result entry:
    {
      "rank": int,
      "id": str,
      "text": str (truncated 200 chars),
      "fact_type": str,
      "document_id": str,
      "gold_tag": "gold" | "non-gold" | null,
      "rrf_rank": int,
      "global_rrf_rank": int,
      "ce_score": float,
      "combined_score": float,
      "channel_ranks": {"semantic": int|null, "bm25": int|null, "graph": int|null, "temporal": int|null}
    }
"""
import argparse
import json
import sys
import urllib.error
import urllib.request


def _recall(api_base: str, bank_id: str, query: str, top_k: int) -> dict:
    url = f"{api_base}/v1/default/banks/{bank_id}/memories/recall"
    body = json.dumps({"query": query, "top_k": top_k, "trace": True}).encode()
    req = urllib.request.Request(
        url, data=body,
        headers={"Content-Type": "application/json", "Accept": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=120) as resp:
            return json.loads(resp.read())
    except urllib.error.HTTPError as e:
        print(f"HTTP {e.code}: {e.read().decode()}", file=sys.stderr)
        sys.exit(1)
    except urllib.error.URLError as e:
        print(f"Connection error: {e.reason}", file=sys.stderr)
        sys.exit(1)


def _extract(item: dict, rank: int, gold_ids: set) -> dict:
    cr = item.get("channel_ranks")
    if cr is None:
        cr = {}
    return {
        "rank": rank,
        "id": item.get("id"),
        "text": (item.get("text") or "")[:200],
        "fact_type": item.get("fact_type"),
        "document_id": item.get("document_id"),
        "gold_tag": ("gold" if item.get("document_id") in gold_ids else "non-gold") if gold_ids else None,
        "rrf_rank": item.get("rrf_rank"),
        "global_rrf_rank": item.get("global_rrf_rank"),
        "ce_score": round(float(item.get("cross_encoder_score") or 0), 4),
        "combined_score": item.get("score") or item.get("combined_score"),
        "channel_ranks": {
            "semantic": cr.get("semantic"),
            "bm25": cr.get("bm25"),
            "graph": cr.get("graph"),
            "temporal": cr.get("temporal"),
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Phase 2: dual recall with trace")
    parser.add_argument("--bank-id", required=True)
    parser.add_argument("--query", required=True)
    parser.add_argument("--gold-session-ids", default=None,
                        help="Comma-separated gold document_ids for gold_tag annotation")
    parser.add_argument("--api-base", default="http://localhost:8888")
    args = parser.parse_args()

    gold_ids: set = set(args.gold_session_ids.split(",")) if args.gold_session_ids else set()

    print("→ Running top-25 recall (trace=True)...", file=sys.stderr)
    r25 = _recall(args.api_base, args.bank_id, args.query, 25)

    print("→ Running top-300 recall (trace=True)...", file=sys.stderr)
    r300 = _recall(args.api_base, args.bank_id, args.query, 300)

    results25 = r25.get("results", [])
    results300 = r300.get("results", [])
    trace = r25.get("trace") or {}

    # Validate --trace worked: channel_ranks must be a dict, not None
    if results25 and results25[0].get("channel_ranks") is None:
        print(
            "ERROR: channel_ranks is null in top-25 results — trace did not activate.\n"
            f"trace field from response: {r25.get('trace')!r}",
            file=sys.stderr,
        )
        sys.exit(1)

    ids_in_25 = {item.get("id") for item in results25}

    top25 = [_extract(item, i + 1, gold_ids) for i, item in enumerate(results25)]
    top300_extended = [
        _extract(item, i + 1, gold_ids)
        for i, item in enumerate(results300)
        if item.get("id") not in ids_in_25
    ]

    facts_by_id = {r["id"]: r for r in top25 + top300_extended}

    print(json.dumps({
        "trace": {
            "query_type": trace.get("query_type"),
            "rrf_weights": trace.get("rrf_weights"),
        },
        "top25": top25,
        "top300_extended": top300_extended,
        "facts_by_id": facts_by_id,
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding='utf-8')
    main()
