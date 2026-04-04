from __future__ import annotations

import importlib
import os
import sys
from pathlib import Path


def _required_files(repo_root: Path) -> list[Path]:
    return [
        repo_root / "cogmem_api" / "config.py",
        repo_root / ".env.example",
        repo_root / "logs" / "task_611_summary.md",
        repo_root / "tests" / "artifacts" / "test_task611_config_contract.py",
    ]


def assert_required_files(repo_root: Path) -> None:
    missing = [str(path.relative_to(repo_root)) for path in _required_files(repo_root) if not path.exists()]
    assert not missing, f"Missing B1 artifacts/files: {missing}"


def assert_isolation(repo_root: Path) -> None:
    scope = [
        repo_root / "cogmem_api" / "config.py",
        repo_root / ".env.example",
    ]

    violations: list[str] = []
    for file_path in scope:
        text = file_path.read_text(encoding="utf-8")
        if "from hindsight_api" in text or "import hindsight_api" in text:
            violations.append(str(file_path.relative_to(repo_root)))

    assert not violations, f"Isolation violation: {violations}"


def assert_env_contract_documented(repo_root: Path) -> None:
    env_example = (repo_root / ".env.example").read_text(encoding="utf-8")
    expected_envs = [
        "COGMEM_API_LLM_BASE_URL",
        "COGMEM_API_LLM_TIMEOUT",
        "COGMEM_API_RETAIN_LLM_TIMEOUT",
        "COGMEM_API_REFLECT_LLM_TIMEOUT",
        "COGMEM_API_RETAIN_MAX_COMPLETION_TOKENS",
        "COGMEM_API_RETAIN_CHUNK_SIZE",
        "COGMEM_API_RETAIN_EXTRACT_CAUSAL_LINKS",
        "COGMEM_API_RETAIN_EXTRACTION_MODE",
        "COGMEM_API_RETAIN_MISSION",
        "COGMEM_API_RETAIN_CUSTOM_INSTRUCTIONS",
        "COGMEM_API_EMBEDDINGS_PROVIDER",
        "COGMEM_API_EMBEDDINGS_OPENAI_MODEL",
        "COGMEM_API_RERANKER_PROVIDER",
        "COGMEM_API_RERANKER_LOCAL_MODEL",
        "COGMEM_API_RERANKER_MAX_CANDIDATES",
        "COGMEM_API_RECALL_MAX_CONCURRENT",
    ]

    missing = [name for name in expected_envs if name not in env_example]
    assert not missing, f"Missing env contract in .env.example: {missing}"


def _restore_env(backup: dict[str, str | None]) -> None:
    for key, value in backup.items():
        if value is None:
            os.environ.pop(key, None)
        else:
            os.environ[key] = value


def run_behavioral_matrix() -> None:
    import cogmem_api.config as config_module

    env_keys = [
        "COGMEM_API_DATABASE_URL",
        "COGMEM_API_DATABASE_SCHEMA",
        "COGMEM_API_HOST",
        "COGMEM_API_PORT",
        "COGMEM_API_LOG_LEVEL",
        "COGMEM_API_WORKERS",
        "COGMEM_API_LLM_PROVIDER",
        "COGMEM_API_LLM_MODEL",
        "COGMEM_API_LLM_API_KEY",
        "COGMEM_API_LLM_BASE_URL",
        "COGMEM_API_LLM_TIMEOUT",
        "COGMEM_API_RETAIN_LLM_TIMEOUT",
        "COGMEM_API_REFLECT_LLM_TIMEOUT",
        "COGMEM_API_RETAIN_MAX_COMPLETION_TOKENS",
        "COGMEM_API_RETAIN_CHUNK_SIZE",
        "COGMEM_API_RETAIN_EXTRACT_CAUSAL_LINKS",
        "COGMEM_API_RETAIN_EXTRACTION_MODE",
        "COGMEM_API_RETAIN_MISSION",
        "COGMEM_API_RETAIN_CUSTOM_INSTRUCTIONS",
        "COGMEM_API_RECALL_MAX_CONCURRENT",
        "COGMEM_API_DB_POOL_MIN_SIZE",
        "COGMEM_API_DB_POOL_MAX_SIZE",
        "COGMEM_API_GRAPH_RETRIEVER",
        "COGMEM_API_TEXT_SEARCH_EXTENSION",
        "COGMEM_API_MPFP_TOP_K_NEIGHBORS",
        "COGMEM_API_BFS_REFRACTORY_STEPS",
        "COGMEM_API_BFS_FIRING_QUOTA",
        "COGMEM_API_BFS_ACTIVATION_SATURATION",
        "COGMEM_API_EMBEDDINGS_PROVIDER",
        "COGMEM_API_EMBEDDINGS_LOCAL_MODEL",
        "COGMEM_API_EMBEDDINGS_OPENAI_MODEL",
        "COGMEM_API_EMBEDDINGS_OPENAI_BASE_URL",
        "COGMEM_API_EMBEDDINGS_OPENAI_API_KEY",
        "COGMEM_API_RERANKER_PROVIDER",
        "COGMEM_API_RERANKER_LOCAL_MODEL",
        "COGMEM_API_RERANKER_TEI_URL",
        "COGMEM_API_RERANKER_TEI_BATCH_SIZE",
        "COGMEM_API_RERANKER_MAX_CANDIDATES",
    ]
    backup = {key: os.environ.get(key) for key in env_keys}

    try:
        for key in env_keys:
            os.environ.pop(key, None)

        config_module = importlib.reload(config_module)
        runtime = config_module._get_raw_config()
        engine = config_module.get_config()

        assert runtime.llm_base_url is None
        assert runtime.llm_timeout == 120.0
        assert runtime.retain_llm_timeout == 120.0
        assert runtime.reflect_llm_timeout == 120.0
        assert runtime.retain_max_completion_tokens == 64000
        assert runtime.retain_chunk_size == 3000
        assert runtime.retain_extract_causal_links is True
        assert runtime.retain_extraction_mode == "concise"
        assert runtime.retain_mission is None
        assert runtime.retain_custom_instructions is None
        assert runtime.recall_max_concurrent == 32

        assert engine.embeddings_provider == "local"
        assert engine.embeddings_openai_model == "text-embedding-3-small"
        assert engine.reranker_provider == "rrf"
        assert engine.reranker_max_candidates == 300

        os.environ["COGMEM_API_LLM_BASE_URL"] = "http://host.docker.internal:1234/v1"
        os.environ["COGMEM_API_LLM_TIMEOUT"] = "90"
        os.environ["COGMEM_API_RETAIN_LLM_TIMEOUT"] = "150"
        os.environ["COGMEM_API_REFLECT_LLM_TIMEOUT"] = "80"
        os.environ["COGMEM_API_RETAIN_MAX_COMPLETION_TOKENS"] = "12000"
        os.environ["COGMEM_API_RETAIN_CHUNK_SIZE"] = "2500"
        os.environ["COGMEM_API_RETAIN_EXTRACT_CAUSAL_LINKS"] = "false"
        os.environ["COGMEM_API_RETAIN_EXTRACTION_MODE"] = "VERBOSE"
        os.environ["COGMEM_API_RETAIN_MISSION"] = "Keep durable memory"
        os.environ["COGMEM_API_RETAIN_CUSTOM_INSTRUCTIONS"] = "Custom contract"
        os.environ["COGMEM_API_RECALL_MAX_CONCURRENT"] = "8"
        os.environ["COGMEM_API_EMBEDDINGS_PROVIDER"] = "openai"
        os.environ["COGMEM_API_EMBEDDINGS_OPENAI_MODEL"] = "text-embedding-3-large"
        os.environ["COGMEM_API_EMBEDDINGS_OPENAI_BASE_URL"] = "https://api.openai.com/v1"
        os.environ["COGMEM_API_EMBEDDINGS_OPENAI_API_KEY"] = "emb-secret"
        os.environ["COGMEM_API_RERANKER_PROVIDER"] = "cohere"
        os.environ["COGMEM_API_RERANKER_LOCAL_MODEL"] = "cross-encoder/custom-model"
        os.environ["COGMEM_API_RERANKER_TEI_URL"] = "http://tei:8080"
        os.environ["COGMEM_API_RERANKER_TEI_BATCH_SIZE"] = "64"
        os.environ["COGMEM_API_RERANKER_MAX_CANDIDATES"] = "150"

        config_module = importlib.reload(config_module)
        runtime = config_module._get_raw_config()
        engine = config_module.get_config()

        assert runtime.llm_base_url == "http://host.docker.internal:1234/v1"
        assert runtime.llm_timeout == 90.0
        assert runtime.retain_llm_timeout == 150.0
        assert runtime.reflect_llm_timeout == 80.0
        assert runtime.retain_max_completion_tokens == 12000
        assert runtime.retain_chunk_size == 2500
        assert runtime.retain_extract_causal_links is False
        assert runtime.retain_extraction_mode == "verbose"
        assert runtime.retain_mission == "Keep durable memory"
        assert runtime.retain_custom_instructions == "Custom contract"
        assert runtime.recall_max_concurrent == 8

        assert engine.embeddings_provider == "openai"
        assert engine.embeddings_openai_model == "text-embedding-3-large"
        assert engine.embeddings_openai_base_url == "https://api.openai.com/v1"
        assert engine.embeddings_openai_api_key == "emb-secret"
        assert engine.reranker_provider == "cohere"
        assert engine.reranker_local_model == "cross-encoder/custom-model"
        assert engine.reranker_tei_url == "http://tei:8080"
        assert engine.reranker_tei_batch_size == 64
        assert engine.reranker_max_candidates == 150

        # Invalid matrix should gracefully fallback to defaults/minimum guards.
        os.environ["COGMEM_API_LLM_TIMEOUT"] = "not-a-number"
        os.environ["COGMEM_API_RETAIN_LLM_TIMEOUT"] = "-50"
        os.environ["COGMEM_API_REFLECT_LLM_TIMEOUT"] = ""
        os.environ["COGMEM_API_RETAIN_MAX_COMPLETION_TOKENS"] = "0"
        os.environ["COGMEM_API_RETAIN_CHUNK_SIZE"] = "-10"
        os.environ["COGMEM_API_RETAIN_EXTRACT_CAUSAL_LINKS"] = "invalid-bool"
        os.environ["COGMEM_API_RETAIN_EXTRACTION_MODE"] = "invalid-mode"
        os.environ["COGMEM_API_RETAIN_MISSION"] = ""
        os.environ["COGMEM_API_RETAIN_CUSTOM_INSTRUCTIONS"] = ""
        os.environ["COGMEM_API_RECALL_MAX_CONCURRENT"] = "bad"
        os.environ["COGMEM_API_RERANKER_TEI_BATCH_SIZE"] = "not-int"
        os.environ["COGMEM_API_RERANKER_MAX_CANDIDATES"] = "-1"

        config_module = importlib.reload(config_module)
        runtime = config_module._get_raw_config()
        engine = config_module.get_config()

        assert runtime.llm_timeout == 120.0
        assert runtime.retain_llm_timeout == 0.1
        assert runtime.reflect_llm_timeout == 120.0
        assert runtime.retain_max_completion_tokens == 1
        assert runtime.retain_chunk_size == 1
        assert runtime.retain_extract_causal_links is True
        assert runtime.retain_extraction_mode == "concise"
        assert runtime.retain_mission is None
        assert runtime.retain_custom_instructions is None
        assert runtime.recall_max_concurrent == 32
        assert engine.reranker_tei_batch_size == 128
        assert engine.reranker_max_candidates == 1
    finally:
        _restore_env(backup)
        importlib.reload(config_module)


def main() -> None:
    repo_root = Path(__file__).resolve().parents[2]
    repo_root_str = str(repo_root)
    if repo_root_str not in sys.path:
        sys.path.insert(0, repo_root_str)

    assert_required_files(repo_root)
    assert_isolation(repo_root)
    assert_env_contract_documented(repo_root)
    run_behavioral_matrix()
    print("Task 611 config contract check passed.")


if __name__ == "__main__":
    main()
