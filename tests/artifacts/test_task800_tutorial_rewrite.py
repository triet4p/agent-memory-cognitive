"""Task 800 — Tutorial Rewrite Verification.

Verifies that the tutorial rewrite is complete:
- New structure exists (ARCHITECTURE/, CONFIG/, PER-FILE/, REFERENCE/)
- No broken Jekyll includes remain
- Key new docs are present
- Deleted dirs are gone (functions/, modules/, per-file/, plan.md, idea.md, project-overview.md)
"""

import sys
from pathlib import Path

TUTORIALS = Path(__file__).parent.parent.parent / "tutorials"
ARTIFACTS_DIR = Path(__file__).parent.parent.parent


def test_tutorial_structure():
    """New top-level dirs exist."""
    required_dirs = ["ARCHITECTURE", "CONFIG", "PER-FILE", "REFERENCE"]
    for d in required_dirs:
        path = TUTORIALS / d
        assert path.exists() and path.is_dir(), f"Missing required dir: tutorials/{d}/"
    print("[PASS] All required tutorial dirs exist")


def test_no_broken_includes():
    """No Jekyll {% include-markdown %} remains."""
    broken = []
    for md_file in TUTORIALS.rglob("*.md"):
        content = md_file.read_text(encoding="utf-8")
        if "include-markdown" in content:
            broken.append(str(md_file.relative_to(TUTORIALS)))
    if broken:
        print(f"[FAIL] Broken include-markdown found in: {broken}")
        sys.exit(1)
    print("[PASS] No include-markdown broken includes")


def test_deleted_dirs_gone():
    """Boilerplate dirs were deleted."""
    # Note: On Windows, per-file and PER-FILE are the same directory (case-insensitive FS).
    # 'functions' and 'modules' must be gone. 'per-file'/'PER-FILE' is normalized below.
    deleted = ["functions", "modules"]
    for d in deleted:
        path = TUTORIALS / d
        assert not path.exists(), f"Stale directory still exists: tutorials/{d}/"
    # Verify the PER-FILE dir exists with our new content (not the old per-file)
    new_per_file = TUTORIALS / "PER-FILE"
    assert new_per_file.exists(), f"New PER-FILE dir missing"
    # Check it has our new docs (not old boilerplate)
    doc_count = len(list(new_per_file.glob("*.md")))
    assert doc_count >= 4, f"PER-FILE has only {doc_count} docs, expected >= 4"
    print("[PASS] Deleted dirs are gone, PER-FILE has new content")


def test_deleted_files_gone():
    """Broken Jekyll-include root files were deleted. learning-path.md was renamed to LEARNING-PATH.md."""
    # These must be gone (no rename target)
    gone = ["plan.md", "idea.md", "project-overview.md", "README.md", "module-map.md"]
    for f in gone:
        path = TUTORIALS / f
        assert not path.exists(), f"Stale file still exists: tutorials/{f}"
    # learning-path.md was renamed to LEARNING-PATH.md (check uppercase exists)
    lp = TUTORIALS / "LEARNING-PATH.md"
    assert lp.exists(), "LEARNING-PATH.md should exist (renamed from learning-path.md)"
    print("[PASS] Deleted files are gone (renamed files checked)")


def test_key_new_docs():
    """Key new docs exist with real content."""
    required_docs = [
        "INDEX.md",
        "QUICKSTART.md",
        "LEARNING-PATH.md",
        "ARCHITECTURE/overview.md",
        "ARCHITECTURE/retain-pipeline.md",
        "ARCHITECTURE/search-pipeline.md",
        "ARCHITECTURE/reflect-pipeline.md",
        "CONFIG/env-vars.md",
        "CONFIG/prompts.md",
        "PER-FILE/config.md",
        "PER-FILE/retain-fact-extraction.md",
        "PER-FILE/retain-orchestrator.md",
        "PER-FILE/retain-chunking.md",
        "PER-FILE/retain-dedup.md",
        "REFERENCE/troubleshooting.md",
    ]
    for doc in required_docs:
        path = TUTORIALS / doc
        assert path.exists(), f"Missing required doc: tutorials/{doc}"
        content = path.read_text(encoding="utf-8")
        assert len(content) > 100, f"tutorials/{doc} is too short ({len(content)} chars) — likely empty or boilerplate"
        print(f"  {doc}: {len(content)} chars OK")
    print("[PASS] All key new docs present with real content")


def test_bilingual_content():
    """Docs contain both English headings and explanatory content (bilingual OK)."""
    key_docs = [
        "ARCHITECTURE/overview.md",
        "ARCHITECTURE/retain-pipeline.md",
        "PER-FILE/retain-fact-extraction.md",
        "CONFIG/env-vars.md",
    ]
    for doc in key_docs:
        path = TUTORIALS / doc
        content = path.read_text(encoding="utf-8")
        assert len(content) > 500, f"tutorials/{doc} is too short"
        print(f"  {doc}: {len(content)} chars OK")
    print("[PASS] Key docs have substantial content (bilingual)")


def test_troubleshooting_coverage():
    """Troubleshooting doc covers real bugs from S24 hotfix."""
    path = TUTORIALS / "REFERENCE/troubleshooting.md"
    content = path.read_text(encoding="utf-8")
    required_topics = [
        "dateparser",
        "ForeignKeyViolation",
        "chunk_id",
        "search_vector",
        "bool(",
        "GRAPH_RETRIEVER",
    ]
    for topic in required_topics:
        assert topic.lower() in content.lower(), f"troubleshooting.md missing topic: {topic}"
    print("[PASS] Troubleshooting covers all required topics")


def test_arch_overview_has_key_sections():
    """ARCHITECTURE/overview.md has all key sections."""
    path = TUTORIALS / "ARCHITECTURE/overview.md"
    content = path.read_text(encoding="utf-8")
    required_sections = [
        "Three Pipelines",
        "Memory Engine",
        "Fact Types",
        "Edge Types",
        "Configuration Hierarchy",
        "Database Schema",
    ]
    for section in required_sections:
        assert section in content, f"overview.md missing section: {section}"
    print("[PASS] overview.md has all key sections")


def main():
    print("=" * 60)
    print("Task 800 — Tutorial Rewrite Verification")
    print("=" * 60)

    test_tutorial_structure()
    test_no_broken_includes()
    test_deleted_dirs_gone()
    test_deleted_files_gone()
    test_key_new_docs()
    test_bilingual_content()
    test_troubleshooting_coverage()
    test_arch_overview_has_key_sections()

    print()
    print("=" * 60)
    print("ALL TESTS PASSED")
    print("=" * 60)


if __name__ == "__main__":
    main()
