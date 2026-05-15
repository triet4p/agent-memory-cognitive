"""Search relationships (graph edges) in a CogMem bank.

Use to verify or supplement the graph analysis section of an audit report.
Can filter by keyword (matched against fact text or document_id) and/or link_type.

Link types: entity, semantic, causal, temporal, s_r_link, a_o_causal, transition

Usage:
    # All link types for a keyword
    uv run python .claude/skills/cogmem-diagnose/scripts/get_links.py \
        --bank-id COGMEM_EXP_v14_e567_c001 \
        --keyword "Tiger I"

    # Specific link type only
    uv run python .claude/skills/cogmem-diagnose/scripts/get_links.py \
        --bank-id COGMEM_EXP_v14_e567_c001 \
        --keyword "Tiger I" \
        --link-type entity

    # All link types, summary by type
    uv run python .claude/skills/cogmem-diagnose/scripts/get_links.py \
        --bank-id COGMEM_EXP_v14_e567_c001 \
        --keyword "Tiger I" \
        --summarize

Output JSON:
    {
      "total": int,
      "by_type": {"entity": N, "semantic": N, ...},
      "links": [{link_type, weight, from_id, from_document_id, from_text, to_id, to_document_id, to_text}]
    }
"""
import argparse
import json
import sys
import urllib.error
import urllib.parse
import urllib.request

try:
    sys.stdout.reconfigure(encoding="utf-8")
except AttributeError:
    pass

ALL_LINK_TYPES = ["entity", "semantic", "causal", "temporal", "s_r_link", "a_o_causal", "transition"]


def fetch_links(api_base: str, bank_id: str, keyword: str | None, link_type: str | None, limit: int) -> list:
    params: dict = {"limit": limit}
    if keyword:
        params["keyword"] = keyword
    if link_type:
        params["link_type"] = link_type
    qs = urllib.parse.urlencode(params)
    url = f"{api_base}/v1/default/banks/{bank_id}/relationships/search?{qs}"
    req = urllib.request.Request(url, headers={"Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read())


def main():
    parser = argparse.ArgumentParser(description="Search relationships in a CogMem bank.")
    parser.add_argument("--bank-id", required=True)
    parser.add_argument("--keyword", default=None, help="Text keyword to match facts")
    parser.add_argument(
        "--link-type",
        default=None,
        choices=ALL_LINK_TYPES + [None],  # type: ignore[arg-type]
        help="Filter to a specific link type. Omit to fetch all types.",
    )
    parser.add_argument("--limit", type=int, default=200)
    parser.add_argument("--summarize", action="store_true", help="Show count summary by link type")
    parser.add_argument("--api-base", default="http://localhost:8888")
    args = parser.parse_args()

    try:
        if args.link_type:
            links = fetch_links(args.api_base, args.bank_id, args.keyword, args.link_type, args.limit)
        else:
            # Fetch all types in one call (API supports no filter = all types)
            links = fetch_links(args.api_base, args.bank_id, args.keyword, None, args.limit)
    except urllib.error.HTTPError as e:
        print(f"HTTP {e.code}: {e.read().decode()}", file=sys.stderr)
        sys.exit(1)
    except urllib.error.URLError as e:
        print(f"Connection error: {e.reason}", file=sys.stderr)
        sys.exit(1)

    by_type: dict[str, int] = {}
    normalized = []
    for lnk in links:
        lt = lnk.get("link_type", "unknown")
        by_type[lt] = by_type.get(lt, 0) + 1
        normalized.append({
            "link_type": lt,
            "weight": lnk.get("weight"),
            "from_id": lnk.get("from_unit_id"),
            "from_document_id": lnk.get("from_document_id"),
            "from_text": (lnk.get("from_text") or "")[:120],
            "to_id": lnk.get("to_unit_id"),
            "to_document_id": lnk.get("to_document_id"),
            "to_text": (lnk.get("to_text") or "")[:120],
        })

    output = {
        "total": len(normalized),
        "by_type": by_type,
        "links": normalized if not args.summarize else normalized[:20],
    }
    print(json.dumps(output, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
