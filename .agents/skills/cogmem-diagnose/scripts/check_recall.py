"""Re-run recall for a query with trace and report where specific fact IDs appear.

Useful for verifying or challenging a diagnosis: did the audit report's rank data
reflect the current pipeline state? Pass --fact-ids to highlight target facts.

Usage:
    # Basic recall with rank summary
    uv run python .claude/skills/cogmem-diagnose/scripts/check_recall.py \
        --bank-id COGMEM_EXP_v14_e567_c001 \
        --query "How many model kits have I worked on or bought?" \
        --top-k 50

    # Highlight specific fact IDs in output
    uv run python .claude/skills/cogmem-diagnose/scripts/check_recall.py \
        --bank-id COGMEM_EXP_v14_e567_c001 \
        --query "How many model kits have I worked on or bought?" \
        --top-k 50 \
        --fact-ids "49689465-e60c-4096-bccb-d2971f5e0659,c450e31f-bfea-4d1c-9037-c7fb924f7f9f"

Output JSON:
    {
      "query_type": str,
      "rrf_weights": {...},
      "results": [{rank, id, document_id, ce_score, combined_score, channel_ranks, text}],
      "target_facts": {fact_id: {rank, ce_score, channel_ranks} | "not_found"}
    }
"""
import argparse
import json
import sys
import urllib.error
import urllib.request

try:
    sys.stdout.reconfigure(encoding="utf-8")
except AttributeError:
    pass

_TIMEOUT = 60


def recall(api_base: str, bank_id: str, query: str, top_k: int) -> dict:
    url = f"{api_base}/v1/default/banks/{bank_id}/memories/recall"
    payload = json.dumps({
        "query": query,
        "top_k": top_k,
        "trace": True,
    }).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=payload,
        headers={"Content-Type": "application/json", "Accept": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=_TIMEOUT) as resp:
        return json.loads(resp.read())


def main():
    parser = argparse.ArgumentParser(description="Re-run recall and locate specific facts.")
    parser.add_argument("--bank-id", required=True)
    parser.add_argument("--query", required=True)
    parser.add_argument("--top-k", type=int, default=50)
    parser.add_argument(
        "--fact-ids",
        default="",
        help="Comma-separated fact UUIDs to locate in results",
    )
    parser.add_argument("--api-base", default="http://localhost:8888")
    args = parser.parse_args()

    target_ids = {fid.strip() for fid in args.fact_ids.split(",") if fid.strip()}

    try:
        raw = recall(args.api_base, args.bank_id, args.query, args.top_k)
    except urllib.error.HTTPError as e:
        print(f"HTTP {e.code}: {e.read().decode()}", file=sys.stderr)
        sys.exit(1)
    except urllib.error.URLError as e:
        print(f"Connection error: {e.reason}", file=sys.stderr)
        sys.exit(1)

    results_raw = raw.get("results") or raw  # handle both wrapped and bare list
    trace = raw.get("trace", {})

    results = []
    target_facts: dict = {fid: "not_found" for fid in target_ids}

    for rank, item in enumerate(results_raw, 1):
        fact_id = item.get("id") or item.get("unit_id", "")
        cr = item.get("channel_ranks") or {}
        entry = {
            "rank": rank,
            "id": fact_id,
            "document_id": item.get("document_id", ""),
            "ce_score": item.get("cross_encoder_score") or item.get("score"),
            "combined_score": item.get("combined_score") or item.get("score"),
            "channel_ranks": {
                "semantic": cr.get("semantic"),
                "bm25": cr.get("bm25"),
                "graph": cr.get("graph"),
                "temporal": cr.get("temporal"),
            },
            "text": (item.get("text") or "")[:200],
        }
        results.append(entry)
        if fact_id in target_ids:
            target_facts[fact_id] = {
                "rank": rank,
                "ce_score": entry["ce_score"],
                "combined_score": entry["combined_score"],
                "channel_ranks": entry["channel_ranks"],
                "text": entry["text"],
            }

    output = {
        "query_type": (trace.get("query_type") if isinstance(trace, dict) else None),
        "rrf_weights": (trace.get("rrf_weights") if isinstance(trace, dict) else None),
        "total_returned": len(results),
        "results": results,
        "target_facts": target_facts,
    }
    print(json.dumps(output, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
