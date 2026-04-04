# Reflect Pipeline Modules

## Purpose
- Tài liệu hóa lazy reflect synthesis path của CogMem.
- Chỉ rõ cách chuyển retrieval outputs thành evidence và answer synthesis.

## Inputs
- Question từ caller.
- Retrieved items (`RetrievalResult`, `MergedCandidate`, hoặc dict payload).
- Optional `llm_generate` callback.

## Outputs
- `ReflectSynthesisResult`: answer, used_memory_ids, networks_covered, evidence_count.
- Prompt synthesis (khi bật `include_prompt`).

## Top-down level
- Module

## Prerequisites
- `tutorials/README.md`
- `tutorials/modules/search-pipeline.md`
- `tutorials/flows/retain-recall-reflect-response.md`

## Module responsibility
- `cogmem_api/engine/reflect/__init__.py`
  - Trách nhiệm: export public API của reflect package.
- `cogmem_api/engine/reflect/models.py`
  - Trách nhiệm: schema cho evidence và synthesis outputs.
- `cogmem_api/engine/reflect/tools.py`
  - Trách nhiệm: normalize retrieval payload, convert sang `ReflectEvidence`, dedupe/rank evidence.
  - Error boundary: bỏ qua items không đủ contract (`id/text/fact_type`).
- `cogmem_api/engine/reflect/prompts.py`
  - Trách nhiệm: build prompt từ question + evidences + profile.
- `cogmem_api/engine/reflect/agent.py`
  - Trách nhiệm: orchestrate lazy synthesis và fallback answer strategy.
  - Data contracts: luôn synthesize từ retrieved evidence; không phụ thuộc observation pipeline.
  - Error boundary: khi `llm_generate` rỗng/lỗi output -> dùng `_default_markdown_answer`.

## Function inventory (public/private)
- Public functions/classes:
  - `reflect/__init__.py`: `synthesize_lazy_reflect`, `prepare_lazy_evidence`, `to_reflect_evidence`, `group_evidence_by_network`, `build_lazy_synthesis_prompt`, `ReflectEvidence`, `ReflectSynthesisResult`
  - `reflect/agent.py`: `synthesize_lazy_reflect`
  - `reflect/prompts.py`: `build_lazy_synthesis_prompt`
  - `reflect/tools.py`: `to_reflect_evidence`, `prepare_lazy_evidence`, `group_evidence_by_network`
  - `reflect/models.py`: `ReflectEvidence`, `ReflectSynthesisResult`
- Private/internal helpers:
  - `reflect/agent.py`: `_default_markdown_answer`
  - `reflect/prompts.py`: `_truncate`
  - `reflect/tools.py`: `_coerce_score`, `_coerce_datetime`, `_normalize_payload`

## Failure modes
- Retrieved items không đúng schema -> evidence bị loại, answer thiếu căn cứ.
- Số evidence quá lớn -> prompt bị dài (truncate theo helper).
- Callback LLM trả rỗng -> fallback markdown answer.

## Verify commands
- `uv run python tests/artifacts/test_task717_tutorial_core.py`
- `Select-String -Path cogmem_api/engine/reflect/*.py -Pattern "def synthesize_lazy_reflect|def prepare_lazy_evidence|class ReflectSynthesisResult|def build_lazy_synthesis_prompt"`