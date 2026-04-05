# Function Deep Dive - [cogmem_api/engine/retain/types.py](https://github.com/triet4p/agent-memory-cognitive/blob/master/cogmem_api/engine/retain/types.py)

## Purpose
- Mô tả chi tiết các hàm ingestion/retain và chuẩn hóa dữ liệu trước khi ghi graph.
- Đảm bảo mọi hàm public/private trong module đều có contract docs phục vụ onboarding và traceability.

## Inputs
- Nguồn từ function inventory S18.1 (`tutorials/functions/function-inventory.json`).
- Chữ ký hàm, kiểu trả về, và vị trí dòng trong source module tương ứng.

## Outputs
- Tài liệu deep-dive cho 9 hàm/method trong module này.
- Mỗi hàm có purpose, inputs, outputs, side effects, dependency calls, failure modes, pre/post-conditions, verify command.

## Top-down level
- Function

## Prerequisites
- `tutorials/functions/function-inventory.md`
- `tutorials/module-map.md`
- Module dossier tương ứng trong `tutorials/modules/`

## Module responsibility
- Source module: `cogmem_api/engine/retain/types.py`.
- Public/private breakdown: public=7, private=2.
- Bối cảnh chi tiết từng hàm nằm ở phần Function inventory bên dưới.

## Function inventory (public/private)
| Owner | Function | Visibility | Signature | Location | Deep-dive status |
|---|---|---|---|---|---|
| (module) | coerce_fact_type | public | coerce_fact_type(raw: str \| None) -> str | [cogmem_api/engine/retain/types.py](https://github.com/triet4p/agent-memory-cognitive/blob/master/cogmem_api/engine/retain/types.py):32 | documented |
| (module) | clamp_relation_strength | public | clamp_relation_strength(value: Any, default: float=1.0) -> float | [cogmem_api/engine/retain/types.py](https://github.com/triet4p/agent-memory-cognitive/blob/master/cogmem_api/engine/retain/types.py):47 | documented |
| (module) | normalize_intention_status | public | normalize_intention_status(value: Any) -> str \| None | [cogmem_api/engine/retain/types.py](https://github.com/triet4p/agent-memory-cognitive/blob/master/cogmem_api/engine/retain/types.py):56 | documented |
| (module) | _normalize_bool | private | _normalize_bool(value: Any, default: bool) -> bool | [cogmem_api/engine/retain/types.py](https://github.com/triet4p/agent-memory-cognitive/blob/master/cogmem_api/engine/retain/types.py):70 | documented |
| (module) | sanitize_raw_snippet | public | sanitize_raw_snippet(raw_snippet: str \| None, fact_text: str) -> str | [cogmem_api/engine/retain/types.py](https://github.com/triet4p/agent-memory-cognitive/blob/master/cogmem_api/engine/retain/types.py):83 | documented |
| (module) | _build_edge_intent_payload | private | _build_edge_intent_payload(causal_relations: list[CausalRelation], action_effect_relations: list[ActionEffectRelation], transition_relations: list[TransitionRelation]) -> dict[str, list[dict[str, Any]]] | [cogmem_api/engine/retain/types.py](https://github.com/triet4p/agent-memory-cognitive/blob/master/cogmem_api/engine/retain/types.py):197 | documented |
| (module) | normalize_fact_metadata | public | normalize_fact_metadata(metadata: dict[str, object], *, fact_type: str, raw_snippet: str, causal_relations: list[CausalRelation], action_effect_relations: list[ActionEffectRelation], transition_relations: list[TransitionRelation]) -> dict[str, object] | [cogmem_api/engine/retain/types.py](https://github.com/triet4p/agent-memory-cognitive/blob/master/cogmem_api/engine/retain/types.py):230 | documented |
| ProcessedFact | from_extracted_fact | public | from_extracted_fact(extracted_fact: ExtractedFact, embedding: list[float]) -> 'ProcessedFact' | [cogmem_api/engine/retain/types.py](https://github.com/triet4p/agent-memory-cognitive/blob/master/cogmem_api/engine/retain/types.py):304 | documented |
| RetainContent | from_dict | public | from_dict(payload: RetainContentDict) -> 'RetainContent' | [cogmem_api/engine/retain/types.py](https://github.com/triet4p/agent-memory-cognitive/blob/master/cogmem_api/engine/retain/types.py):134 | documented |

### Function: (module).coerce_fact_type
- Signature: `coerce_fact_type(raw: str | None) -> str`
- Visibility: `public`
- Location: `cogmem_api/engine/retain/types.py:32`
- Purpose:
  - Thực thi nghiệp vụ `coerce_fact_type` trong phạm vi `(module)` của module `cogmem_api/engine/retain/types.py`.
- Inputs:
  - Theo chữ ký: `coerce_fact_type(raw: str | None) -> str`.
- Outputs:
  - Trả về kiểu: `str`.
- Side effects:
  - Không phát hiện side effect rõ ràng từ phân tích static call graph.
- Dependency calls:
  - `lower`, `strip`
- Failure modes:
  - Không phát hiện raise tường minh; lỗi có thể phát sinh từ dependency gọi bên trong.
- Pre-conditions:
  - Các tham số bắt buộc theo chữ ký phải hợp lệ kiểu dữ liệu trước khi gọi.
- Post-conditions:
  - Hàm kết thúc với giá trị trả về theo contract; trạng thái ngoài hàm chỉ thay đổi khi có side effect nêu ở trên.
- Verify command:
  - `Select-String -Path cogmem_api/engine/retain/types.py -Pattern "def coerce_fact_type|async def coerce_fact_type"`

### Function: (module).clamp_relation_strength
- Signature: `clamp_relation_strength(value: Any, default: float=1.0) -> float`
- Visibility: `public`
- Location: `cogmem_api/engine/retain/types.py:47`
- Purpose:
  - Thực thi nghiệp vụ `clamp_relation_strength` trong phạm vi `(module)` của module `cogmem_api/engine/retain/types.py`.
- Inputs:
  - Theo chữ ký: `clamp_relation_strength(value: Any, default: float=1.0) -> float`.
- Outputs:
  - Trả về kiểu: `float`.
- Side effects:
  - Không phát hiện side effect rõ ràng từ phân tích static call graph.
- Dependency calls:
  - `max`, `float`, `min`
- Failure modes:
  - Không phát hiện raise tường minh; lỗi có thể phát sinh từ dependency gọi bên trong.
- Pre-conditions:
  - Các tham số bắt buộc theo chữ ký phải hợp lệ kiểu dữ liệu trước khi gọi.
- Post-conditions:
  - Hàm kết thúc với giá trị trả về theo contract; trạng thái ngoài hàm chỉ thay đổi khi có side effect nêu ở trên.
- Verify command:
  - `Select-String -Path cogmem_api/engine/retain/types.py -Pattern "def clamp_relation_strength|async def clamp_relation_strength"`

### Function: (module).normalize_intention_status
- Signature: `normalize_intention_status(value: Any) -> str | None`
- Visibility: `public`
- Location: `cogmem_api/engine/retain/types.py:56`
- Purpose:
  - Thực thi nghiệp vụ `normalize_intention_status` trong phạm vi `(module)` của module `cogmem_api/engine/retain/types.py`.
- Inputs:
  - Theo chữ ký: `normalize_intention_status(value: Any) -> str | None`.
- Outputs:
  - Trả về kiểu: `str | None`.
- Side effects:
  - Không phát hiện side effect rõ ràng từ phân tích static call graph.
- Dependency calls:
  - `lower`, `isinstance`, `strip`
- Failure modes:
  - Không phát hiện raise tường minh; lỗi có thể phát sinh từ dependency gọi bên trong.
- Pre-conditions:
  - Các tham số bắt buộc theo chữ ký phải hợp lệ kiểu dữ liệu trước khi gọi.
- Post-conditions:
  - Hàm kết thúc với giá trị trả về theo contract; trạng thái ngoài hàm chỉ thay đổi khi có side effect nêu ở trên.
- Verify command:
  - `Select-String -Path cogmem_api/engine/retain/types.py -Pattern "def normalize_intention_status|async def normalize_intention_status"`

### Function: (module)._normalize_bool
- Signature: `_normalize_bool(value: Any, default: bool) -> bool`
- Visibility: `private`
- Location: `cogmem_api/engine/retain/types.py:70`
- Purpose:
  - Thực thi nghiệp vụ `_normalize_bool` trong phạm vi `(module)` của module `cogmem_api/engine/retain/types.py`.
- Inputs:
  - Theo chữ ký: `_normalize_bool(value: Any, default: bool) -> bool`.
- Outputs:
  - Trả về kiểu: `bool`.
- Side effects:
  - Không phát hiện side effect rõ ràng từ phân tích static call graph.
- Dependency calls:
  - `isinstance`, `lower`, `bool`, `strip`
- Failure modes:
  - Không phát hiện raise tường minh; lỗi có thể phát sinh từ dependency gọi bên trong.
- Pre-conditions:
  - Các tham số bắt buộc theo chữ ký phải hợp lệ kiểu dữ liệu trước khi gọi.
- Post-conditions:
  - Hàm kết thúc với giá trị trả về theo contract; trạng thái ngoài hàm chỉ thay đổi khi có side effect nêu ở trên.
- Verify command:
  - `Select-String -Path cogmem_api/engine/retain/types.py -Pattern "def _normalize_bool|async def _normalize_bool"`

### Function: (module).sanitize_raw_snippet
- Signature: `sanitize_raw_snippet(raw_snippet: str | None, fact_text: str) -> str`
- Visibility: `public`
- Location: `cogmem_api/engine/retain/types.py:83`
- Purpose:
  - Thực thi nghiệp vụ `sanitize_raw_snippet` trong phạm vi `(module)` của module `cogmem_api/engine/retain/types.py`.
- Inputs:
  - Theo chữ ký: `sanitize_raw_snippet(raw_snippet: str | None, fact_text: str) -> str`.
- Outputs:
  - Trả về kiểu: `str`.
- Side effects:
  - Không phát hiện side effect rõ ràng từ phân tích static call graph.
- Dependency calls:
  - `isinstance`, `strip`
- Failure modes:
  - Không phát hiện raise tường minh; lỗi có thể phát sinh từ dependency gọi bên trong.
- Pre-conditions:
  - Các tham số bắt buộc theo chữ ký phải hợp lệ kiểu dữ liệu trước khi gọi.
- Post-conditions:
  - Hàm kết thúc với giá trị trả về theo contract; trạng thái ngoài hàm chỉ thay đổi khi có side effect nêu ở trên.
- Verify command:
  - `Select-String -Path cogmem_api/engine/retain/types.py -Pattern "def sanitize_raw_snippet|async def sanitize_raw_snippet"`

### Function: (module)._build_edge_intent_payload
- Signature: `_build_edge_intent_payload(causal_relations: list[CausalRelation], action_effect_relations: list[ActionEffectRelation], transition_relations: list[TransitionRelation]) -> dict[str, list[dict[str, Any]]]`
- Visibility: `private`
- Location: `cogmem_api/engine/retain/types.py:197`
- Purpose:
  - Thực thi nghiệp vụ `_build_edge_intent_payload` trong phạm vi `(module)` của module `cogmem_api/engine/retain/types.py`.
- Inputs:
  - Theo chữ ký: `_build_edge_intent_payload(causal_relations: list[CausalRelation], action_effect_relations: list[ActionEffectRelation], transition_relations: list[TransitionRelation]) -> dict[str, list[dict[str, Any]]]`.
- Outputs:
  - Trả về kiểu: `dict[str, list[dict[str, Any]]]`.
- Side effects:
  - Không phát hiện side effect rõ ràng từ phân tích static call graph.
- Dependency calls:
  - `clamp_relation_strength`, `lower`, `strip`, `str`
- Failure modes:
  - Không phát hiện raise tường minh; lỗi có thể phát sinh từ dependency gọi bên trong.
- Pre-conditions:
  - Các tham số bắt buộc theo chữ ký phải hợp lệ kiểu dữ liệu trước khi gọi.
- Post-conditions:
  - Hàm kết thúc với giá trị trả về theo contract; trạng thái ngoài hàm chỉ thay đổi khi có side effect nêu ở trên.
- Verify command:
  - `Select-String -Path cogmem_api/engine/retain/types.py -Pattern "def _build_edge_intent_payload|async def _build_edge_intent_payload"`

### Function: (module).normalize_fact_metadata
- Signature: `normalize_fact_metadata(metadata: dict[str, object], *, fact_type: str, raw_snippet: str, causal_relations: list[CausalRelation], action_effect_relations: list[ActionEffectRelation], transition_relations: list[TransitionRelation]) -> dict[str, object]`
- Visibility: `public`
- Location: `cogmem_api/engine/retain/types.py:230`
- Purpose:
  - Thực thi nghiệp vụ `normalize_fact_metadata` trong phạm vi `(module)` của module `cogmem_api/engine/retain/types.py`.
- Inputs:
  - Theo chữ ký: `normalize_fact_metadata(metadata: dict[str, object], *, fact_type: str, raw_snippet: str, causal_relations: list[CausalRelation], action_effect_relations: list[ActionEffectRelation], transition_relations: list[TransitionRelation]) -> dict[str, object]`.
- Outputs:
  - Trả về kiểu: `dict[str, object]`.
- Side effects:
  - Không phát hiện side effect rõ ràng từ phân tích static call graph.
- Dependency calls:
  - `dict`, `_build_edge_intent_payload`, `bool`, `strip`, `normalize_intention_status`, `clamp_relation_strength`, `_normalize_bool`, `get`
- Failure modes:
  - Không phát hiện raise tường minh; lỗi có thể phát sinh từ dependency gọi bên trong.
- Pre-conditions:
  - Các tham số bắt buộc theo chữ ký phải hợp lệ kiểu dữ liệu trước khi gọi.
- Post-conditions:
  - Hàm kết thúc với giá trị trả về theo contract; trạng thái ngoài hàm chỉ thay đổi khi có side effect nêu ở trên.
- Verify command:
  - `Select-String -Path cogmem_api/engine/retain/types.py -Pattern "def normalize_fact_metadata|async def normalize_fact_metadata"`

### Function: ProcessedFact.from_extracted_fact
- Signature: `from_extracted_fact(extracted_fact: ExtractedFact, embedding: list[float]) -> 'ProcessedFact'`
- Visibility: `public`
- Location: `cogmem_api/engine/retain/types.py:304`
- Purpose:
  - Thực thi nghiệp vụ `from_extracted_fact` trong phạm vi `ProcessedFact` của module `cogmem_api/engine/retain/types.py`.
- Inputs:
  - Theo chữ ký: `from_extracted_fact(extracted_fact: ExtractedFact, embedding: list[float]) -> 'ProcessedFact'`.
- Outputs:
  - Trả về kiểu: `'ProcessedFact'`.
- Side effects:
  - Không phát hiện side effect rõ ràng từ phân tích static call graph.
- Dependency calls:
  - `coerce_fact_type`, `sanitize_raw_snippet`, `normalize_fact_metadata`, `ProcessedFact`, `CausalRelation`, `ActionEffectRelation`, `TransitionRelation`, `strip`, `list`, `clamp_relation_strength`, `lower`, `str`
- Failure modes:
  - Không phát hiện raise tường minh; lỗi có thể phát sinh từ dependency gọi bên trong.
- Pre-conditions:
  - Các tham số bắt buộc theo chữ ký phải hợp lệ kiểu dữ liệu trước khi gọi.
- Post-conditions:
  - Hàm kết thúc với giá trị trả về theo contract; trạng thái ngoài hàm chỉ thay đổi khi có side effect nêu ở trên.
- Verify command:
  - `Select-String -Path cogmem_api/engine/retain/types.py -Pattern "def from_extracted_fact|async def from_extracted_fact"`

### Function: RetainContent.from_dict
- Signature: `from_dict(payload: RetainContentDict) -> 'RetainContent'`
- Visibility: `public`
- Location: `cogmem_api/engine/retain/types.py:134`
- Purpose:
  - Thực thi nghiệp vụ `from_dict` trong phạm vi `RetainContent` của module `cogmem_api/engine/retain/types.py`.
- Inputs:
  - Theo chữ ký: `from_dict(payload: RetainContentDict) -> 'RetainContent'`.
- Outputs:
  - Trả về kiểu: `'RetainContent'`.
- Side effects:
  - Không phát hiện side effect rõ ràng từ phân tích static call graph.
- Dependency calls:
  - `get`, `isinstance`, `RetainContent`, `replace`, `fromisoformat`, `dict`, `list`, `TypeError`, `type`
- Failure modes:
  - Có thể raise: `TypeError`.
- Pre-conditions:
  - Các tham số bắt buộc theo chữ ký phải hợp lệ kiểu dữ liệu trước khi gọi.
- Post-conditions:
  - Hàm kết thúc với giá trị trả về theo contract; trạng thái ngoài hàm chỉ thay đổi khi có side effect nêu ở trên.
- Verify command:
  - `Select-String -Path cogmem_api/engine/retain/types.py -Pattern "def from_dict|async def from_dict"`

## Failure modes
- Inventory drift: hàm mới trong source nhưng chưa có deep-dive section tương ứng.
- Signature drift: refactor chữ ký hàm nhưng không cập nhật docs gây lệch contract.
- Verify command sai path hoặc sai tên hàm khiến khó truy vết nhanh trong review.

## Verify commands
- `uv run python tests/artifacts/test_task719_function_deep_dive.py`
- `Select-String -Path tutorials/functions/cogmem_api_engine_retain_types.md -Pattern "### Function:"`
- `Select-String -Path tutorials/functions/cogmem_api_engine_retain_types.md -Pattern "- Verify command:"`

