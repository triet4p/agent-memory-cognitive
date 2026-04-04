# LLM Embeddings Reranker Adapters

## Purpose
- Tài liệu hóa adapter layer kết nối CogMem với external models/services.
- Chỉ rõ fallback chiến lược khi provider không khả dụng.

## Inputs
- LLM provider config (base URL, model, key, timeout).
- Embedding provider config (local/openai/deterministic fallback).
- Cross-encoder config (local, remote, passthrough).

## Outputs
- LLM response text đã sanitize/parse được.
- Embedding vectors cho retain/recall.
- Cross-encoder scores cho reranking.

## Top-down level
- Module

## Prerequisites
- `tutorials/README.md`
- `tutorials/modules/engine-core-services.md`
- `tutorials/modules/search-pipeline.md`

## Module responsibility
- `cogmem_api/engine/llm_wrapper.py`
  - Trách nhiệm: normalize output text/JSON và định nghĩa config object cho LLM calls.
  - Data contracts: `sanitize_llm_output`, `parse_llm_json`, `LLMConfig`.
  - Error boundary: output quá dài/JSON malformed -> explicit exception.
- `cogmem_api/engine/embeddings.py`
  - Trách nhiệm: abstract embeddings interface + concrete providers.
  - Inbound: retain/search paths gọi generate vectors.
  - Outbound: list vector float cùng chiều embedding config.
  - Error boundary: provider init lỗi -> caller fallback deterministic.
- `cogmem_api/engine/cross_encoder.py`
  - Trách nhiệm: abstract + concrete cross encoder implementations.
  - Outbound: điểm relevance cho candidate reranking.
  - Error boundary: remote model timeout/network errors, local model load errors.

## Function inventory (public/private)
- Public functions/classes:
  - `cogmem_api/engine/llm_wrapper.py`: `sanitize_llm_output`, `OutputTooLongError`, `parse_llm_json`, `LLMConfig`
  - `cogmem_api/engine/embeddings.py`: `Embeddings`, `DeterministicEmbeddings`, `LocalSTEmbeddings`, `OpenAIEmbeddings`, `create_embeddings_from_env`
  - `cogmem_api/engine/cross_encoder.py`: `CrossEncoderModel`, `LocalSTCrossEncoder`, `RemoteTEICrossEncoder`, `RRFPassthroughCrossEncoder`, `create_cross_encoder_from_env`
- Private/internal helpers:
  - Provider-specific init/predict internals trong từng class implementation.

## Failure modes
- LLM output vượt ngưỡng chiều dài hoặc không parse JSON được.
- Embedding service lỗi xác thực hoặc network.
- Cross-encoder model load fail khiến rerank phải fallback/passthrough.

## Verify commands
- `uv run python tests/artifacts/test_task717_tutorial_core.py`
- `Select-String -Path cogmem_api/engine/llm_wrapper.py,cogmem_api/engine/embeddings.py,cogmem_api/engine/cross_encoder.py -Pattern "class LLMConfig|class Embeddings|class CrossEncoderModel|create_.*_from_env"`