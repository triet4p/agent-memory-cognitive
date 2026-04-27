"""Artifact test for task 764: Two-tier recall (top_k + snippet_budget)."""

if __name__ == "__main__":
    import sys
    sys.path.insert(0, str(__file__).rsplit("/", 2)[0])

    from tests.artifacts.test_task764_recall_top_k import main
    main()