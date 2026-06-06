from __future__ import annotations

import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from cogmem_api.engine.search.graph_retrieval import BFSGraphRetriever
from cogmem_api.engine.search.retrieval import make_graph_retriever
from scripts.eval_cogmem import ABLATION_PROFILES, build_recall_payload


def test_bfs_sum_and_max_reducers_are_distinct() -> None:
    sum_retriever = BFSGraphRetriever(activation_saturation=10.0)
    max_retriever = BFSGraphRetriever(activation_saturation=10.0, activation_reducer="max")

    assert sum_retriever.name == "bfs"
    assert max_retriever.name == "bfs_max"
    assert sum_retriever._merge_activation(0.4, 0.5) == 0.9
    assert max_retriever._merge_activation(0.4, 0.5) == 0.5


def test_sum_reducer_still_respects_saturation() -> None:
    retriever = BFSGraphRetriever(activation_saturation=0.7)
    assert retriever._merge_activation(0.4, 0.5) == 0.7


def test_make_graph_retriever_supports_bfs_max_override() -> None:
    assert make_graph_retriever("bfs").name == "bfs"
    assert make_graph_retriever("bfs_max").name == "bfs_max"


def test_graph_only_sum_and_max_profiles_are_apples_to_apples() -> None:
    sum_payload = build_recall_payload(ABLATION_PROFILES["E7G"], "Who connected the evidence?")
    max_payload = build_recall_payload(ABLATION_PROFILES["E7GM"], "Who connected the evidence?")

    comparable_keys = {
        "types",
        "budget",
        "max_tokens",
        "top_k",
        "snippet_budget",
        "trace",
        "adaptive_router",
        "skip_reranker",
        "graph_only",
    }
    for key in comparable_keys:
        assert sum_payload[key] == max_payload[key], f"SUM/MAX graph-only payload differs on {key}"

    assert sum_payload["graph_retriever"] == "bfs"
    assert max_payload["graph_retriever"] == "bfs_max"
    assert sum_payload["graph_only"] is True
    assert max_payload["graph_only"] is True
    assert sum_payload["skip_reranker"] is True
    assert max_payload["skip_reranker"] is True


if __name__ == "__main__":
    test_bfs_sum_and_max_reducers_are_distinct()
    test_sum_reducer_still_respects_saturation()
    test_make_graph_retriever_supports_bfs_max_override()
    test_graph_only_sum_and_max_profiles_are_apples_to_apples()
    print("task_s36_sum_vs_max_graph_only artifact checks passed")
