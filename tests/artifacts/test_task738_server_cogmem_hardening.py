"""Task 738 — Artifact: Slim server + CogMem hardening checks.

Offline checks (no real LLM needed):
1. serve_ollama_openai.py: no RETAIN_HINT / CONSOLIDATE_HINT / get_task_type
2. serve_ollama_openai.py: has 'usage' field with prompt_eval_count / eval_count
3. llm_wrapper.py: parse_llm_json has json_repair fallback
4. fact_extraction.py: has _sanitize_temporal_fact() and _TODAY_TIME_KEYWORDS
5. json-repair importable
"""

from __future__ import annotations

import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))


def test_server_no_hints() -> None:
    path = _REPO_ROOT / "serve_ollama_openai.py"
    text = path.read_text(encoding="utf-8")
    assert "RETAIN_HINT" not in text, "Server must not contain RETAIN_HINT"
    assert "CONSOLIDATE_HINT" not in text, "Server must not contain CONSOLIDATE_HINT"
    assert "get_task_type" not in text, "Server must not contain get_task_type"
    print("OK  server: no hint injection logic")


def test_server_has_usage() -> None:
    path = _REPO_ROOT / "serve_ollama_openai.py"
    text = path.read_text(encoding="utf-8")
    assert "prompt_eval_count" in text, "Server must extract prompt_eval_count from Ollama"
    assert "eval_count" in text, "Server must extract eval_count from Ollama"
    assert '"usage"' in text or "'usage'" in text, "Server response must include 'usage' field"
    print("OK  server: usage field present")


def test_llm_wrapper_json_repair() -> None:
    path = _REPO_ROOT / "cogmem_api/engine/llm_wrapper.py"
    text = path.read_text(encoding="utf-8")
    assert "json_repair" in text or "repair_json" in text, (
        "llm_wrapper.py must use json_repair as fallback"
    )
    print("OK  llm_wrapper: json_repair fallback present")


def test_fact_extraction_temporal_sanitize() -> None:
    path = _REPO_ROOT / "cogmem_api/engine/retain/fact_extraction.py"
    text = path.read_text(encoding="utf-8")
    assert "_sanitize_temporal_fact" in text, (
        "fact_extraction.py must define _sanitize_temporal_fact()"
    )
    assert "_TODAY_TIME_KEYWORDS" in text, (
        "fact_extraction.py must define _TODAY_TIME_KEYWORDS"
    )
    print("OK  fact_extraction: temporal sanitization present")


def test_json_repair_importable() -> None:
    from json_repair import repair_json
    result = repair_json('{"facts": [{"fact_type": "world", "what": "test"')
    assert "facts" in result
    print("OK  json_repair: importable and functional")


def main() -> None:
    test_server_no_hints()
    test_server_has_usage()
    test_llm_wrapper_json_repair()
    test_fact_extraction_temporal_sanitize()
    test_json_repair_importable()
    print("\nAll task-738 artifact checks passed.")


if __name__ == "__main__":
    main()
