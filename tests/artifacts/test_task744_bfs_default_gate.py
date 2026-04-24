"""Task 744: S20.2 — Set BFS SUM as default graph retriever.

Verifies:
- DEFAULT_GRAPH_RETRIEVER in config.py is "bfs"
- .env COGMEM_API_GRAPH_RETRIEVER is set to "bfs"
- get_default_graph_retriever() returns BFSGraphRetriever when no override
"""

from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from cogmem_api.config import DEFAULT_GRAPH_RETRIEVER, get_config
from cogmem_api.engine.search import get_default_graph_retriever, BFSGraphRetriever


def test_default_graph_retriever_is_bfs():
    result = get_default_graph_retriever()
    assert isinstance(result, BFSGraphRetriever), (
        f"Expected BFSGraphRetriever but got {type(result).__name__}"
    )


def test_default_constant_is_bfs():
    assert DEFAULT_GRAPH_RETRIEVER == "bfs", (
        f"DEFAULT_GRAPH_RETRIEVER should be 'bfs', got '{DEFAULT_GRAPH_RETRIEVER}'"
    )


def test_env_file_graph_retriever_is_bfs():
    env_path = REPO_ROOT / ".env"
    if env_path.exists():
        text = env_path.read_text(encoding="utf-8")
        for line in text.splitlines():
            if line.startswith("COGMEM_API_GRAPH_RETRIEVER="):
                value = line.split("=", 1)[1].strip().strip('"')
                assert value == "bfs", (
                    f".env COGMEM_API_GRAPH_RETRIEVER should be 'bfs', got '{value}'"
                )
                return
    assert False, "COGMEM_API_GRAPH_RETRIEVER not found in .env"


def main() -> None:
    test_default_graph_retriever_is_bfs()
    test_default_constant_is_bfs()
    test_env_file_graph_retriever_is_bfs()
    print("Task 744 BFS default gate passed.")


if __name__ == "__main__":
    main()
