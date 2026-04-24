"""Task 753: S23.1 — Session-Level Recall@k Implementation.

Verifies:
- _build_session_recall_at_k() returns None when gold_session_ids is None/empty
- Recall@k = 1 when top-k contains at least 1 document_id in gold_session_ids
- Recall@k = 0 when top-k has no document_id from gold_session_ids
- Precision@k = (# matched docs in top-k) / k
- LongMemEval fixture loader extracts answer_session_ids into gold_session_ids
- LoCoMo fixture loader extracts evidence D{doc}:{turn} into gold_session_ids
- document_id included in recall results from memory_engine (via API model)
"""

from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.eval_cogmem import _build_session_recall_at_k, _build_recall_at_k, get_fixture


def test_none_gold_session_ids_returns_none():
    results = [{"id": "1", "text": "doc one", "document_id": "D1"}]
    assert _build_session_recall_at_k(results, None, k=5)["recall_at_k"] is None
    assert _build_session_recall_at_k(results, [], k=5)["recall_at_k"] is None


def test_recall_at_k_1_when_match_in_top_5():
    results = [
        {"id": "1", "text": "doc one", "document_id": "D99"},
        {"id": "2", "text": "doc two", "document_id": "D1"},
        {"id": "3", "text": "doc three", "document_id": "D3"},
    ]
    result = _build_session_recall_at_k(results, ["D1", "D2"], k=5)
    assert result["recall_at_k"] == 1.0
    assert result["matched_session_count"] == 1
    assert result["total_gold_sessions"] == 2


def test_recall_at_k_0_when_no_match():
    results = [
        {"id": "1", "text": "doc one", "document_id": "D99"},
        {"id": "2", "text": "doc two", "document_id": "D98"},
        {"id": "3", "text": "doc three", "document_id": "D97"},
    ]
    result = _build_session_recall_at_k(results, ["D1", "D2"], k=5)
    assert result["recall_at_k"] == 0.0
    assert result["matched_session_count"] == 0


def test_recall_at_k_respects_k():
    results = [
        {"id": "1", "text": "doc one", "document_id": "D1"},
        {"id": "2", "text": "doc two", "document_id": "D1"},
        {"id": "3", "text": "doc three", "document_id": "D1"},
    ]
    result = _build_session_recall_at_k(results, ["D1"], k=1)
    assert result["recall_at_k"] == 1.0
    assert result["precision_at_k"] == 1.0 / 1.0


def test_precision_at_k():
    results = [
        {"id": "1", "text": "doc one", "document_id": "D1"},
        {"id": "2", "text": "doc two", "document_id": "D2"},
        {"id": "3", "text": "doc three", "document_id": "D3"},
    ]
    result = _build_session_recall_at_k(results, ["D1", "D5"], k=3)
    assert result["recall_at_k"] == 1.0
    assert result["precision_at_k"] == 1.0 / 3.0
    assert result["matched_session_count"] == 1


def test_missing_document_id_in_result_handled():
    results = [
        {"id": "1", "text": "doc one"},
        {"id": "2", "text": "doc two", "document_id": "D1"},
    ]
    result = _build_session_recall_at_k(results, ["D1"], k=2)
    assert result["recall_at_k"] == 1.0


def test_longmemeval_fixture_has_gold_session_ids():
    fixture = get_fixture("longmemeval")
    found_with_sessions = 0
    for q in fixture["questions"]:
        assert "gold_session_ids" in q, f"question {q['id']} missing gold_session_ids"
        if q["gold_session_ids"]:
            found_with_sessions += 1
    assert found_with_sessions > 0, "Expected at least some questions to have gold_session_ids"


def test_locomo_fixture_has_gold_session_ids():
    fixture = get_fixture("locomo")
    found_with_sessions = 0
    for q in fixture["questions"]:
        assert "gold_session_ids" in q, f"question {q['id']} missing gold_session_ids"
        if q["gold_session_ids"]:
            found_with_sessions += 1
    assert found_with_sessions > 0, "Expected at least some questions to have gold_session_ids"


def test_locomo_evidence_doc_id_extraction():
    fixture = get_fixture("locomo")
    for q in fixture["questions"]:
        if not q["gold_session_ids"]:
            continue
        for sid in q["gold_session_ids"]:
            assert sid.startswith("D"), f"Expected D-prefixed doc ID, got: {sid}"


def test_keyword_recall_still_works():
    results = [
        {"id": "1", "text": "Alice drinks coffee every morning"},
        {"id": "2", "text": "Bob prefers tea"},
    ]
    gold_kw = ["coffee", "morning"]
    result = _build_recall_at_k(results, gold_kw, k=5)
    assert result["recall_at_k"] == 1.0
    assert result["recalled_keywords"] == 2
    assert result["total_gold_keywords"] == 2


def test_short_fixture_no_gold_session_ids():
    from scripts.eval_cogmem import SHORT_DIALOGUE_FIXTURE
    for q in SHORT_DIALOGUE_FIXTURE["questions"]:
        assert "gold_session_ids" not in q or q.get("gold_session_ids") is None, \
            "SHORT fixture should not have gold_session_ids"


def test_longmemeval_fixture_sessions_has_document_ids():
    fixture = get_fixture("longmemeval")
    for q in fixture["questions"]:
        sessions = q.get("_sessions")
        assert sessions is not None, f"question {q['id']} missing _sessions"
        assert len(sessions) > 0, f"question {q['id']} has empty _sessions"
        for session_id, turns in sessions:
            assert isinstance(turns, list), f"turns should be list for {session_id}"
            assert len(turns) > 0, f"empty turns for {session_id}"
        # Gold session IDs must be findable in _sessions (cross-match)
        session_ids_set = {sid for sid, _ in sessions}
        for gid in q.get("gold_session_ids", []):
            assert gid in session_ids_set, (
                f"gold session '{gid}' not found in _sessions {list(session_ids_set)[:5]}"
            )


def test_locomo_fixture_sessions_has_d_prefix():
    fixture = get_fixture("locomo")
    for q in fixture["questions"]:
        sessions = q.get("_sessions")
        assert sessions is not None, f"question {q['id']} missing _sessions"
        assert len(sessions) > 0, f"question {q['id']} has empty _sessions"
        for session_id, turns in sessions:
            assert session_id.startswith("D"), f"expected D-prefixed id, got: {session_id}"
            assert isinstance(turns, list), f"turns should be list for {session_id}"


def test_retain_fixture_builds_items_with_document_id():
    from scripts.eval_cogmem import get_fixture, retain_fixture
    fixture = get_fixture("longmemeval")
    captured_payload = {}
    def fake_post(url, payload, timeout):
        captured_payload.update(payload)
        return {"status": "ok"}
    retain_fixture("http://localhost:8888", "test-bank", fixture, post_json_fn=fake_post, timeout_seconds=30.0)
    items = captured_payload.get("items", [])
    assert len(items) > 0, "expected items in payload"
    has_doc_id = any("document_id" in item and item["document_id"] for item in items)
    assert has_doc_id, "expected at least some items to have document_id"
    has_content = all("content" in item and item["content"] for item in items)
    assert has_content, "all items should have content"


def test_retain_fixture_short_no_document_id():
    from scripts.eval_cogmem import SHORT_DIALOGUE_FIXTURE, retain_fixture
    captured_payload = {}
    def fake_post(url, payload, timeout):
        captured_payload.update(payload)
        return {"status": "ok"}
    retain_fixture("http://localhost:8888", "test-bank", SHORT_DIALOGUE_FIXTURE, post_json_fn=fake_post, timeout_seconds=30.0)
    items = captured_payload.get("items", [])
    assert len(items) > 0
    has_doc_id = any("document_id" in item and item["document_id"] for item in items)
    assert not has_doc_id, "SHORT fixture should not have document_id"


if __name__ == "__main__":
    print("Task 753 session-level Recall@k tests")
    test_none_gold_session_ids_returns_none()
    print("  test_none_gold_session_ids_returns_none PASSED")
    test_recall_at_k_1_when_match_in_top_5()
    print("  test_recall_at_k_1_when_match_in_top_5 PASSED")
    test_recall_at_k_0_when_no_match()
    print("  test_recall_at_k_0_when_no_match PASSED")
    test_recall_at_k_respects_k()
    print("  test_recall_at_k_respects_k PASSED")
    test_precision_at_k()
    print("  test_precision_at_k PASSED")
    test_missing_document_id_in_result_handled()
    print("  test_missing_document_id_in_result_handled PASSED")
    test_longmemeval_fixture_has_gold_session_ids()
    print("  test_longmemeval_fixture_has_gold_session_ids PASSED")
    test_locomo_fixture_has_gold_session_ids()
    print("  test_locomo_fixture_has_gold_session_ids PASSED")
    test_locomo_evidence_doc_id_extraction()
    print("  test_locomo_evidence_doc_id_extraction PASSED")
    test_keyword_recall_still_works()
    print("  test_keyword_recall_still_works PASSED")
    test_short_fixture_no_gold_session_ids()
    print("  test_short_fixture_no_gold_session_ids PASSED")
    test_longmemeval_fixture_sessions_has_document_ids()
    print("  test_longmemeval_fixture_sessions_has_document_ids PASSED")
    test_locomo_fixture_sessions_has_d_prefix()
    print("  test_locomo_fixture_sessions_has_d_prefix PASSED")
    test_retain_fixture_builds_items_with_document_id()
    print("  test_retain_fixture_builds_items_with_document_id PASSED")
    test_retain_fixture_short_no_document_id()
    print("  test_retain_fixture_short_no_document_id PASSED")
    print("Task 753 session-level Recall@k passed.")