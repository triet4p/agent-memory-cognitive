# Function Deep Dive - [cogmem_api/engine/retain/fact_extraction.py](https://github.com/triet4p/agent-memory-cognitive/blob/master/cogmem_api/engine/retain/fact_extraction.py)

## Purpose
- Mô tả chi tiết các hàm ingestion/retain và chuẩn hóa dữ liệu trước khi ghi graph.
- Đảm bảo mọi hàm public/private trong module đều có contract docs phục vụ onboarding và traceability.

## Inputs
- Nguồn từ function inventory S18.1 (`tutorials/functions/function-inventory.json`).
- Chữ ký hàm, kiểu trả về, và vị trí dòng trong source module tương ứng.

## Outputs
- Tài liệu deep-dive cho 21 hàm/method trong module này.
- Mỗi hàm có purpose, inputs, outputs, side effects, dependency calls, failure modes, pre/post-conditions, verify command.

## Top-down level
- Function

## Prerequisites
- `tutorials/functions/function-inventory.md`
- `tutorials/module-map.md`
- Module dossier tương ứng trong `tutorials/modules/`

## Module responsibility
- Source module: `cogmem_api/engine/retain/fact_extraction.py`.
- Public/private breakdown: public=1, private=20.
- Bối cảnh chi tiết từng hàm nằm ở phần Function inventory bên dưới.

## Function inventory (public/private)
| Owner | Function | Visibility | Signature | Location | Deep-dive status |
|---|---|---|---|---|---|
| (module) | _safe_datetime | private | _safe_datetime(value: datetime \| None) -> datetime \| None | [cogmem_api/engine/retain/fact_extraction.py](https://github.com/triet4p/agent-memory-cognitive/blob/master/cogmem_api/engine/retain/fact_extraction.py):102 | documented |
| (module) | _parse_datetime | private | _parse_datetime(value: Any) -> datetime \| None | [cogmem_api/engine/retain/fact_extraction.py](https://github.com/triet4p/agent-memory-cognitive/blob/master/cogmem_api/engine/retain/fact_extraction.py):108 | documented |
| (module) | _extract_entities | private | _extract_entities(raw_entities: Any) -> list[str] | [cogmem_api/engine/retain/fact_extraction.py](https://github.com/triet4p/agent-memory-cognitive/blob/master/cogmem_api/engine/retain/fact_extraction.py):122 | documented |
| (module) | _extract_entities_from_text | private | _extract_entities_from_text(text: str) -> list[str] | [cogmem_api/engine/retain/fact_extraction.py](https://github.com/triet4p/agent-memory-cognitive/blob/master/cogmem_api/engine/retain/fact_extraction.py):145 | documented |
| (module) | _first_non_empty | private | _first_non_empty(payload: dict[str, Any], keys: list[str]) -> str | [cogmem_api/engine/retain/fact_extraction.py](https://github.com/triet4p/agent-memory-cognitive/blob/master/cogmem_api/engine/retain/fact_extraction.py):153 | documented |
| (module) | _normalized_optional_text | private | _normalized_optional_text(value: Any) -> str \| None | [cogmem_api/engine/retain/fact_extraction.py](https://github.com/triet4p/agent-memory-cognitive/blob/master/cogmem_api/engine/retain/fact_extraction.py):161 | documented |
| (module) | _infer_fact_type | private | _infer_fact_type(segment: str, default_fact_type: str='world') -> str | [cogmem_api/engine/retain/fact_extraction.py](https://github.com/triet4p/agent-memory-cognitive/blob/master/cogmem_api/engine/retain/fact_extraction.py):172 | documented |
| (module) | _extract_causal_relations | private | _extract_causal_relations(raw_relations: Any) -> list[CausalRelation] | [cogmem_api/engine/retain/fact_extraction.py](https://github.com/triet4p/agent-memory-cognitive/blob/master/cogmem_api/engine/retain/fact_extraction.py):185 | documented |
| (module) | _extract_action_effect_relations | private | _extract_action_effect_relations(raw_relations: Any) -> list[ActionEffectRelation] | [cogmem_api/engine/retain/fact_extraction.py](https://github.com/triet4p/agent-memory-cognitive/blob/master/cogmem_api/engine/retain/fact_extraction.py):217 | documented |
| (module) | _parse_action_effect_triplet | private | _parse_action_effect_triplet(text: str) -> tuple[str, str, str] \| None | [cogmem_api/engine/retain/fact_extraction.py](https://github.com/triet4p/agent-memory-cognitive/blob/master/cogmem_api/engine/retain/fact_extraction.py):253 | documented |
| (module) | _extract_transition_relations | private | _extract_transition_relations(raw_relations: Any) -> list[TransitionRelation] | [cogmem_api/engine/retain/fact_extraction.py](https://github.com/triet4p/agent-memory-cognitive/blob/master/cogmem_api/engine/retain/fact_extraction.py):278 | documented |
| (module) | _fallback_fact_splits | private | _fallback_fact_splits(text: str) -> list[str] | [cogmem_api/engine/retain/fact_extraction.py](https://github.com/triet4p/agent-memory-cognitive/blob/master/cogmem_api/engine/retain/fact_extraction.py):318 | documented |
| (module) | _chunk_content | private | _chunk_content(text: str, max_chars: int) -> list[str] | [cogmem_api/engine/retain/fact_extraction.py](https://github.com/triet4p/agent-memory-cognitive/blob/master/cogmem_api/engine/retain/fact_extraction.py):325 | documented |
| (module) | _build_prompt | private | _build_prompt(config: Any) -> tuple[str, str] | [cogmem_api/engine/retain/fact_extraction.py](https://github.com/triet4p/agent-memory-cognitive/blob/master/cogmem_api/engine/retain/fact_extraction.py):353 | documented |
| (module) | _build_user_message | private | _build_user_message(chunk: str, chunk_index: int, total_chunks: int, event_date: datetime \| None, context: str, metadata: dict[str, Any] \| None) -> str | [cogmem_api/engine/retain/fact_extraction.py](https://github.com/triet4p/agent-memory-cognitive/blob/master/cogmem_api/engine/retain/fact_extraction.py):381 | documented |
| (module) | _call_llm_chunk | private | async _call_llm_chunk(llm_config: Any, prompt: str, user_message: str, max_completion_tokens: int) -> tuple[list[dict[str, Any]], TokenUsage] | [cogmem_api/engine/retain/fact_extraction.py](https://github.com/triet4p/agent-memory-cognitive/blob/master/cogmem_api/engine/retain/fact_extraction.py):405 | documented |
| (module) | _normalize_llm_facts | private | _normalize_llm_facts(raw_facts: list[dict[str, Any]], content: RetainContent, content_index: int, chunk_index: int, mode: str, chunk_text: str, extract_causal_links: bool) -> list[ExtractedFact] | [cogmem_api/engine/retain/fact_extraction.py](https://github.com/triet4p/agent-memory-cognitive/blob/master/cogmem_api/engine/retain/fact_extraction.py):462 | documented |
| (module) | _extract_facts_with_llm | private | async _extract_facts_with_llm(content: RetainContent, content_index: int, llm_config: Any, config: Any) -> tuple[list[ExtractedFact], list[ChunkMetadata], TokenUsage] | [cogmem_api/engine/retain/fact_extraction.py](https://github.com/triet4p/agent-memory-cognitive/blob/master/cogmem_api/engine/retain/fact_extraction.py):582 | documented |
| (module) | _extract_seeded_facts | private | _extract_seeded_facts(content: RetainContent, content_index: int, extract_causal_links: bool) -> tuple[list[ExtractedFact], ChunkMetadata] | [cogmem_api/engine/retain/fact_extraction.py](https://github.com/triet4p/agent-memory-cognitive/blob/master/cogmem_api/engine/retain/fact_extraction.py):641 | documented |
| (module) | _extract_fallback_facts | private | _extract_fallback_facts(content: RetainContent, content_index: int) -> tuple[list[ExtractedFact], ChunkMetadata] | [cogmem_api/engine/retain/fact_extraction.py](https://github.com/triet4p/agent-memory-cognitive/blob/master/cogmem_api/engine/retain/fact_extraction.py):735 | documented |
| (module) | extract_facts_from_contents | public | async extract_facts_from_contents(contents: list[RetainContent], llm_config, agent_name: str, config, pool=None, operation_id: str \| None=None, schema: str \| None=None) -> tuple[list[ExtractedFact], list[ChunkMetadata], TokenUsage] | [cogmem_api/engine/retain/fact_extraction.py](https://github.com/triet4p/agent-memory-cognitive/blob/master/cogmem_api/engine/retain/fact_extraction.py):781 | documented |

### Function: (module)._safe_datetime
- Signature: `_safe_datetime(value: datetime | None) -> datetime | None`
- Visibility: `private`
- Location: `cogmem_api/engine/retain/fact_extraction.py:102`
- Purpose:
  - Thực thi nghiệp vụ `_safe_datetime` trong phạm vi `(module)` của module `cogmem_api/engine/retain/fact_extraction.py`.
- Inputs:
  - Theo chữ ký: `_safe_datetime(value: datetime | None) -> datetime | None`.
- Outputs:
  - Trả về kiểu: `datetime | None`.
- Side effects:
  - Không phát hiện side effect rõ ràng từ phân tích static call graph.
- Dependency calls:
  - `replace`
- Failure modes:
  - Không phát hiện raise tường minh; lỗi có thể phát sinh từ dependency gọi bên trong.
- Pre-conditions:
  - Các tham số bắt buộc theo chữ ký phải hợp lệ kiểu dữ liệu trước khi gọi.
- Post-conditions:
  - Hàm kết thúc với giá trị trả về theo contract; trạng thái ngoài hàm chỉ thay đổi khi có side effect nêu ở trên.
- Verify command:
  - `Select-String -Path cogmem_api/engine/retain/fact_extraction.py -Pattern "def _safe_datetime|async def _safe_datetime"`

### Function: (module)._parse_datetime
- Signature: `_parse_datetime(value: Any) -> datetime | None`
- Visibility: `private`
- Location: `cogmem_api/engine/retain/fact_extraction.py:108`
- Purpose:
  - Thực thi nghiệp vụ `_parse_datetime` trong phạm vi `(module)` của module `cogmem_api/engine/retain/fact_extraction.py`.
- Inputs:
  - Theo chữ ký: `_parse_datetime(value: Any) -> datetime | None`.
- Outputs:
  - Trả về kiểu: `datetime | None`.
- Side effects:
  - Không phát hiện side effect rõ ràng từ phân tích static call graph.
- Dependency calls:
  - `isinstance`, `_safe_datetime`, `strip`, `fromisoformat`, `replace`
- Failure modes:
  - Không phát hiện raise tường minh; lỗi có thể phát sinh từ dependency gọi bên trong.
- Pre-conditions:
  - Các tham số bắt buộc theo chữ ký phải hợp lệ kiểu dữ liệu trước khi gọi.
- Post-conditions:
  - Hàm kết thúc với giá trị trả về theo contract; trạng thái ngoài hàm chỉ thay đổi khi có side effect nêu ở trên.
- Verify command:
  - `Select-String -Path cogmem_api/engine/retain/fact_extraction.py -Pattern "def _parse_datetime|async def _parse_datetime"`

### Function: (module)._extract_entities
- Signature: `_extract_entities(raw_entities: Any) -> list[str]`
- Visibility: `private`
- Location: `cogmem_api/engine/retain/fact_extraction.py:122`
- Purpose:
  - Thực thi nghiệp vụ `_extract_entities` trong phạm vi `(module)` của module `cogmem_api/engine/retain/fact_extraction.py`.
- Inputs:
  - Theo chữ ký: `_extract_entities(raw_entities: Any) -> list[str]`.
- Outputs:
  - Trả về kiểu: `list[str]`.
- Side effects:
  - Không phát hiện side effect rõ ràng từ phân tích static call graph.
- Dependency calls:
  - `set`, `lower`, `isinstance`, `strip`, `append`, `add`, `str`, `get`
- Failure modes:
  - Không phát hiện raise tường minh; lỗi có thể phát sinh từ dependency gọi bên trong.
- Pre-conditions:
  - Các tham số bắt buộc theo chữ ký phải hợp lệ kiểu dữ liệu trước khi gọi.
- Post-conditions:
  - Hàm kết thúc với giá trị trả về theo contract; trạng thái ngoài hàm chỉ thay đổi khi có side effect nêu ở trên.
- Verify command:
  - `Select-String -Path cogmem_api/engine/retain/fact_extraction.py -Pattern "def _extract_entities|async def _extract_entities"`

### Function: (module)._extract_entities_from_text
- Signature: `_extract_entities_from_text(text: str) -> list[str]`
- Visibility: `private`
- Location: `cogmem_api/engine/retain/fact_extraction.py:145`
- Purpose:
  - Thực thi nghiệp vụ `_extract_entities_from_text` trong phạm vi `(module)` của module `cogmem_api/engine/retain/fact_extraction.py`.
- Inputs:
  - Theo chữ ký: `_extract_entities_from_text(text: str) -> list[str]`.
- Outputs:
  - Trả về kiểu: `list[str]`.
- Side effects:
  - Không phát hiện side effect rõ ràng từ phân tích static call graph.
- Dependency calls:
  - `findall`
- Failure modes:
  - Không phát hiện raise tường minh; lỗi có thể phát sinh từ dependency gọi bên trong.
- Pre-conditions:
  - Các tham số bắt buộc theo chữ ký phải hợp lệ kiểu dữ liệu trước khi gọi.
- Post-conditions:
  - Hàm kết thúc với giá trị trả về theo contract; trạng thái ngoài hàm chỉ thay đổi khi có side effect nêu ở trên.
- Verify command:
  - `Select-String -Path cogmem_api/engine/retain/fact_extraction.py -Pattern "def _extract_entities_from_text|async def _extract_entities_from_text"`

### Function: (module)._first_non_empty
- Signature: `_first_non_empty(payload: dict[str, Any], keys: list[str]) -> str`
- Visibility: `private`
- Location: `cogmem_api/engine/retain/fact_extraction.py:153`
- Purpose:
  - Thực thi nghiệp vụ `_first_non_empty` trong phạm vi `(module)` của module `cogmem_api/engine/retain/fact_extraction.py`.
- Inputs:
  - Theo chữ ký: `_first_non_empty(payload: dict[str, Any], keys: list[str]) -> str`.
- Outputs:
  - Trả về kiểu: `str`.
- Side effects:
  - Không phát hiện side effect rõ ràng từ phân tích static call graph.
- Dependency calls:
  - `get`, `isinstance`, `strip`
- Failure modes:
  - Không phát hiện raise tường minh; lỗi có thể phát sinh từ dependency gọi bên trong.
- Pre-conditions:
  - Các tham số bắt buộc theo chữ ký phải hợp lệ kiểu dữ liệu trước khi gọi.
- Post-conditions:
  - Hàm kết thúc với giá trị trả về theo contract; trạng thái ngoài hàm chỉ thay đổi khi có side effect nêu ở trên.
- Verify command:
  - `Select-String -Path cogmem_api/engine/retain/fact_extraction.py -Pattern "def _first_non_empty|async def _first_non_empty"`

### Function: (module)._normalized_optional_text
- Signature: `_normalized_optional_text(value: Any) -> str | None`
- Visibility: `private`
- Location: `cogmem_api/engine/retain/fact_extraction.py:161`
- Purpose:
  - Thực thi nghiệp vụ `_normalized_optional_text` trong phạm vi `(module)` của module `cogmem_api/engine/retain/fact_extraction.py`.
- Inputs:
  - Theo chữ ký: `_normalized_optional_text(value: Any) -> str | None`.
- Outputs:
  - Trả về kiểu: `str | None`.
- Side effects:
  - Không phát hiện side effect rõ ràng từ phân tích static call graph.
- Dependency calls:
  - `strip`, `isinstance`, `upper`
- Failure modes:
  - Không phát hiện raise tường minh; lỗi có thể phát sinh từ dependency gọi bên trong.
- Pre-conditions:
  - Các tham số bắt buộc theo chữ ký phải hợp lệ kiểu dữ liệu trước khi gọi.
- Post-conditions:
  - Hàm kết thúc với giá trị trả về theo contract; trạng thái ngoài hàm chỉ thay đổi khi có side effect nêu ở trên.
- Verify command:
  - `Select-String -Path cogmem_api/engine/retain/fact_extraction.py -Pattern "def _normalized_optional_text|async def _normalized_optional_text"`

### Function: (module)._infer_fact_type
- Signature: `_infer_fact_type(segment: str, default_fact_type: str='world') -> str`
- Visibility: `private`
- Location: `cogmem_api/engine/retain/fact_extraction.py:172`
- Purpose:
  - Thực thi nghiệp vụ `_infer_fact_type` trong phạm vi `(module)` của module `cogmem_api/engine/retain/fact_extraction.py`.
- Inputs:
  - Theo chữ ký: `_infer_fact_type(segment: str, default_fact_type: str='world') -> str`.
- Outputs:
  - Trả về kiểu: `str`.
- Side effects:
  - Không phát hiện side effect rõ ràng từ phân tích static call graph.
- Dependency calls:
  - `lower`, `search`
- Failure modes:
  - Không phát hiện raise tường minh; lỗi có thể phát sinh từ dependency gọi bên trong.
- Pre-conditions:
  - Các tham số bắt buộc theo chữ ký phải hợp lệ kiểu dữ liệu trước khi gọi.
- Post-conditions:
  - Hàm kết thúc với giá trị trả về theo contract; trạng thái ngoài hàm chỉ thay đổi khi có side effect nêu ở trên.
- Verify command:
  - `Select-String -Path cogmem_api/engine/retain/fact_extraction.py -Pattern "def _infer_fact_type|async def _infer_fact_type"`

### Function: (module)._extract_causal_relations
- Signature: `_extract_causal_relations(raw_relations: Any) -> list[CausalRelation]`
- Visibility: `private`
- Location: `cogmem_api/engine/retain/fact_extraction.py:185`
- Purpose:
  - Thực thi nghiệp vụ `_extract_causal_relations` trong phạm vi `(module)` của module `cogmem_api/engine/retain/fact_extraction.py`.
- Inputs:
  - Theo chữ ký: `_extract_causal_relations(raw_relations: Any) -> list[CausalRelation]`.
- Outputs:
  - Trả về kiểu: `list[CausalRelation]`.
- Side effects:
  - Không phát hiện side effect rõ ràng từ phân tích static call graph.
- Dependency calls:
  - `get`, `append`, `isinstance`, `float`, `CausalRelation`, `str`, `max`, `min`
- Failure modes:
  - Không phát hiện raise tường minh; lỗi có thể phát sinh từ dependency gọi bên trong.
- Pre-conditions:
  - Các tham số bắt buộc theo chữ ký phải hợp lệ kiểu dữ liệu trước khi gọi.
- Post-conditions:
  - Hàm kết thúc với giá trị trả về theo contract; trạng thái ngoài hàm chỉ thay đổi khi có side effect nêu ở trên.
- Verify command:
  - `Select-String -Path cogmem_api/engine/retain/fact_extraction.py -Pattern "def _extract_causal_relations|async def _extract_causal_relations"`

### Function: (module)._extract_action_effect_relations
- Signature: `_extract_action_effect_relations(raw_relations: Any) -> list[ActionEffectRelation]`
- Visibility: `private`
- Location: `cogmem_api/engine/retain/fact_extraction.py:217`
- Purpose:
  - Thực thi nghiệp vụ `_extract_action_effect_relations` trong phạm vi `(module)` của module `cogmem_api/engine/retain/fact_extraction.py`.
- Inputs:
  - Theo chữ ký: `_extract_action_effect_relations(raw_relations: Any) -> list[ActionEffectRelation]`.
- Outputs:
  - Trả về kiểu: `list[ActionEffectRelation]`.
- Side effects:
  - Không phát hiện side effect rõ ràng từ phân tích static call graph.
- Dependency calls:
  - `get`, `lower`, `append`, `isinstance`, `float`, `ActionEffectRelation`, `strip`, `max`, `str`, `min`
- Failure modes:
  - Không phát hiện raise tường minh; lỗi có thể phát sinh từ dependency gọi bên trong.
- Pre-conditions:
  - Các tham số bắt buộc theo chữ ký phải hợp lệ kiểu dữ liệu trước khi gọi.
- Post-conditions:
  - Hàm kết thúc với giá trị trả về theo contract; trạng thái ngoài hàm chỉ thay đổi khi có side effect nêu ở trên.
- Verify command:
  - `Select-String -Path cogmem_api/engine/retain/fact_extraction.py -Pattern "def _extract_action_effect_relations|async def _extract_action_effect_relations"`

### Function: (module)._parse_action_effect_triplet
- Signature: `_parse_action_effect_triplet(text: str) -> tuple[str, str, str] | None`
- Visibility: `private`
- Location: `cogmem_api/engine/retain/fact_extraction.py:253`
- Purpose:
  - Thực thi nghiệp vụ `_parse_action_effect_triplet` trong phạm vi `(module)` của module `cogmem_api/engine/retain/fact_extraction.py`.
- Inputs:
  - Theo chữ ký: `_parse_action_effect_triplet(text: str) -> tuple[str, str, str] | None`.
- Outputs:
  - Trả về kiểu: `tuple[str, str, str] | None`.
- Side effects:
  - Không phát hiện side effect rõ ràng từ phân tích static call graph.
- Dependency calls:
  - `join`, `compile`, `search`, `split`, `strip`, `group`
- Failure modes:
  - Không phát hiện raise tường minh; lỗi có thể phát sinh từ dependency gọi bên trong.
- Pre-conditions:
  - Các tham số bắt buộc theo chữ ký phải hợp lệ kiểu dữ liệu trước khi gọi.
- Post-conditions:
  - Hàm kết thúc với giá trị trả về theo contract; trạng thái ngoài hàm chỉ thay đổi khi có side effect nêu ở trên.
- Verify command:
  - `Select-String -Path cogmem_api/engine/retain/fact_extraction.py -Pattern "def _parse_action_effect_triplet|async def _parse_action_effect_triplet"`

### Function: (module)._extract_transition_relations
- Signature: `_extract_transition_relations(raw_relations: Any) -> list[TransitionRelation]`
- Visibility: `private`
- Location: `cogmem_api/engine/retain/fact_extraction.py:278`
- Purpose:
  - Thực thi nghiệp vụ `_extract_transition_relations` trong phạm vi `(module)` của module `cogmem_api/engine/retain/fact_extraction.py`.
- Inputs:
  - Theo chữ ký: `_extract_transition_relations(raw_relations: Any) -> list[TransitionRelation]`.
- Outputs:
  - Trả về kiểu: `list[TransitionRelation]`.
- Side effects:
  - Không phát hiện side effect rõ ràng từ phân tích static call graph.
- Dependency calls:
  - `lower`, `get`, `isinstance`, `append`, `float`, `TransitionRelation`, `strip`, `max`, `str`, `min`
- Failure modes:
  - Không phát hiện raise tường minh; lỗi có thể phát sinh từ dependency gọi bên trong.
- Pre-conditions:
  - Các tham số bắt buộc theo chữ ký phải hợp lệ kiểu dữ liệu trước khi gọi.
- Post-conditions:
  - Hàm kết thúc với giá trị trả về theo contract; trạng thái ngoài hàm chỉ thay đổi khi có side effect nêu ở trên.
- Verify command:
  - `Select-String -Path cogmem_api/engine/retain/fact_extraction.py -Pattern "def _extract_transition_relations|async def _extract_transition_relations"`

### Function: (module)._fallback_fact_splits
- Signature: `_fallback_fact_splits(text: str) -> list[str]`
- Visibility: `private`
- Location: `cogmem_api/engine/retain/fact_extraction.py:318`
- Purpose:
  - Thực thi nghiệp vụ `_fallback_fact_splits` trong phạm vi `(module)` của module `cogmem_api/engine/retain/fact_extraction.py`.
- Inputs:
  - Theo chữ ký: `_fallback_fact_splits(text: str) -> list[str]`.
- Outputs:
  - Trả về kiểu: `list[str]`.
- Side effects:
  - Không phát hiện side effect rõ ràng từ phân tích static call graph.
- Dependency calls:
  - `strip`, `split`
- Failure modes:
  - Không phát hiện raise tường minh; lỗi có thể phát sinh từ dependency gọi bên trong.
- Pre-conditions:
  - Các tham số bắt buộc theo chữ ký phải hợp lệ kiểu dữ liệu trước khi gọi.
- Post-conditions:
  - Hàm kết thúc với giá trị trả về theo contract; trạng thái ngoài hàm chỉ thay đổi khi có side effect nêu ở trên.
- Verify command:
  - `Select-String -Path cogmem_api/engine/retain/fact_extraction.py -Pattern "def _fallback_fact_splits|async def _fallback_fact_splits"`

### Function: (module)._chunk_content
- Signature: `_chunk_content(text: str, max_chars: int) -> list[str]`
- Visibility: `private`
- Location: `cogmem_api/engine/retain/fact_extraction.py:325`
- Purpose:
  - Thực thi nghiệp vụ `_chunk_content` trong phạm vi `(module)` của module `cogmem_api/engine/retain/fact_extraction.py`.
- Inputs:
  - Theo chữ ký: `_chunk_content(text: str, max_chars: int) -> list[str]`.
- Outputs:
  - Trả về kiểu: `list[str]`.
- Side effects:
  - Không phát hiện side effect rõ ràng từ phân tích static call graph.
- Dependency calls:
  - `strip`, `append`, `len`, `split`, `join`
- Failure modes:
  - Không phát hiện raise tường minh; lỗi có thể phát sinh từ dependency gọi bên trong.
- Pre-conditions:
  - Các tham số bắt buộc theo chữ ký phải hợp lệ kiểu dữ liệu trước khi gọi.
- Post-conditions:
  - Hàm kết thúc với giá trị trả về theo contract; trạng thái ngoài hàm chỉ thay đổi khi có side effect nêu ở trên.
- Verify command:
  - `Select-String -Path cogmem_api/engine/retain/fact_extraction.py -Pattern "def _chunk_content|async def _chunk_content"`

### Function: (module)._build_prompt
- Signature: `_build_prompt(config: Any) -> tuple[str, str]`
- Visibility: `private`
- Location: `cogmem_api/engine/retain/fact_extraction.py:353`
- Purpose:
  - Thực thi nghiệp vụ `_build_prompt` trong phạm vi `(module)` của module `cogmem_api/engine/retain/fact_extraction.py`.
- Inputs:
  - Theo chữ ký: `_build_prompt(config: Any) -> tuple[str, str]`.
- Outputs:
  - Trả về kiểu: `tuple[str, str]`.
- Side effects:
  - Không phát hiện side effect rõ ràng từ phân tích static call graph.
- Dependency calls:
  - `lower`, `_normalized_optional_text`, `getattr`, `format`, `strip`, `str`
- Failure modes:
  - Không phát hiện raise tường minh; lỗi có thể phát sinh từ dependency gọi bên trong.
- Pre-conditions:
  - Các tham số bắt buộc theo chữ ký phải hợp lệ kiểu dữ liệu trước khi gọi.
- Post-conditions:
  - Hàm kết thúc với giá trị trả về theo contract; trạng thái ngoài hàm chỉ thay đổi khi có side effect nêu ở trên.
- Verify command:
  - `Select-String -Path cogmem_api/engine/retain/fact_extraction.py -Pattern "def _build_prompt|async def _build_prompt"`

### Function: (module)._build_user_message
- Signature: `_build_user_message(chunk: str, chunk_index: int, total_chunks: int, event_date: datetime | None, context: str, metadata: dict[str, Any] | None) -> str`
- Visibility: `private`
- Location: `cogmem_api/engine/retain/fact_extraction.py:381`
- Purpose:
  - Thực thi nghiệp vụ `_build_user_message` trong phạm vi `(module)` của module `cogmem_api/engine/retain/fact_extraction.py`.
- Inputs:
  - Theo chữ ký: `_build_user_message(chunk: str, chunk_index: int, total_chunks: int, event_date: datetime | None, context: str, metadata: dict[str, Any] | None) -> str`.
- Outputs:
  - Trả về kiểu: `str`.
- Side effects:
  - Không phát hiện side effect rõ ràng từ phân tích static call graph.
- Dependency calls:
  - `isoformat`, `items`, `join`
- Failure modes:
  - Không phát hiện raise tường minh; lỗi có thể phát sinh từ dependency gọi bên trong.
- Pre-conditions:
  - Các tham số bắt buộc theo chữ ký phải hợp lệ kiểu dữ liệu trước khi gọi.
- Post-conditions:
  - Hàm kết thúc với giá trị trả về theo contract; trạng thái ngoài hàm chỉ thay đổi khi có side effect nêu ở trên.
- Verify command:
  - `Select-String -Path cogmem_api/engine/retain/fact_extraction.py -Pattern "def _build_user_message|async def _build_user_message"`

### Function: (module)._call_llm_chunk
- Signature: `async _call_llm_chunk(llm_config: Any, prompt: str, user_message: str, max_completion_tokens: int) -> tuple[list[dict[str, Any]], TokenUsage]`
- Visibility: `private`
- Location: `cogmem_api/engine/retain/fact_extraction.py:405`
- Purpose:
  - Thực thi nghiệp vụ `_call_llm_chunk` trong phạm vi `(module)` của module `cogmem_api/engine/retain/fact_extraction.py`.
- Inputs:
  - Theo chữ ký: `async _call_llm_chunk(llm_config: Any, prompt: str, user_message: str, max_completion_tokens: int) -> tuple[list[dict[str, Any]], TokenUsage]`.
- Outputs:
  - Trả về kiểu: `tuple[list[dict[str, Any]], TokenUsage]`.
- Side effects:
  - Không phát hiện side effect rõ ràng từ phân tích static call graph.
- Dependency calls:
  - `TokenUsage`, `isinstance`, `get`, `hasattr`, `call`, `len`, `parse_llm_json`
- Failure modes:
  - Không phát hiện raise tường minh; lỗi có thể phát sinh từ dependency gọi bên trong.
- Pre-conditions:
  - Các tham số bắt buộc theo chữ ký phải hợp lệ kiểu dữ liệu trước khi gọi.
- Post-conditions:
  - Hàm kết thúc với giá trị trả về theo contract; trạng thái ngoài hàm chỉ thay đổi khi có side effect nêu ở trên.
- Verify command:
  - `Select-String -Path cogmem_api/engine/retain/fact_extraction.py -Pattern "def _call_llm_chunk|async def _call_llm_chunk"`

### Function: (module)._normalize_llm_facts
- Signature: `_normalize_llm_facts(raw_facts: list[dict[str, Any]], content: RetainContent, content_index: int, chunk_index: int, mode: str, chunk_text: str, extract_causal_links: bool) -> list[ExtractedFact]`
- Visibility: `private`
- Location: `cogmem_api/engine/retain/fact_extraction.py:462`
- Purpose:
  - Thực thi nghiệp vụ `_normalize_llm_facts` trong phạm vi `(module)` của module `cogmem_api/engine/retain/fact_extraction.py`.
- Inputs:
  - Theo chữ ký: `_normalize_llm_facts(raw_facts: list[dict[str, Any]], content: RetainContent, content_index: int, chunk_index: int, mode: str, chunk_text: str, extract_causal_links: bool) -> list[ExtractedFact]`.
- Outputs:
  - Trả về kiểu: `list[ExtractedFact]`.
- Side effects:
  - Không phát hiện side effect rõ ràng từ phân tích static call graph.
- Dependency calls:
  - `lower`, `coerce_fact_type`, `dict`, `isinstance`, `get`, `_extract_action_effect_relations`, `_extract_entities`, `_parse_datetime`, `append`, `_first_non_empty`, `_normalized_optional_text`, `join`
- Failure modes:
  - Không phát hiện raise tường minh; lỗi có thể phát sinh từ dependency gọi bên trong.
- Pre-conditions:
  - Các tham số bắt buộc theo chữ ký phải hợp lệ kiểu dữ liệu trước khi gọi.
- Post-conditions:
  - Hàm kết thúc với giá trị trả về theo contract; trạng thái ngoài hàm chỉ thay đổi khi có side effect nêu ở trên.
- Verify command:
  - `Select-String -Path cogmem_api/engine/retain/fact_extraction.py -Pattern "def _normalize_llm_facts|async def _normalize_llm_facts"`

### Function: (module)._extract_facts_with_llm
- Signature: `async _extract_facts_with_llm(content: RetainContent, content_index: int, llm_config: Any, config: Any) -> tuple[list[ExtractedFact], list[ChunkMetadata], TokenUsage]`
- Visibility: `private`
- Location: `cogmem_api/engine/retain/fact_extraction.py:582`
- Purpose:
  - Thực thi nghiệp vụ `_extract_facts_with_llm` trong phạm vi `(module)` của module `cogmem_api/engine/retain/fact_extraction.py`.
- Inputs:
  - Theo chữ ký: `async _extract_facts_with_llm(content: RetainContent, content_index: int, llm_config: Any, config: Any) -> tuple[list[ExtractedFact], list[ChunkMetadata], TokenUsage]`.
- Outputs:
  - Trả về kiểu: `tuple[list[ExtractedFact], list[ChunkMetadata], TokenUsage]`.
- Side effects:
  - Không phát hiện side effect rõ ràng từ phân tích static call graph.
- Dependency calls:
  - `TokenUsage`, `_build_prompt`, `int`, `bool`, `_chunk_content`, `enumerate`, `getattr`, `_build_user_message`, `_normalize_llm_facts`, `extend`, `append`, `hasattr`
- Failure modes:
  - Không phát hiện raise tường minh; lỗi có thể phát sinh từ dependency gọi bên trong.
- Pre-conditions:
  - Các tham số bắt buộc theo chữ ký phải hợp lệ kiểu dữ liệu trước khi gọi.
- Post-conditions:
  - Hàm kết thúc với giá trị trả về theo contract; trạng thái ngoài hàm chỉ thay đổi khi có side effect nêu ở trên.
- Verify command:
  - `Select-String -Path cogmem_api/engine/retain/fact_extraction.py -Pattern "def _extract_facts_with_llm|async def _extract_facts_with_llm"`

### Function: (module)._extract_seeded_facts
- Signature: `_extract_seeded_facts(content: RetainContent, content_index: int, extract_causal_links: bool) -> tuple[list[ExtractedFact], ChunkMetadata]`
- Visibility: `private`
- Location: `cogmem_api/engine/retain/fact_extraction.py:641`
- Purpose:
  - Thực thi nghiệp vụ `_extract_seeded_facts` trong phạm vi `(module)` của module `cogmem_api/engine/retain/fact_extraction.py`.
- Inputs:
  - Theo chữ ký: `_extract_seeded_facts(content: RetainContent, content_index: int, extract_causal_links: bool) -> tuple[list[ExtractedFact], ChunkMetadata]`.
- Outputs:
  - Trả về kiểu: `tuple[list[ExtractedFact], ChunkMetadata]`.
- Side effects:
  - Không phát hiện side effect rõ ràng từ phân tích static call graph.
- Dependency calls:
  - `list`, `ChunkMetadata`, `strip`, `dict`, `get`, `_extract_action_effect_relations`, `_extract_entities`, `append`, `coerce_fact_type`, `_infer_fact_type`, `str`, `max`
- Failure modes:
  - Không phát hiện raise tường minh; lỗi có thể phát sinh từ dependency gọi bên trong.
- Pre-conditions:
  - Các tham số bắt buộc theo chữ ký phải hợp lệ kiểu dữ liệu trước khi gọi.
- Post-conditions:
  - Hàm kết thúc với giá trị trả về theo contract; trạng thái ngoài hàm chỉ thay đổi khi có side effect nêu ở trên.
- Verify command:
  - `Select-String -Path cogmem_api/engine/retain/fact_extraction.py -Pattern "def _extract_seeded_facts|async def _extract_seeded_facts"`

### Function: (module)._extract_fallback_facts
- Signature: `_extract_fallback_facts(content: RetainContent, content_index: int) -> tuple[list[ExtractedFact], ChunkMetadata]`
- Visibility: `private`
- Location: `cogmem_api/engine/retain/fact_extraction.py:735`
- Purpose:
  - Thực thi nghiệp vụ `_extract_fallback_facts` trong phạm vi `(module)` của module `cogmem_api/engine/retain/fact_extraction.py`.
- Inputs:
  - Theo chữ ký: `_extract_fallback_facts(content: RetainContent, content_index: int) -> tuple[list[ExtractedFact], ChunkMetadata]`.
- Outputs:
  - Trả về kiểu: `tuple[list[ExtractedFact], ChunkMetadata]`.
- Side effects:
  - Không phát hiện side effect rõ ràng từ phân tích static call graph.
- Dependency calls:
  - `_fallback_fact_splits`, `_extract_entities`, `ChunkMetadata`, `_extract_entities_from_text`, `_infer_fact_type`, `dict`, `append`, `_parse_action_effect_triplet`, `ExtractedFact`, `len`, `_safe_datetime`
- Failure modes:
  - Không phát hiện raise tường minh; lỗi có thể phát sinh từ dependency gọi bên trong.
- Pre-conditions:
  - Các tham số bắt buộc theo chữ ký phải hợp lệ kiểu dữ liệu trước khi gọi.
- Post-conditions:
  - Hàm kết thúc với giá trị trả về theo contract; trạng thái ngoài hàm chỉ thay đổi khi có side effect nêu ở trên.
- Verify command:
  - `Select-String -Path cogmem_api/engine/retain/fact_extraction.py -Pattern "def _extract_fallback_facts|async def _extract_fallback_facts"`

### Function: (module).extract_facts_from_contents
- Signature: `async extract_facts_from_contents(contents: list[RetainContent], llm_config, agent_name: str, config, pool=None, operation_id: str | None=None, schema: str | None=None) -> tuple[list[ExtractedFact], list[ChunkMetadata], TokenUsage]`
- Visibility: `public`
- Location: `cogmem_api/engine/retain/fact_extraction.py:781`
- Purpose:
  - Thực thi nghiệp vụ `extract_facts_from_contents` trong phạm vi `(module)` của module `cogmem_api/engine/retain/fact_extraction.py`.
- Inputs:
  - Theo chữ ký: `async extract_facts_from_contents(contents: list[RetainContent], llm_config, agent_name: str, config, pool=None, operation_id: str | None=None, schema: str | None=None) -> tuple[list[ExtractedFact], list[ChunkMetadata], TokenUsage]`.
- Outputs:
  - Trả về kiểu: `tuple[list[ExtractedFact], list[ChunkMetadata], TokenUsage]`.
- Side effects:
  - Không phát hiện side effect rõ ràng từ phân tích static call graph.
- Dependency calls:
  - `TokenUsage`, `bool`, `enumerate`, `getattr`, `_extract_fallback_facts`, `extend`, `append`, `_extract_seeded_facts`, `_extract_facts_with_llm`
- Failure modes:
  - Không phát hiện raise tường minh; lỗi có thể phát sinh từ dependency gọi bên trong.
- Pre-conditions:
  - Các tham số bắt buộc theo chữ ký phải hợp lệ kiểu dữ liệu trước khi gọi.
- Post-conditions:
  - Hàm kết thúc với giá trị trả về theo contract; trạng thái ngoài hàm chỉ thay đổi khi có side effect nêu ở trên.
- Verify command:
  - `Select-String -Path cogmem_api/engine/retain/fact_extraction.py -Pattern "def extract_facts_from_contents|async def extract_facts_from_contents"`

## Failure modes
- Inventory drift: hàm mới trong source nhưng chưa có deep-dive section tương ứng.
- Signature drift: refactor chữ ký hàm nhưng không cập nhật docs gây lệch contract.
- Verify command sai path hoặc sai tên hàm khiến khó truy vết nhanh trong review.

## Verify commands
- `uv run python tests/artifacts/test_task719_function_deep_dive.py`
- `Select-String -Path tutorials/functions/cogmem_api_engine_retain_fact_extraction.md -Pattern "### Function:"`
- `Select-String -Path tutorials/functions/cogmem_api_engine_retain_fact_extraction.md -Pattern "- Verify command:"`

