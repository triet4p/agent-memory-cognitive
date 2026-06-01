"""S35-T8B artifact: minimal temporal-anchor prompt variant.

Verifies:
  - v3_temporal dispatch works via env.
  - v3_temporal keeps v2 shape and adds exactly the temporal-anchor rule.
  - v2 remains free of the new temporal-anchor rule.
  - No brand-disambiguation or counterfactual rules are added in T8B.

Run: uv run python tests/artifacts/test_task_s35_t8b_temporal_prompt.py
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from cogmem_api.engine import eval_helpers
from cogmem_api.prompts.eval.generate import build_generation_prompt_v2, build_generation_prompt_v3_temporal


EVIDENCE = [
    {
        "text": "John has a basketball game in Seattle next month",
        "raw_snippet": "[john]: I have a basketball game in Seattle next month.",
        "document_id": "D3",
    },
    {
        "text": "John plans a trip to Chicago",
        "raw_snippet": "[john]: I am going to Chicago after the Seattle game.",
        "document_id": "D4",
    },
]
QUERY = "Where was John going before Chicago?"
SESSION_DATE_MAP = {"D3": "2023-08-12", "D4": "2023-09-01"}


def test_v2_has_no_t8b_temporal_anchor_rule() -> None:
    prompt = build_generation_prompt_v2(
        QUERY,
        EVIDENCE,
        session_date_map=SESSION_DATE_MAP,
        include_snippets=True,
    )
    assert "before a Chicago trip" not in prompt
    assert "brand" not in prompt.lower()
    assert "counterfactual" not in prompt.lower()
    assert "Date: 2023-08-12" in prompt
    print("[ok] v2 unchanged: no T8B temporal-anchor rule")


def test_v3_temporal_adds_only_temporal_anchor_rule() -> None:
    prompt = build_generation_prompt_v3_temporal(
        QUERY,
        EVIDENCE,
        session_date_map=SESSION_DATE_MAP,
        include_snippets=True,
    )
    assert "explicit identifier" in prompt  # v2 core rule retained
    assert "before a Chicago trip" in prompt
    assert "first find" in prompt and "Chicago-trip memory/date" in prompt
    assert "Date: 2023-08-12" in prompt
    assert "brand" not in prompt.lower()
    assert "counterfactual" not in prompt.lower()
    print("[ok] v3_temporal adds temporal anchor example without extra rule families")


def test_env_dispatch_for_v3_temporal_aliases() -> None:
    for variant in ("v3_temporal", "v3-temporal", "v3"):
        os.environ["COGMEM_API_GENERATE_PROMPT_VARIANT"] = variant
        try:
            prompt = eval_helpers.build_generation_prompt(
                QUERY,
                EVIDENCE,
                session_date_map=SESSION_DATE_MAP,
                include_snippets=True,
            )
            assert "before a Chicago trip" in prompt
        finally:
            os.environ.pop("COGMEM_API_GENERATE_PROMPT_VARIANT", None)
    print("[ok] env dispatch routes v3_temporal/v3-temporal/v3 to temporal variant")


def main() -> int:
    test_v2_has_no_t8b_temporal_anchor_rule()
    test_v3_temporal_adds_only_temporal_anchor_rule()
    test_env_dispatch_for_v3_temporal_aliases()
    print("\nS35-T8B PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
