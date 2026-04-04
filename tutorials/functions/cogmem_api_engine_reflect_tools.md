# Function Deep Dive - cogmem_api/engine/reflect/tools.py

## Purpose
- Mô tả chi tiết các hàm lazy synthesis và chuẩn hóa evidence cho bước phản hồi.
- Đảm bảo mọi hàm public/private trong module đều có contract docs phục vụ onboarding và traceability.

## Inputs
- Nguồn từ function inventory S18.1 (`tutorials/functions/function-inventory.json`).
- Chữ ký hàm, kiểu trả về, và vị trí dòng trong source module tương ứng.

## Outputs
- Tài liệu deep-dive cho 6 hàm/method trong module này.
- Mỗi hàm có purpose, inputs, outputs, side effects, dependency calls, failure modes, pre/post-conditions, verify command.

## Top-down level
- Function

## Prerequisites
- `tutorials/functions/function-inventory.md`
- `tutorials/module-map.md`
- Module dossier tương ứng trong `tutorials/modules/`

## Module responsibility
- Source module: `cogmem_api/engine/reflect/tools.py`.
- Public/private breakdown: public=3, private=3.
- Bối cảnh chi tiết từng hàm nằm ở phần Function inventory bên dưới.

## Function inventory (public/private)
| Owner | Function | Visibility | Signature | Location | Deep-dive status |
|---|---|---|---|---|---|
| (module) | _coerce_score | private | _coerce_score(payload: dict[str, Any]) -> float | cogmem_api/engine/reflect/tools.py:16 | documented |
| (module) | _coerce_datetime | private | _coerce_datetime(payload: dict[str, Any]) -> datetime \| None | cogmem_api/engine/reflect/tools.py:24 | documented |
| (module) | _normalize_payload | private | _normalize_payload(item: RetrievalResult \| MergedCandidate \| dict[str, Any], source: str \| None) -> dict[str, Any] | cogmem_api/engine/reflect/tools.py:31 | documented |
| (module) | to_reflect_evidence | public | to_reflect_evidence(item: RetrievalResult \| MergedCandidate \| dict[str, Any], source: str \| None=None) -> ReflectEvidence \| None | cogmem_api/engine/reflect/tools.py:64 | documented |
| (module) | prepare_lazy_evidence | public | prepare_lazy_evidence(items: list[RetrievalResult \| MergedCandidate \| dict[str, Any]], max_items: int=8) -> list[ReflectEvidence] | cogmem_api/engine/reflect/tools.py:94 | documented |
| (module) | group_evidence_by_network | public | group_evidence_by_network(evidences: list[ReflectEvidence]) -> dict[str, list[ReflectEvidence]] | cogmem_api/engine/reflect/tools.py:119 | documented |

### Function: (module)._coerce_score
- Signature: `_coerce_score(payload: dict[str, Any]) -> float`
- Visibility: `private`
- Location: `cogmem_api/engine/reflect/tools.py:16`
- Purpose:
  - Thực thi nghiệp vụ `_coerce_score` trong phạm vi `(module)` của module `cogmem_api/engine/reflect/tools.py`.
- Inputs:
  - Theo chữ ký: `_coerce_score(payload: dict[str, Any]) -> float`.
- Outputs:
  - Trả về kiểu: `float`.
- Side effects:
  - Không phát hiện side effect rõ ràng từ phân tích static call graph.
- Dependency calls:
  - `get`, `isinstance`, `float`
- Failure modes:
  - Không phát hiện raise tường minh; lỗi có thể phát sinh từ dependency gọi bên trong.
- Pre-conditions:
  - Các tham số bắt buộc theo chữ ký phải hợp lệ kiểu dữ liệu trước khi gọi.
- Post-conditions:
  - Hàm kết thúc với giá trị trả về theo contract; trạng thái ngoài hàm chỉ thay đổi khi có side effect nêu ở trên.
- Verify command:
  - `Select-String -Path cogmem_api/engine/reflect/tools.py -Pattern "def _coerce_score|async def _coerce_score"`

### Function: (module)._coerce_datetime
- Signature: `_coerce_datetime(payload: dict[str, Any]) -> datetime | None`
- Visibility: `private`
- Location: `cogmem_api/engine/reflect/tools.py:24`
- Purpose:
  - Thực thi nghiệp vụ `_coerce_datetime` trong phạm vi `(module)` của module `cogmem_api/engine/reflect/tools.py`.
- Inputs:
  - Theo chữ ký: `_coerce_datetime(payload: dict[str, Any]) -> datetime | None`.
- Outputs:
  - Trả về kiểu: `datetime | None`.
- Side effects:
  - Không phát hiện side effect rõ ràng từ phân tích static call graph.
- Dependency calls:
  - `isinstance`, `get`
- Failure modes:
  - Không phát hiện raise tường minh; lỗi có thể phát sinh từ dependency gọi bên trong.
- Pre-conditions:
  - Các tham số bắt buộc theo chữ ký phải hợp lệ kiểu dữ liệu trước khi gọi.
- Post-conditions:
  - Hàm kết thúc với giá trị trả về theo contract; trạng thái ngoài hàm chỉ thay đổi khi có side effect nêu ở trên.
- Verify command:
  - `Select-String -Path cogmem_api/engine/reflect/tools.py -Pattern "def _coerce_datetime|async def _coerce_datetime"`

### Function: (module)._normalize_payload
- Signature: `_normalize_payload(item: RetrievalResult | MergedCandidate | dict[str, Any], source: str | None) -> dict[str, Any]`
- Visibility: `private`
- Location: `cogmem_api/engine/reflect/tools.py:31`
- Purpose:
  - Thực thi nghiệp vụ `_normalize_payload` trong phạm vi `(module)` của module `cogmem_api/engine/reflect/tools.py`.
- Inputs:
  - Theo chữ ký: `_normalize_payload(item: RetrievalResult | MergedCandidate | dict[str, Any], source: str | None) -> dict[str, Any]`.
- Outputs:
  - Trả về kiểu: `dict[str, Any]`.
- Side effects:
  - Không phát hiện side effect rõ ràng từ phân tích static call graph.
- Dependency calls:
  - `isinstance`, `dict`, `str`, `get`
- Failure modes:
  - Không phát hiện raise tường minh; lỗi có thể phát sinh từ dependency gọi bên trong.
- Pre-conditions:
  - Các tham số bắt buộc theo chữ ký phải hợp lệ kiểu dữ liệu trước khi gọi.
- Post-conditions:
  - Hàm kết thúc với giá trị trả về theo contract; trạng thái ngoài hàm chỉ thay đổi khi có side effect nêu ở trên.
- Verify command:
  - `Select-String -Path cogmem_api/engine/reflect/tools.py -Pattern "def _normalize_payload|async def _normalize_payload"`

### Function: (module).to_reflect_evidence
- Signature: `to_reflect_evidence(item: RetrievalResult | MergedCandidate | dict[str, Any], source: str | None=None) -> ReflectEvidence | None`
- Visibility: `public`
- Location: `cogmem_api/engine/reflect/tools.py:64`
- Purpose:
  - Thực thi nghiệp vụ `to_reflect_evidence` trong phạm vi `(module)` của module `cogmem_api/engine/reflect/tools.py`.
- Inputs:
  - Theo chữ ký: `to_reflect_evidence(item: RetrievalResult | MergedCandidate | dict[str, Any], source: str | None=None) -> ReflectEvidence | None`.
- Outputs:
  - Trả về kiểu: `ReflectEvidence | None`.
- Side effects:
  - Không phát hiện side effect rõ ràng từ phân tích static call graph.
- Dependency calls:
  - `_normalize_payload`, `strip`, `get`, `ReflectEvidence`, `str`, `_coerce_score`, `_coerce_datetime`
- Failure modes:
  - Không phát hiện raise tường minh; lỗi có thể phát sinh từ dependency gọi bên trong.
- Pre-conditions:
  - Các tham số bắt buộc theo chữ ký phải hợp lệ kiểu dữ liệu trước khi gọi.
- Post-conditions:
  - Hàm kết thúc với giá trị trả về theo contract; trạng thái ngoài hàm chỉ thay đổi khi có side effect nêu ở trên.
- Verify command:
  - `Select-String -Path cogmem_api/engine/reflect/tools.py -Pattern "def to_reflect_evidence|async def to_reflect_evidence"`

### Function: (module).prepare_lazy_evidence
- Signature: `prepare_lazy_evidence(items: list[RetrievalResult | MergedCandidate | dict[str, Any]], max_items: int=8) -> list[ReflectEvidence]`
- Visibility: `public`
- Location: `cogmem_api/engine/reflect/tools.py:94`
- Purpose:
  - Thực thi nghiệp vụ `prepare_lazy_evidence` trong phạm vi `(module)` của module `cogmem_api/engine/reflect/tools.py`.
- Inputs:
  - Theo chữ ký: `prepare_lazy_evidence(items: list[RetrievalResult | MergedCandidate | dict[str, Any]], max_items: int=8) -> list[ReflectEvidence]`.
- Outputs:
  - Trả về kiểu: `list[ReflectEvidence]`.
- Side effects:
  - Không phát hiện side effect rõ ràng từ phân tích static call graph.
- Dependency calls:
  - `sorted`, `to_reflect_evidence`, `get`, `values`, `max`, `timestamp`, `float`
- Failure modes:
  - Không phát hiện raise tường minh; lỗi có thể phát sinh từ dependency gọi bên trong.
- Pre-conditions:
  - Các tham số bắt buộc theo chữ ký phải hợp lệ kiểu dữ liệu trước khi gọi.
- Post-conditions:
  - Hàm kết thúc với giá trị trả về theo contract; trạng thái ngoài hàm chỉ thay đổi khi có side effect nêu ở trên.
- Verify command:
  - `Select-String -Path cogmem_api/engine/reflect/tools.py -Pattern "def prepare_lazy_evidence|async def prepare_lazy_evidence"`

### Function: (module).group_evidence_by_network
- Signature: `group_evidence_by_network(evidences: list[ReflectEvidence]) -> dict[str, list[ReflectEvidence]]`
- Visibility: `public`
- Location: `cogmem_api/engine/reflect/tools.py:119`
- Purpose:
  - Thực thi nghiệp vụ `group_evidence_by_network` trong phạm vi `(module)` của module `cogmem_api/engine/reflect/tools.py`.
- Inputs:
  - Theo chữ ký: `group_evidence_by_network(evidences: list[ReflectEvidence]) -> dict[str, list[ReflectEvidence]]`.
- Outputs:
  - Trả về kiểu: `dict[str, list[ReflectEvidence]]`.
- Side effects:
  - Không phát hiện side effect rõ ràng từ phân tích static call graph.
- Dependency calls:
  - `defaultdict`, `dict`, `append`
- Failure modes:
  - Không phát hiện raise tường minh; lỗi có thể phát sinh từ dependency gọi bên trong.
- Pre-conditions:
  - Các tham số bắt buộc theo chữ ký phải hợp lệ kiểu dữ liệu trước khi gọi.
- Post-conditions:
  - Hàm kết thúc với giá trị trả về theo contract; trạng thái ngoài hàm chỉ thay đổi khi có side effect nêu ở trên.
- Verify command:
  - `Select-String -Path cogmem_api/engine/reflect/tools.py -Pattern "def group_evidence_by_network|async def group_evidence_by_network"`

## Failure modes
- Inventory drift: hàm mới trong source nhưng chưa có deep-dive section tương ứng.
- Signature drift: refactor chữ ký hàm nhưng không cập nhật docs gây lệch contract.
- Verify command sai path hoặc sai tên hàm khiến khó truy vết nhanh trong review.

## Verify commands
- `uv run python tests/artifacts/test_task719_function_deep_dive.py`
- `Select-String -Path tutorials/functions/cogmem_api_engine_reflect_tools.md -Pattern "### Function:"`
- `Select-String -Path tutorials/functions/cogmem_api_engine_reflect_tools.md -Pattern "- Verify command:"`

