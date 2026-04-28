"""Artifact test for Task 778 — API structured messages input.

Verifies:
1. RetainItem accepts messages field
2. MessageInput model exists
3. RetainContent accepts messages
4. _build_retain_payload derives content from messages when provided
5. chunk_id is included in RecallResult
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))


def test_message_input_exists():
    from cogmem_api.api.http import MessageInput
    msg = MessageInput(role="user", content="hello")
    assert msg.role == "user"
    assert msg.content == "hello"
    print("PASS: MessageInput model exists and works")


def test_retain_item_messages_field():
    from cogmem_api.api.http import RetainItem
    item = RetainItem(
        messages=[{"role": "user", "content": "hello"}, {"role": "assistant", "content": "hi"}]
    )
    assert item.messages is not None
    assert len(item.messages) == 2
    assert item.content is None
    print("PASS: RetainItem accepts messages field")


def test_retain_item_content_still_works():
    from cogmem_api.api.http import RetainItem
    item = RetainItem(content="hello world")
    assert item.content == "hello world"
    assert item.messages is None
    print("PASS: RetainItem content field still works (backward compat)")


def test_retain_item_rejects_empty():
    from cogmem_api.api.http import RetainItem
    try:
        RetainItem(content="")
        print("FAIL: RetainItem should reject empty content")
        return False
    except ValueError:
        print("PASS: RetainItem rejects empty content/messages")


def test_retain_item_rejects_empty_messages():
    from cogmem_api.api.http import RetainItem
    try:
        RetainItem(messages=[])
        print("FAIL: RetainItem should reject empty messages")
        return False
    except ValueError:
        print("PASS: RetainItem rejects empty messages list")


def test_build_retain_payload_from_messages():
    from cogmem_api.api.http import RetainItem, _build_retain_payload
    item = RetainItem(
        messages=[
            {"role": "user", "content": "I bought a Tiger I kit"},
            {"role": "assistant", "content": "Great choice! What scale?"},
            {"role": "user", "content": "1/16 scale"},
        ]
    )
    payload = _build_retain_payload(item)
    assert payload is not None
    assert "content" in payload
    assert "[user]:" in payload["content"]
    assert "Tiger I" in payload["content"]
    assert "messages" in payload
    assert len(payload["messages"]) == 3
    print("PASS: _build_retain_payload derives content from messages")


def test_build_retain_payload_from_content():
    from cogmem_api.api.http import RetainItem, _build_retain_payload
    item = RetainItem(content="plain text content")
    payload = _build_retain_payload(item)
    assert payload is not None
    assert payload["content"] == "plain text content"
    assert "messages" not in payload
    print("PASS: _build_retain_payload works with content (backward compat)")


def test_retain_content_accepts_messages():
    from cogmem_api.engine.retain.types import RetainContent
    content = RetainContent.from_dict({
        "content": "",
        "messages": [{"role": "user", "content": "hello"}],
        "document_id": "doc1",
    })
    assert content.messages is not None
    assert len(content.messages) == 1
    assert content.messages[0]["role"] == "user"
    print("PASS: RetainContent.from_dict accepts messages field")


def test_retain_content_messages_none_when_absent():
    from cogmem_api.engine.retain.types import RetainContent
    content = RetainContent.from_dict({"content": "plain"})
    assert content.messages is None
    print("PASS: RetainContent.messages is None when not provided")


def test_recall_result_has_chunk_id():
    from cogmem_api.api.http import RecallResult
    result = RecallResult(
        id="123",
        text="some text",
        type="experience",
        chunk_id="bank_doc1_p1_0",
    )
    assert result.chunk_id == "bank_doc1_p1_0"
    print("PASS: RecallResult has chunk_id field")


def main():
    tests = [
        test_message_input_exists,
        test_retain_item_messages_field,
        test_retain_item_content_still_works,
        test_retain_item_rejects_empty,
        test_retain_item_rejects_empty_messages,
        test_build_retain_payload_from_messages,
        test_build_retain_payload_from_content,
        test_retain_content_accepts_messages,
        test_retain_content_messages_none_when_absent,
        test_recall_result_has_chunk_id,
    ]
    passed = 0
    for test in tests:
        try:
            result = test()
            if result is False:
                print(f"  FAILED: {test.__name__}")
        except Exception as exc:
            print(f"  ERROR: {test.__name__} -> {exc}")
        else:
            passed += 1

    total = len(tests)
    print(f"\n{passed}/{total} PASS")
    return passed == total


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)