"""Recall top-k facts then run generation to get the model's actual answer.

Use ONLY when `generated_answer` is absent, null, or empty in the checkpoint file.
Do NOT call this if `generated_answer` already exists — use that field directly.

Usage:
    uv run python .claude/skills/cogmem-verify/scripts/generate_answer.py \
        --bank-id COGMEM_EXP_v14_e567_c001 \
        --query "How many model kits have I worked on or bought?" \
        --gold-answer "5" \
        --top-k 25

Output JSON:
    {
      "query": str,
      "gold_answer": str,
      "top_k_used": int,
      "model_answer": str,
      "recall_summary_top10": [{rank, id, document_id, ce_score, text}]
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

_TIMEOUT = 120


def post_json(url: str, payload: dict) -> dict:
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=data,
        headers={"Content-Type": "application/json", "Accept": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=_TIMEOUT) as resp:
        return json.loads(resp.read())


def main():
    parser = argparse.ArgumentParser(
        description="Recall + generate to get model answer when checkpoint has none."
    )
    parser.add_argument("--bank-id", required=True)
    parser.add_argument("--query", required=True)
    parser.add_argument("--gold-answer", default="", help="Expected answer for comparison")
    parser.add_argument("--top-k", type=int, default=25)
    parser.add_argument("--api-base", default="http://localhost:8888")
    args = parser.parse_args()

    # Step 1: Recall
    try:
        recall_resp = post_json(
            f"{args.api_base}/v1/default/banks/{args.bank_id}/memories/recall",
            {"query": args.query, "top_k": args.top_k, "trace": True},
        )
    except urllib.error.HTTPError as e:
        print(f"Recall HTTP {e.code}: {e.read().decode()}", file=sys.stderr)
        sys.exit(1)
    except urllib.error.URLError as e:
        print(f"Connection error (recall): {e.reason}", file=sys.stderr)
        sys.exit(1)

    results_raw = recall_resp.get("results") or recall_resp
    evidence = []
    recall_summary = []
    for rank, item in enumerate(results_raw, 1):
        evidence.append(item)
        recall_summary.append({
            "rank": rank,
            "id": item.get("id") or item.get("unit_id", ""),
            "document_id": item.get("document_id", ""),
            "ce_score": item.get("cross_encoder_score") or item.get("score"),
            "text": (item.get("text") or "")[:150],
        })

    # Step 2: Generate
    try:
        gen_resp = post_json(
            f"{args.api_base}/v1/default/banks/{args.bank_id}/memories/generate",
            {"query": args.query, "evidence": evidence},
        )
    except urllib.error.HTTPError as e:
        print(f"Generate HTTP {e.code}: {e.read().decode()}", file=sys.stderr)
        sys.exit(1)
    except urllib.error.URLError as e:
        print(f"Connection error (generate): {e.reason}", file=sys.stderr)
        sys.exit(1)

    output = {
        "query": args.query,
        "gold_answer": args.gold_answer,
        "top_k_used": args.top_k,
        "model_answer": gen_resp.get("answer", ""),
        "recall_summary_top10": recall_summary[:10],
    }
    print(json.dumps(output, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
