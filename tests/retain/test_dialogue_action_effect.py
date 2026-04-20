"""Retain pipeline — Dialogue: Technical action-effect (causal triplets).

Scenario:
  An engineer faces two performance problems:
    1. API response time is 2 seconds under heavy load → added Redis cache → dropped to 200ms.
    2. Database timeouts spike under high traffic → enabled connection pooling → timeouts eliminated.

Expected extraction (at minimum):
  - 1+ "action_effect" facts  (Ministral-3B may merge into 1; 2 is ideal)
  - Each has metadata: precondition, action, outcome (all non-empty)
  - confidence in [0.0, 1.0]
  - devalue_sensitive is bool
  - at least one action_effect fact about caching/response-time (Redis or generic "cache"/"response")

Known flaky with Ministral-3B: model sometimes omits "Redis"/"cache" from entity/text and only
extracts the connection-pooling fact, causing the cache_fact assertion to fail.
"""

from __future__ import annotations

import asyncio
import sys
from datetime import UTC, datetime
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from tests.retain._shared import make_config, resolve_llm  # noqa: E402

DIALOGUE = """\
USER: Our system gets really slow when loading large datasets from the database.
ASSISTANT: Have you considered adding a caching layer?
USER: We did. After adding a Redis cache in the service layer, response time dropped from 2 seconds to 200ms.
ASSISTANT: Redis is very effective for read-heavy workloads. Any other issues?
USER: One more: when request volume spikes, the database keeps timing out.
      After enabling connection pooling, the timeouts went away and the system became stable.
"""

_FAKE_RESPONSE = {
    "facts": [
        {
            "fact_type": "action_effect",
            "what": "Adding Redis cache reduced API response time from 2s to 200ms",
            "entities": ["Redis"],
            "precondition": "API response time was 2 seconds under heavy data load",
            "action": "Added Redis caching layer to the service",
            "outcome": "Response time dropped from 2s to 200ms",
            "confidence": 0.95,
            "devalue_sensitive": True,
        },
        {
            "fact_type": "action_effect",
            "what": "Enabling connection pooling eliminated database timeout spikes under high traffic",
            "entities": [],
            "precondition": "Database timed out when request volume spiked",
            "action": "Enabled connection pooling",
            "outcome": "Database timeouts were eliminated and system became stable",
            "confidence": 0.88,
            "devalue_sensitive": True,
        },
    ]
}


async def run_test() -> None:
    from cogmem_api.engine.retain.fact_extraction import extract_facts_from_contents
    from cogmem_api.engine.retain.types import RetainContent

    content = RetainContent(
        content=DIALOGUE,
        context="system_debugging",
        event_date=datetime(2026, 4, 17, 14, 0, tzinfo=UTC),
    )

    facts, _chunks, _usage = await extract_facts_from_contents(
        contents=[content],
        llm_config=resolve_llm(_FAKE_RESPONSE),
        agent_name="test",
        config=make_config("verbose"),
    )

    ae_facts = [f for f in facts if f.fact_type == "action_effect"]
    assert len(ae_facts) >= 1, (
        f"Expected at least 1 action_effect fact. "
        f"Got fact_types: {[f.fact_type for f in facts]}"
    )

    for ae in ae_facts:
        assert ae.metadata.get("precondition"), \
            f"action_effect missing 'precondition'. metadata={ae.metadata}"
        assert ae.metadata.get("action"), \
            f"action_effect missing 'action'. metadata={ae.metadata}"
        assert ae.metadata.get("outcome"), \
            f"action_effect missing 'outcome'. metadata={ae.metadata}"

        confidence = ae.metadata.get("confidence")
        assert isinstance(confidence, float), \
            f"confidence must be float, got {type(confidence)}"
        assert 0.0 <= confidence <= 1.0, f"confidence out of range: {confidence}"

        devalue = ae.metadata.get("devalue_sensitive")
        assert isinstance(devalue, bool), \
            f"devalue_sensitive must be bool, got {type(devalue)}"

    # Accept: "redis" by name, OR any caching/response-time fact
    # (Ministral-3B may not preserve the specific tech name "Redis" in entities/text)
    _CACHE_KEYWORDS = ("redis", "cache", "cach", "response")
    cache_fact = next(
        (f for f in ae_facts if
         any(kw in e.lower() for kw in _CACHE_KEYWORDS for e in f.entities)
         or any(kw in f.fact_text.lower() for kw in _CACHE_KEYWORDS)),
        None,
    )
    assert cache_fact is not None, (
        f"Expected a caching/Redis action_effect fact. "
        f"Entities: {[f.entities for f in ae_facts]}, "
        f"Texts: {[f.fact_text[:80] for f in ae_facts]}"
    )

    if len(ae_facts) >= 2:
        print("OK  both action_effect facts extracted (Redis + connection pooling)")
    else:
        print(f"--  {len(ae_facts)} action_effect extracted (ideal: 2; model may merge)")

    print("OK  action_effect facts present")
    print("OK  precondition / action / outcome all set")
    print("OK  confidence in [0.0, 1.0]")
    print("OK  devalue_sensitive is bool")
    print("OK  caching/Redis action_effect found")


def main() -> None:
    asyncio.run(run_test())
    print("All action-effect dialogue retain tests passed.")


if __name__ == "__main__":
    main()
