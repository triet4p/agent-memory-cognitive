from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.retain_locomo_bank_sessions import _build_items_for_conv_index


def main() -> None:
    conv50_items = _build_items_for_conv_index(94)
    conv47_items = _build_items_for_conv_index(132)

    assert conv50_items, "conv-50 should expose retainable session items"
    assert conv47_items, "conv-47 should expose retainable session items"

    conv50_ids = [item["document_id"] for item in conv50_items]
    conv47_ids = [item["document_id"] for item in conv47_items]

    assert conv50_ids == sorted(conv50_ids, key=lambda s: int(s[1:])), conv50_ids
    assert conv47_ids == sorted(conv47_ids, key=lambda s: int(s[1:])), conv47_ids
    assert len(set(conv50_ids)) == len(conv50_ids), conv50_ids
    assert len(set(conv47_ids)) == len(conv47_ids), conv47_ids

    for item in conv50_items + conv47_items:
        assert item.get("messages"), f"expected messages payload for {item['document_id']}"

    print("task_s35_t8f_sessionwise_retain: OK")


if __name__ == "__main__":
    main()
