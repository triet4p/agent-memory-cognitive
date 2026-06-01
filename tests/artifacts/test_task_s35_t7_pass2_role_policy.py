"""S35-T7 artifact: Pass 2 role policy for real-world transcript roles.

Verifies:
1. Standard user/assistant chat still runs Pass 2 only for user turns.
2. LoCoMo-style named speakers infer non-machine roles when no user role exists.
3. Machine-only transcripts do not trigger Pass 2.
4. Explicit configured target roles are respected.
5. Pseudo roles "human"/"participant" expand to non-reserved roles.

Run: uv run python tests/artifacts/test_task_s35_t7_pass2_role_policy.py
"""

from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from cogmem_api.engine.retain.chunking import chunk_for_pass2, resolve_pass2_target_roles


def _chunks_for_policy(messages: list[dict[str, str]], configured_roles: tuple[str, ...] = ("user",)):
    roles = resolve_pass2_target_roles(messages, configured_roles)
    chunks = []
    for role in roles:
        chunks.extend(
            chunk_for_pass2(
                messages,
                target_role=role,
                max_chars=3000,
                include_role_marker=role != "user",
            )
        )
    return roles, chunks


def test_standard_chat_stays_user_only() -> None:
    messages = [
        {"role": "user", "content": "I bought a Tiger I kit."},
        {"role": "assistant", "content": "Great choice."},
        {"role": "user", "content": "I want to try weathering."},
    ]
    roles, chunks = _chunks_for_policy(messages)
    texts = [chunk.text for chunk in chunks]

    assert roles == ("user",)
    assert len(chunks) == 2
    assert any("Tiger I" in text for text in texts)
    assert any("weathering" in text for text in texts)
    assert not any("Great choice" in text for text in texts)
    assert not any(text.startswith("[user]:") for text in texts)
    print("[ok] standard user/assistant chat -> Pass 2 keeps user-only behavior")


def test_named_speakers_are_inferred_when_no_user_role() -> None:
    messages = [
        {"role": "Jon", "content": "I lost my banking job yesterday."},
        {"role": "Gina", "content": "I launched an online store last month."},
        {"role": "Jon", "content": "I plan to open a dance studio."},
    ]
    roles, chunks = _chunks_for_policy(messages)
    texts = [chunk.text for chunk in chunks]

    assert roles == ("jon", "gina")
    assert len(chunks) == 3
    assert any(text.startswith("[jon]:") and "banking job" in text for text in texts)
    assert any(text.startswith("[gina]:") and "online store" in text for text in texts)
    assert any(text.startswith("[jon]:") and "dance studio" in text for text in texts)
    print("[ok] named speaker transcript without user role -> Pass 2 infers both speakers")


def test_machine_only_roles_do_not_trigger_pass2() -> None:
    messages = [
        {"role": "system", "content": "You are an assistant."},
        {"role": "assistant", "content": "I can help."},
        {"role": "tool", "content": "{\"ok\": true}"},
    ]
    roles, chunks = _chunks_for_policy(messages)

    assert roles == ()
    assert chunks == []
    print("[ok] machine-only transcript -> no Pass 2 chunks")


def test_explicit_target_role_is_respected() -> None:
    messages = [
        {"role": "speaker_a", "content": "I bought a power bank."},
        {"role": "speaker_b", "content": "I prefer paper maps."},
    ]
    roles, chunks = _chunks_for_policy(messages, configured_roles=("speaker_a",))

    assert roles == ("speaker_a",)
    assert len(chunks) == 1
    assert chunks[0].text.startswith("[speaker_a]:")
    assert "power bank" in chunks[0].text
    assert "paper maps" not in chunks[0].text
    print("[ok] explicit target role -> only configured speaker is processed")


def test_human_pseudo_role_expands_to_non_reserved_roles() -> None:
    messages = [
        {"role": "speaker_a", "content": "I adopted a cat named Luna."},
        {"role": "assistant", "content": "That is lovely."},
        {"role": "tool", "content": "ignored"},
        {"role": "speaker_b", "content": "I am planning a trip to Hue."},
    ]
    roles, chunks = _chunks_for_policy(messages, configured_roles=("human",))
    texts = [chunk.text for chunk in chunks]

    assert roles == ("speaker_a", "speaker_b")
    assert len(chunks) == 2
    assert any(text.startswith("[speaker_a]:") and "Luna" in text for text in texts)
    assert any(text.startswith("[speaker_b]:") and "Hue" in text for text in texts)
    assert not any("lovely" in text or "ignored" in text for text in texts)
    print("[ok] human pseudo-role -> expands to non-reserved speaker roles")


def main() -> int:
    test_standard_chat_stays_user_only()
    test_named_speakers_are_inferred_when_no_user_role()
    test_machine_only_roles_do_not_trigger_pass2()
    test_explicit_target_role_is_respected()
    test_human_pseudo_role_expands_to_non_reserved_roles()
    print("\nS35-T7 PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
