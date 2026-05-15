"""Fetch all facts for a specific session (document_id) from a CogMem bank.

Usage:
    uv run python .claude/skills/cogmem-audit/scripts/fetch_session_facts.py \
        --bank-id COGMEM_EXP_v14_e567_c001 \
        --document-id answer_593bdffd_3

    uv run python .claude/skills/cogmem-audit/scripts/fetch_session_facts.py \
        --bank-id COGMEM_EXP_v14_e567_c001 \
        --document-id answer_593bdffd_3 \
        --limit 200 \
        --api-base http://localhost:8888
"""
import argparse
import json
import urllib.request
import urllib.parse
import urllib.error
import sys
try:
    sys.stdout.reconfigure(encoding='utf-8')
except AttributeError:
    pass


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--bank-id", required=True)
    parser.add_argument("--document-id", required=True, help="Session ID (document_id)")
    parser.add_argument("--limit", type=int, default=100)
    parser.add_argument("--fact-type", default=None, help="Optional fact type filter")
    parser.add_argument("--api-base", default="http://localhost:8888")
    args = parser.parse_args()

    params = {"document_id": args.document_id, "limit": args.limit}
    if args.fact_type:
        params["type"] = args.fact_type

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
