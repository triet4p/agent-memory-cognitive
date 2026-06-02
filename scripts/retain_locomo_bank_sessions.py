from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any

import requests

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.eval_cogmem import _benchmark_item_as_fixture, get_fixture, resolve_api_base_url


def _build_items_for_conv_index(conv_index: int) -> list[dict[str, Any]]:
    fixture = get_fixture("locomo")
    mini = _benchmark_item_as_fixture(fixture, conv_index)
    messages_data = mini.get("_messages") or []
    sessions_data = mini.get("_sessions") or []

    items: list[dict[str, Any]] = []
    if messages_data:
        for session_id, msgs in messages_data:
            items.append({"messages": msgs, "document_id": session_id})
        return items

    for session_id, turns in sessions_data:
        items.append({"content": "\n\n".join(turns), "document_id": session_id})
    return items


def _delete_bank_if_requested(api_base_url: str, bank_id: str, enabled: bool) -> None:
    if not enabled:
        return
    response = requests.delete(f"{api_base_url}/v1/default/banks/{bank_id}", timeout=60)
    # Deleting a missing bank is fine for reruns; keep the flow idempotent.
    if response.status_code not in (200, 404):
        response.raise_for_status()


def _retain_one_item(api_base_url: str, bank_id: str, item: dict[str, Any], timeout_seconds: float) -> dict[str, Any]:
    response = requests.post(
        f"{api_base_url}/v1/default/banks/{bank_id}/memories",
        json={"items": [item], "async": False},
        timeout=timeout_seconds,
    )
    if not response.ok:
        print(f"[ERROR] retain failed for {item.get('document_id')}: {response.status_code}", file=sys.stderr)
        print(response.text, file=sys.stderr)
    response.raise_for_status()
    return response.json()


def main() -> None:
    parser = argparse.ArgumentParser(description="Retain one LoCoMo conversation session-by-session into a bank.")
    parser.add_argument("--conv-index", type=int, required=True, help="LoCoMo QA index identifying the target conversation.")
    parser.add_argument("--bank-id", required=True, help="Target bank ID.")
    parser.add_argument("--api-base-url", default=None, help="CogMem API base URL. Defaults to env or http://localhost:8888")
    parser.add_argument("--api-timeout", type=float, default=1800.0, help="Per-session retain timeout in seconds.")
    parser.add_argument(
        "--delete-bank",
        action="store_true",
        help="Delete the target bank before retaining. Safe for reruns of the same bank.",
    )
    args = parser.parse_args()

    api_base_url = resolve_api_base_url(args.api_base_url)
    items = _build_items_for_conv_index(args.conv_index)
    if not items:
        raise SystemExit(f"No session items found for conv-index {args.conv_index}")

    _delete_bank_if_requested(api_base_url, args.bank_id, args.delete_bank)

    print(
        f"[retain-sessionwise] bank={args.bank_id} conv_index={args.conv_index} "
        f"sessions={len(items)} timeout={args.api_timeout:.0f}s",
        flush=True,
    )

    total_units = 0
    for idx, item in enumerate(items, start=1):
        document_id = str(item.get("document_id") or f"session_{idx}")
        print(f"[{idx}/{len(items)}] retaining {document_id}", flush=True)
        result = _retain_one_item(api_base_url, args.bank_id, item, timeout_seconds=args.api_timeout)
        unit_count = len(result.get("unit_ids") or [])
        total_units += unit_count
        print(f"[{idx}/{len(items)}] {document_id} -> {unit_count} units", flush=True)

    print(
        f"[retain-sessionwise] complete bank={args.bank_id} sessions={len(items)} total_units={total_units}",
        flush=True,
    )


if __name__ == "__main__":
    main()
