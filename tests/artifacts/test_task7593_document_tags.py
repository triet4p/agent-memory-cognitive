"""Task 759.3 artifact tests: document_tags wired through fact_storage INSERT.

Verification that document_tags parameter is added to insert_facts_batch
and passed through from orchestrator.
"""

from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))


def test_insert_facts_batch_accepts_document_tags() -> None:
    """insert_facts_batch accepts document_tags parameter."""
    from cogmem_api.engine.retain import fact_storage
    import inspect

    sig = inspect.signature(fact_storage.insert_facts_batch)
    params = list(sig.parameters.keys())
    assert "document_tags" in params, \
        f"document_tags not in insert_facts_batch signature: {params}"

    print("PASS: test_insert_facts_batch_accepts_document_tags")


def test_orchestrator_passes_document_tags() -> None:
    """orchestrator.retain_batch passes document_tags to insert_facts_batch."""
    from cogmem_api.engine.retain import orchestrator
    import inspect

    sig = inspect.signature(orchestrator.retain_batch)
    params = list(sig.parameters.keys())
    assert "document_tags" in params, \
        f"document_tags not in retain_batch signature: {params}"

    source = open(orchestrator.__file__, encoding="utf-8").read()
    assert "document_tags=document_tags" in source, \
        "document_tags not passed through to insert_facts_batch in orchestrator"

    print("PASS: test_orchestrator_passes_document_tags")


def _main() -> None:
    tests = [
        test_insert_facts_batch_accepts_document_tags,
        test_orchestrator_passes_document_tags,
    ]
    passed = 0
    failed = 0
    for test in tests:
        try:
            test()
            passed += 1
        except Exception as exc:
            print(f"FAIL: {test.__name__}: {exc}")
            failed += 1
    print(f"\nResults: {passed}/2 passed")
    if failed:
        print(f"FAILED: {failed} test(s)")
        sys.exit(1)
    print("ALL TESTS PASSED")


if __name__ == "__main__":
    _main()
