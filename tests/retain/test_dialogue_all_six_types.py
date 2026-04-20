"""Retain pipeline — Dialogue: All six fact types in one conversation.

Scenario:
  Jake is a DevOps engineer at CloudSys. The dialogue is deliberately crafted
  to contain a clear example of every CogMem fact type:
    - world      : Jake's role
    - experience : past deployment incident
    - opinion    : prefers GitOps over manual deployments
    - habit      : runs smoke tests after every deploy
    - intention  : plans to introduce chaos engineering
    - action_effect: enabled canary releases → reduced incident rate

Expected extraction (at minimum):
  - At least 4 of the 6 types present (some SLMs may miss 1-2)
  - Ideal: all 6 types extracted

Difficulty: HARD — all six types, requires LLM to correctly classify each.
  Test passes at 4+/6 to account for Ministral-3B limitations.
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
USER: Jake, tell me about your work at CloudSys.
JAKE: I am a DevOps engineer at CloudSys, responsible for the CI/CD platform.
USER: Has anything gone wrong recently?
JAKE: Last month we had a major outage when a bad config was pushed to production.
      It took 4 hours to recover. It was a painful incident.
USER: What is your philosophy on deployments?
JAKE: I strongly believe GitOps is far safer than manual deployments.
      Manual changes in production are a recipe for disaster.
USER: Any regular practices?
JAKE: I always run smoke tests immediately after every deployment. No exceptions.
USER: What are your plans going forward?
JAKE: I intend to introduce chaos engineering practices to the team by end of Q2 2026.
      We need to find weaknesses before production does.
USER: What have you already improved?
JAKE: We enabled canary releases six months ago. Our production incident rate dropped by 60%.
"""

_FAKE_RESPONSE = {
    "facts": [
        {
            "fact_type": "world",
            "what": "Jake is a DevOps engineer at CloudSys responsible for the CI/CD platform",
            "entities": ["Jake", "CloudSys"],
        },
        {
            "fact_type": "experience",
            "what": "CloudSys experienced a major production outage last month due to a bad config push, taking 4 hours to recover",
            "entities": ["Jake", "CloudSys"],
            "when": "last month",
            "fact_kind": "event",
        },
        {
            "fact_type": "opinion",
            "what": "Jake strongly believes GitOps is safer than manual deployments",
            "entities": ["Jake"],
            "confidence": 0.95,
        },
        {
            "fact_type": "habit",
            "what": "Jake always runs smoke tests immediately after every deployment",
            "entities": ["Jake"],
        },
        {
            "fact_type": "intention",
            "what": "Jake intends to introduce chaos engineering practices to the team by end of Q2 2026",
            "entities": ["Jake"],
            "intention_status": "planning",
        },
        {
            "fact_type": "action_effect",
            "what": "Enabling canary releases reduced CloudSys production incident rate by 60%",
            "entities": ["Jake", "CloudSys"],
            "precondition": "Production deployments were high-risk without traffic splitting",
            "action": "Enabled canary releases",
            "outcome": "Production incident rate dropped by 60%",
            "confidence": 0.9,
        },
    ]
}

_ALL_TYPES = {"world", "experience", "opinion", "habit", "intention", "action_effect"}
_MIN_TYPES = 4


async def run_test() -> None:
    from cogmem_api.engine.retain.fact_extraction import extract_facts_from_contents
    from cogmem_api.engine.retain.types import RetainContent

    content = RetainContent(
        content=DIALOGUE,
        context="all_six_types",
        event_date=datetime(2026, 4, 20, 9, 0, tzinfo=UTC),
    )

    facts, _chunks, _usage = await extract_facts_from_contents(
        contents=[content],
        llm_config=resolve_llm(_FAKE_RESPONSE),
        agent_name="test",
        config=make_config("verbose"),
    )

    found_types = {f.fact_type for f in facts}
    missing = _ALL_TYPES - found_types
    found_count = len(_ALL_TYPES & found_types)

    assert found_count >= _MIN_TYPES, (
        f"Expected at least {_MIN_TYPES}/6 types, got {found_count}/6. "
        f"Found: {found_types}. Missing: {missing}"
    )

    if found_count == 6:
        print("OK  all 6 fact types extracted")
    else:
        print(f"OK  {found_count}/6 fact types extracted (missing: {missing})")


def main() -> None:
    asyncio.run(run_test())
    print("All six-types dialogue retain tests passed.")


if __name__ == "__main__":
    main()
