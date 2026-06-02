"""Fetch facts from a CogMem bank by keyword, document_id, or all.

Usage:
    # Search by keyword (matches text field)
    uv run python .claude/skills/cogmem-diagnose/scripts/get_fact.py \
        --bank-id COGMEM_EXP_v14_e567_c001 \
        --keyword "Tiger I tank"

    # All facts from a specific session
    uv run python .claude/skills/cogmem-diagnose/scripts/get_fact.py \
        --bank-id COGMEM_EXP_v14_e567_c001 \
        --document-id answer_593bdffd_3

    # All facts in bank (large — use sparingly)
    uv run python .claude/skills/cogmem-diagnose/scripts/get_fact.py \
        --bank-id COGMEM_EXP_v14_e567_c001 \
        --all

Output: JSON array of fact objects with id, text, fact_type, document_id, raw_snippet.
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


def main():
    parser = argparse.ArgumentParser(description="Fetch facts from a CogMem bank.")
    parser.add_argument("--bank-id", required=True)
    parser.add_argument("--keyword", default=None, help="Text keyword to search")
    parser.add_argument("--document-id", default=None, help="Session ID filter")
    parser.add_argument("--all", action="store_true", help="Fetch all facts (ignores keyword/document-id)")
    parser.add_argument("--limit", type=int, default=200)
    parser.add_argument("--api-base", default="http://localhost:8888")
    args = parser.parse_args()

    if args.all:
        url = f"{args.api_base}/v1/default/banks/{args.bank_id}/facts/all"
        req = urllib.request.Request(url, headers={"Accept": "application/json"})
    else:
        params: dict = {"limit": args.limit}
        if args.keyword:
            params["keyword"] = args.keyword
        if args.document_id:
            params["document_id"] = args.document_id
        qs = urllib.parse.urlencode(params)
        url = f"{args.api_base}/v1/default/banks/{args.bank_id}/facts?{qs}"
        req = urllib.request.Request(url, headers={"Accept": "application/json"})

    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read())
        print(json.dumps(data, ensure_ascii=False, indent=2))
    except urllib.error.HTTPError as e:
        print(f"HTTP {e.code}: {e.read().decode()}", file=sys.stderr)
        sys.exit(1)
    except urllib.error.URLError as e:
        print(f"Connection error: {e.reason}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
