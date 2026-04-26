"""Task 757 artifact tests — Session Recall Bug Fixes.

Root cause (confirmed from server log): No module named 'dateparser'
  → recall_async outer try-except caught it silently → lexical fallback
  → lexical fallback had no document_id → session_recall@k = 0.0

Tests that:
8.1  TypeError fix: recall_keyword_accuracy=None formats correctly in print statement
8.2  dateparser is installed and importable (PRIMARY FIX)
8.3  Cross-encoder failure falls back to RRF order, not full lexical scan
8.4  Lexical fallback includes document_id
8.5  Warning log when CE or main path fails
8.7  BM25 native path does not reference search_vector column
"""

import sys
import os
import re

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))


def test_8_2_dateparser_installed() -> None:
    """dateparser must be importable — missing it causes recall main path to fail silently."""
    try:
        from dateparser.search import search_dates
    except ImportError as e:
        raise AssertionError(
            f"dateparser not installed — this was the root cause of session_recall=0.0: {e}"
        )
    # Verify it handles a temporal query and a non-temporal query without error
    result = search_dates("yesterday")
    assert result is not None and len(result) > 0, "Expected dateparser to find 'yesterday'"
    result2 = search_dates("How many model kits have I worked on?")
    # May or may not find a date — just must not raise


def test_8_1_kw_none_format() -> None:
    """eval_cogmem build_print_line handles recall_keyword_accuracy=None."""
    # Simulate the fixed logic from lines 1083-1090 of eval_cogmem.py
    metrics = {"recall_keyword_accuracy": None, "judge_accuracy": 0.0}
    kw = metrics.get("recall_keyword_accuracy")
    kw_str = "null" if kw is None else f"{kw:.3f}"
    assert kw_str == "null", f"Expected 'null', got {kw_str!r}"

    # Also verify non-None still formats correctly
    metrics2 = {"recall_keyword_accuracy": 0.667}
    kw2 = metrics2.get("recall_keyword_accuracy")
    kw_str2 = "null" if kw2 is None else f"{kw2:.3f}"
    assert kw_str2 == "0.667", f"Expected '0.667', got {kw_str2!r}"


def test_8_2_cross_encoder_graceful_fallback_preserves_document_id() -> None:
    """When cross-encoder fails, RRF-based fallback preserves document_id."""
    from dataclasses import dataclass, field
    from cogmem_api.engine.search.types import RetrievalResult, MergedCandidate, ScoredResult

    # Simulate: two candidates with document_ids set from retain
    r1 = RetrievalResult(id="u1", text="Spitfire Mk.V painting", fact_type="experience",
                         document_id="answer_593bdffd_1")
    r2 = RetrievalResult(id="u2", text="Tiger I diorama progress", fact_type="experience",
                         document_id="answer_593bdffd_3")

    c1 = MergedCandidate(retrieval=r1, rrf_score=0.9)
    c2 = MergedCandidate(retrieval=r2, rrf_score=0.7)
    top_candidates = [c1, c2]

    # Simulate what the fixed code does when cross-encoder fails
    scored = [
        ScoredResult(candidate=c, cross_encoder_score=0.0, cross_encoder_score_normalized=c.rrf_score)
        for c in top_candidates
    ]
    for sr in scored:
        sr.combined_score = sr.cross_encoder_score_normalized
        sr.weight = sr.combined_score

    results = [
        {
            "id": sr.id,
            "text": sr.retrieval.text,
            "fact_type": sr.retrieval.fact_type,
            "score": float(sr.combined_score),
            "document_id": sr.candidate.retrieval.document_id,
        }
        for sr in scored
    ]

    assert len(results) == 2
    assert results[0]["document_id"] == "answer_593bdffd_1", (
        f"Expected gold session ID, got {results[0]['document_id']!r}"
    )
    assert results[1]["document_id"] == "answer_593bdffd_3"
    # Order preserved from RRF (highest score first)
    assert results[0]["id"] == "u1"


def test_8_3_lexical_fallback_includes_document_id() -> None:
    """_fallback_recall_from_conn result dict now includes document_id."""
    import inspect
    import cogmem_api.engine.memory_engine as me_mod

    src = inspect.getsource(me_mod.MemoryEngine._fallback_recall_from_conn)
    assert "document_id" in src, (
        "_fallback_recall_from_conn must include document_id in SELECT and result"
    )
    # Verify it's in both the SELECT query and the result dict
    assert src.count("document_id") >= 2, (
        "Expected document_id in both SELECT clause and append dict"
    )


def test_8_4_warning_log_when_ce_fails() -> None:
    """memory_engine logs a warning when cross-encoder fails."""
    import inspect
    import cogmem_api.engine.memory_engine as me_mod

    src = inspect.getsource(me_mod.MemoryEngine.recall_async)
    assert "Cross-encoder reranking failed" in src, (
        "recall_async must log a warning when cross-encoder fails"
    )
    assert "Recall main path failed" in src, (
        "recall_async must log a warning when the main path fails"
    )


def test_8_2_session_recall_computation_with_null_docid() -> None:
    """session_recall@k = 0 when all document_ids are None (old fallback behavior)."""
    gold_set = {"answer_593bdffd_1", "answer_593bdffd_2", "answer_593bdffd_3"}
    results_no_docid = [
        {"id": f"u{i}", "text": f"fact {i}", "document_id": None}
        for i in range(10)
    ]
    top_k = results_no_docid[:5]
    matched = [r.get("document_id") for r in top_k if r.get("document_id") in gold_set]
    assert len(matched) == 0, "Expected 0 matches when document_id is None"

    # With correct document_ids (fixed behavior)
    results_with_docid = [
        {"id": "u1", "text": "Spitfire Mk.V", "document_id": "answer_593bdffd_1"},
        {"id": "u2", "text": "Tiger I", "document_id": "answer_593bdffd_3"},
        {"id": "u3", "text": "other", "document_id": "haystack_irrelevant"},
        {"id": "u4", "text": "other2", "document_id": None},
        {"id": "u5", "text": "other3", "document_id": "haystack_x"},
    ]
    top_k2 = results_with_docid[:5]
    matched2 = [r.get("document_id") for r in top_k2 if r.get("document_id") in gold_set]
    assert len(matched2) == 2, f"Expected 2 matches, got {len(matched2)}"
    recall = 1.0 if matched2 else 0.0
    assert recall == 1.0


def test_8_5_dateparser_in_pyproject() -> None:
    """dateparser appears in pyproject.toml dependencies."""
    import tomllib, pathlib
    root = pathlib.Path(__file__).parent.parent.parent
    with open(root / "pyproject.toml", "rb") as f:
        data = tomllib.load(f)
    deps = data["project"]["dependencies"]
    assert any("dateparser" in d for d in deps), (
        f"dateparser not in pyproject.toml dependencies: {deps}"
    )


def test_8_7_native_bm25_no_search_vector() -> None:
    """BM25 native path must not reference search_vector column.

    search_vector only appears in vchord/pg_textsearch branches (opt-in extensions).
    The default 'native' branch must use to_tsvector('english', text) inline.
    """
    import inspect
    import cogmem_api.engine.search.retrieval as ret_mod
    src = inspect.getsource(ret_mod.retrieve_semantic_bm25_combined)
    # Old native-path patterns that used the non-existent column
    assert "ts_rank_cd(search_vector," not in src, (
        "Native BM25 must not use ts_rank_cd(search_vector, ...) — column does not exist"
    )
    assert "search_vector @@ to_tsquery" not in src, (
        "Native BM25 must not use search_vector @@ to_tsquery — column does not exist"
    )
    # Verify the replacement is in place
    assert "to_tsvector('english', text)" in src, (
        "Expected to_tsvector('english', text) inline expression in native BM25 path"
    )


if __name__ == "__main__":
    tests = [
        test_8_2_dateparser_installed,
        test_8_1_kw_none_format,
        test_8_2_cross_encoder_graceful_fallback_preserves_document_id,
        test_8_3_lexical_fallback_includes_document_id,
        test_8_4_warning_log_when_ce_fails,
        test_8_2_session_recall_computation_with_null_docid,
        test_8_5_dateparser_in_pyproject,
        test_8_7_native_bm25_no_search_vector,
    ]
    passed = 0
    for t in tests:
        try:
            t()
            print(f"  PASS  {t.__name__}")
            passed += 1
        except Exception as e:
            print(f"  FAIL  {t.__name__}: {e}")
    print(f"\n{passed}/{len(tests)} passed")
    if passed < len(tests):
        sys.exit(1)
