"""
Phase 3 orchestrator: probes ALL 7 link types for a keyword in one shot.

The agent no longer needs to call search_links.py 7 times manually — this script
runs all link types, computes per-type summary stats, and outputs a single JSON.

Usage:
    uv run python .claude/skills/cogmem-audit/scripts/run_phase3.py \
        --bank-id COGMEM_EXP_v14_e567_c001 \
        --keyword "Tiger I" \
        --gold-session-ids "answer_593bdffd_1,answer_593bdffd_2,answer_593bdffd_3,answer_593bdffd_4"

    # Multiple facts: run once per fact
    uv run python .claude/skills/cogmem-audit/scripts/run_phase3.py \
        --bank-id COGMEM_EXP_v14_e567_c001 \
        --keyword "F-15 Eagle" \
        --gold-session-ids "answer_593bdffd_1"

Output JSON structure:
    {
      "keyword": str,
      "summary_table": [
        {
          "link_type": str,
          "count": int,
          "avg_weight": float | null,
          "cross_session_count": int,
          "cross_session_to_non_gold": int,   # cross-session links to non-gold sessions (BFS budget waste)
          "samples": [{from, to, weight, from_doc, to_doc}, ...]
        },
        ...
      ],
      "connectivity_class": str,   # Well-connected | Weakly connected | Isolated | BFS-diluted
      "connectivity_evidence": str
    }
"""
import argparse
import json
import sys
import urllib.error
import urllib.parse
import urllib.request

LINK_TYPES = ["entity", "semantic", "causal", "temporal", "s_r_link", "a_o_causal", "transition"]


def _search(api_base: str, bank_id: str, keyword: str, link_type: str, limit: int) -> list:
    params = {"keyword": keyword, "link_type": link_type, "limit": limit}
    qs = urllib.parse.urlencode(params)
    url = f"{api_base}/v1/default/banks/{bank_id}/relationships/search?{qs}"
    req = urllib.request.Request(url, headers={"Accept": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read())
    except urllib.error.HTTPError as e:
        print(f"  HTTP {e.code} for link_type={link_type}: {e.read().decode()}", file=sys.stderr)
        return []
    except urllib.error.URLError as e:
        print(f"  Connection error for link_type={link_type}: {e.reason}", file=sys.stderr)
        return []


def _summarize(links: list, gold_ids: set) -> dict:
    if not links:
        return {
            "count": 0,
            "avg_weight": None,
            "cross_session_count": 0,
            "cross_session_to_non_gold": 0,
            "samples": [],
        }

    weights = [float(lk["weight"]) for lk in links if lk.get("weight") is not None]
    avg_w = round(sum(weights) / len(weights), 3) if weights else None

    cross = [
        lk for lk in links
        if lk.get("from_document_id") != lk.get("to_document_id")
    ]
    cross_to_non_gold = [
        lk for lk in cross
        if gold_ids and lk.get("to_document_id") not in gold_ids
    ] if gold_ids else []

    samples = [
        {
            "from": (lk.get("from_text") or "")[:100],
            "to": (lk.get("to_text") or "")[:100],
            "weight": lk.get("weight"),
            "from_doc": lk.get("from_document_id"),
            "to_doc": lk.get("to_document_id"),
        }
        for lk in links[:3]
    ]

    return {
        "count": len(links),
        "avg_weight": avg_w,
        "cross_session_count": len(cross),
        "cross_session_to_non_gold": len(cross_to_non_gold),
        "samples": samples,
    }


def _classify(summary_table: list) -> tuple[str, str]:
    """Assign connectivity class from summary stats."""
    entity = next((r for r in summary_table if r["link_type"] == "entity"), {})
    causal = next((r for r in summary_table if r["link_type"] == "causal"), {})
    semantic = next((r for r in summary_table if r["link_type"] == "semantic"), {})
    total_links = sum(r["count"] for r in summary_table)
    total_cross_non_gold = sum(r["cross_session_to_non_gold"] for r in summary_table)

    strong_entity = (entity.get("count", 0) > 0 and (entity.get("avg_weight") or 0) > 0.7
                     and entity.get("cross_session_count", 0) < entity.get("count", 1))
    strong_causal = (causal.get("count", 0) > 0 and (causal.get("avg_weight") or 0) > 0.7)

    if total_links <= 1:
        return "Isolated", f"Only {total_links} link(s) total — cut off from BFS"

    if (strong_entity or strong_causal):
        if total_cross_non_gold > 10:
            return (
                "BFS-diluted",
                f"Has strong entity/causal links but {total_cross_non_gold} cross-session links "
                f"to non-gold sessions consume BFS budget",
            )
        return "Well-connected", f"Strong entity/causal links (weight>0.7) within session"

    if semantic.get("count", 0) > 0 or total_links > 5:
        if total_cross_non_gold > 10:
            return (
                "BFS-diluted",
                f"{total_cross_non_gold} cross-session links to non-gold sessions dilute BFS activation",
            )
        return "Weakly connected", "Only low-weight semantic links or links to non-gold sessions"

    return "Weakly connected", f"{total_links} total links but no strong entity/causal path"


def main() -> None:
    parser = argparse.ArgumentParser(description="Phase 3: probe all 7 link types")
    parser.add_argument("--bank-id", required=True)
    parser.add_argument("--keyword", required=True, help="Distinctive keyword from fact text")
    parser.add_argument("--gold-session-ids", default=None,
                        help="Comma-separated gold document_ids to detect BFS budget waste")
    parser.add_argument("--limit", type=int, default=200)
    parser.add_argument("--api-base", default="http://localhost:8888")
    args = parser.parse_args()

    gold_ids: set = set(args.gold_session_ids.split(",")) if args.gold_session_ids else set()

    summary_table = []
    details = {}

    for lt in LINK_TYPES:
        print(f"→ Probing link_type={lt}...", file=sys.stderr)
        links = _search(args.api_base, args.bank_id, args.keyword, lt, args.limit)
        s = _summarize(links, gold_ids)
        summary_table.append({"link_type": lt, **s})
        details[lt] = {"summary": s, "raw_count": len(links)}

    connectivity_class, connectivity_evidence = _classify(summary_table)

    print(json.dumps({
        "keyword": args.keyword,
        "bank_id": args.bank_id,
        "summary_table": summary_table,
        "connectivity_class": connectivity_class,
        "connectivity_evidence": connectivity_evidence,
        "details": details,
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
