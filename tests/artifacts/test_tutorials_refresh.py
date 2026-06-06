"""Artifact test: tutorials reflect the current code state (S35 refresh).

Standalone script (no pytest). Run:
    uv run python tests/artifacts/test_tutorials_refresh.py

Guards against the specific staleness this refresh fixed:
 - search pipeline must use the 6 real query types (incl. `preference`, NOT `entity`)
 - graph retriever options must include `bfs_max`
 - the two new ARCHITECTURE pages exist and are wired into mkdocs nav
 - retain pipeline documents Phase A / Phase B + Pass 3
"""

from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
TUT = REPO_ROOT / "tutorials"

if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))


def _read(rel: str) -> str:
    path = REPO_ROOT / rel
    assert path.exists(), f"Missing expected file: {rel}"
    return path.read_text(encoding="utf-8")


def assert_code_ground_truth() -> None:
    """The facts the docs now assert must still hold in code."""
    from cogmem_api.config import ALLOWED_GRAPH_RETRIEVERS
    from cogmem_api.engine.query_analyzer import _ADAPTIVE_RRF_WEIGHTS

    query_types = set(_ADAPTIVE_RRF_WEIGHTS.keys())
    assert query_types == {
        "semantic", "temporal", "causal", "prospective", "preference", "multi_hop"
    }, f"Query types drifted: {query_types}"
    assert "entity" not in query_types, "There is no `entity` query type"
    assert "bfs_max" in ALLOWED_GRAPH_RETRIEVERS, ALLOWED_GRAPH_RETRIEVERS
    assert ALLOWED_GRAPH_RETRIEVERS == {"bfs", "bfs_max", "link_expansion", "mpfp"}


def assert_search_pipeline_doc() -> None:
    text = _read("tutorials/ARCHITECTURE/search-pipeline.md")
    assert "`preference`" in text, "search-pipeline must document the preference query type"
    assert "| `entity` | Named entities" not in text, "stale `entity` query-type row still present"
    assert "bfs_max" in text and "activation_reducer" in text, "SUM/MAX toggle not documented"
    for retriever in ("MPFPGraphRetriever", "LinkExpansionRetriever"):
        assert retriever in text, f"{retriever} not mentioned in search pipeline doc"


def assert_retain_pipeline_doc() -> None:
    text = _read("tutorials/ARCHITECTURE/retain-pipeline.md")
    assert "Phase A" in text and "Phase B" in text, "retain doc must cover Phase A / Phase B links"
    assert "Pass 3" in text, "retain doc must cover Pass 3"
    assert "enabled_fact_types" in text and "agentic_transcript" in text
    assert "≥ **0.6**" in text or "≥ 0.6" in text, "in-session semantic threshold should be 0.6"


def assert_new_pages_and_nav() -> None:
    bench = _read("tutorials/ARCHITECTURE/benchmark-ablation.md")
    assert "cogmem_bench" in bench and "enabled_fact_types" in bench
    evald = _read("tutorials/ARCHITECTURE/evaluation.md")
    assert "cogmem-verify" in evald and "cogmem-diagnose" in evald and "cogmem-audit" in evald

    nav = _read("mkdocs.yml")
    assert "ARCHITECTURE/benchmark-ablation.md" in nav, "benchmark page not in mkdocs nav"
    assert "ARCHITECTURE/evaluation.md" in nav, "evaluation page not in mkdocs nav"


def assert_index_trimmed() -> None:
    index = _read("tutorials/INDEX.md")
    # Old over-promised PER-FILE entries that do not exist must be gone.
    for ghost in ("PER-FILE/api-http.md", "PER-FILE/engine-core.md", "REFERENCE/glossary.md"):
        assert ghost not in index, f"INDEX still promises non-existent doc: {ghost}"
    assert "benchmark-ablation.md" in index and "evaluation.md" in index


def main() -> None:
    assert_code_ground_truth()
    assert_search_pipeline_doc()
    assert_retain_pipeline_doc()
    assert_new_pages_and_nav()
    assert_index_trimmed()
    print("tutorials refresh checks passed (search/retain accuracy + new pages + trimmed index).")


if __name__ == "__main__":
    main()
