# Function Deep Dive - [cogmem_api/engine/search/types.py](https://github.com/triet4p/agent-memory-cognitive/blob/master/cogmem_api/engine/search/types.py)

## Purpose
- Mô tả chi tiết các hàm retrieval, fusion, reranking và routing của recall pipeline.
- Đảm bảo mọi hàm public/private trong module đều có contract docs phục vụ onboarding và traceability.

## Inputs
- Nguồn từ function inventory S18.1 (`tutorials/functions/function-inventory.json`).
- Chữ ký hàm, kiểu trả về, và vị trí dòng trong source module tương ứng.

## Outputs
- Tài liệu deep-dive cho 5 hàm/method trong module này.
- Mỗi hàm có purpose, inputs, outputs, side effects, dependency calls, failure modes, pre/post-conditions, verify command.

## Top-down level
- Function

## Prerequisites
- `tutorials/functions/function-inventory.md`
- `tutorials/module-map.md`
- Module dossier tương ứng trong `tutorials/modules/`

## Module responsibility
- Source module: `cogmem_api/engine/search/types.py`.
- Public/private breakdown: public=5, private=0.
- Bối cảnh chi tiết từng hàm nằm ở phần Function inventory bên dưới.

## Function inventory (public/private)
| Owner | Function | Visibility | Signature | Location | Deep-dive status |
|---|---|---|---|---|---|
| MergedCandidate | id | public | id(self) -> str | [cogmem_api/engine/search/types.py](https://github.com/triet4p/agent-memory-cognitive/blob/master/cogmem_api/engine/search/types.py):100 | documented |
| RetrievalResult | from_db_row | public | from_db_row(cls, row: dict[str, Any]) -> 'RetrievalResult' | [cogmem_api/engine/search/types.py](https://github.com/triet4p/agent-memory-cognitive/blob/master/cogmem_api/engine/search/types.py):60 | documented |
| ScoredResult | id | public | id(self) -> str | [cogmem_api/engine/search/types.py](https://github.com/triet4p/agent-memory-cognitive/blob/master/cogmem_api/engine/search/types.py):130 | documented |
| ScoredResult | retrieval | public | retrieval(self) -> RetrievalResult | [cogmem_api/engine/search/types.py](https://github.com/triet4p/agent-memory-cognitive/blob/master/cogmem_api/engine/search/types.py):135 | documented |
| ScoredResult | to_dict | public | to_dict(self) -> dict[str, Any] | [cogmem_api/engine/search/types.py](https://github.com/triet4p/agent-memory-cognitive/blob/master/cogmem_api/engine/search/types.py):139 | documented |

### Function: MergedCandidate.id
- Signature: `id(self) -> str`
- Visibility: `public`
- Location: `cogmem_api/engine/search/types.py:100`
- Purpose:
  - Thực thi nghiệp vụ `id` trong phạm vi `MergedCandidate` của module `cogmem_api/engine/search/types.py`.
- Inputs:
  - Theo chữ ký: `id(self) -> str`.
- Outputs:
  - Trả về kiểu: `str`.
- Side effects:
  - Không phát hiện side effect rõ ràng từ phân tích static call graph.
- Dependency calls:
  - Không phát hiện lời gọi hàm trực tiếp.
- Failure modes:
  - Không phát hiện raise tường minh; lỗi có thể phát sinh từ dependency gọi bên trong.
- Pre-conditions:
  - Các tham số bắt buộc theo chữ ký phải hợp lệ kiểu dữ liệu trước khi gọi.
- Post-conditions:
  - Hàm kết thúc với giá trị trả về theo contract; trạng thái ngoài hàm chỉ thay đổi khi có side effect nêu ở trên.
- Verify command:
  - `Select-String -Path cogmem_api/engine/search/types.py -Pattern "def id|async def id"`

### Function: RetrievalResult.from_db_row
- Signature: `from_db_row(cls, row: dict[str, Any]) -> 'RetrievalResult'`
- Visibility: `public`
- Location: `cogmem_api/engine/search/types.py:60`
- Purpose:
  - Thực thi nghiệp vụ `from_db_row` trong phạm vi `RetrievalResult` của module `cogmem_api/engine/search/types.py`.
- Inputs:
  - Theo chữ ký: `from_db_row(cls, row: dict[str, Any]) -> 'RetrievalResult'`.
- Outputs:
  - Trả về kiểu: `'RetrievalResult'`.
- Side effects:
  - Không phát hiện side effect rõ ràng từ phân tích static call graph.
- Dependency calls:
  - `cls`, `str`, `get`
- Failure modes:
  - Không phát hiện raise tường minh; lỗi có thể phát sinh từ dependency gọi bên trong.
- Pre-conditions:
  - Các tham số bắt buộc theo chữ ký phải hợp lệ kiểu dữ liệu trước khi gọi.
- Post-conditions:
  - Hàm kết thúc với giá trị trả về theo contract; trạng thái ngoài hàm chỉ thay đổi khi có side effect nêu ở trên.
- Verify command:
  - `Select-String -Path cogmem_api/engine/search/types.py -Pattern "def from_db_row|async def from_db_row"`

### Function: ScoredResult.id
- Signature: `id(self) -> str`
- Visibility: `public`
- Location: `cogmem_api/engine/search/types.py:130`
- Purpose:
  - Thực thi nghiệp vụ `id` trong phạm vi `ScoredResult` của module `cogmem_api/engine/search/types.py`.
- Inputs:
  - Theo chữ ký: `id(self) -> str`.
- Outputs:
  - Trả về kiểu: `str`.
- Side effects:
  - Không phát hiện side effect rõ ràng từ phân tích static call graph.
- Dependency calls:
  - Không phát hiện lời gọi hàm trực tiếp.
- Failure modes:
  - Không phát hiện raise tường minh; lỗi có thể phát sinh từ dependency gọi bên trong.
- Pre-conditions:
  - Các tham số bắt buộc theo chữ ký phải hợp lệ kiểu dữ liệu trước khi gọi.
- Post-conditions:
  - Hàm kết thúc với giá trị trả về theo contract; trạng thái ngoài hàm chỉ thay đổi khi có side effect nêu ở trên.
- Verify command:
  - `Select-String -Path cogmem_api/engine/search/types.py -Pattern "def id|async def id"`

### Function: ScoredResult.retrieval
- Signature: `retrieval(self) -> RetrievalResult`
- Visibility: `public`
- Location: `cogmem_api/engine/search/types.py:135`
- Purpose:
  - Thực thi nghiệp vụ `retrieval` trong phạm vi `ScoredResult` của module `cogmem_api/engine/search/types.py`.
- Inputs:
  - Theo chữ ký: `retrieval(self) -> RetrievalResult`.
- Outputs:
  - Trả về kiểu: `RetrievalResult`.
- Side effects:
  - Không phát hiện side effect rõ ràng từ phân tích static call graph.
- Dependency calls:
  - Không phát hiện lời gọi hàm trực tiếp.
- Failure modes:
  - Không phát hiện raise tường minh; lỗi có thể phát sinh từ dependency gọi bên trong.
- Pre-conditions:
  - Các tham số bắt buộc theo chữ ký phải hợp lệ kiểu dữ liệu trước khi gọi.
- Post-conditions:
  - Hàm kết thúc với giá trị trả về theo contract; trạng thái ngoài hàm chỉ thay đổi khi có side effect nêu ở trên.
- Verify command:
  - `Select-String -Path cogmem_api/engine/search/types.py -Pattern "def retrieval|async def retrieval"`

### Function: ScoredResult.to_dict
- Signature: `to_dict(self) -> dict[str, Any]`
- Visibility: `public`
- Location: `cogmem_api/engine/search/types.py:139`
- Purpose:
  - Thực thi nghiệp vụ `to_dict` trong phạm vi `ScoredResult` của module `cogmem_api/engine/search/types.py`.
- Inputs:
  - Theo chữ ký: `to_dict(self) -> dict[str, Any]`.
- Outputs:
  - Trả về kiểu: `dict[str, Any]`.
- Side effects:
  - Có khả năng tạo side effect qua call `update`.
- Dependency calls:
  - `update`
- Failure modes:
  - Không phát hiện raise tường minh; lỗi có thể phát sinh từ dependency gọi bên trong.
- Pre-conditions:
  - Các tham số bắt buộc theo chữ ký phải hợp lệ kiểu dữ liệu trước khi gọi.
- Post-conditions:
  - Hàm kết thúc với giá trị trả về theo contract; trạng thái ngoài hàm chỉ thay đổi khi có side effect nêu ở trên.
- Verify command:
  - `Select-String -Path cogmem_api/engine/search/types.py -Pattern "def to_dict|async def to_dict"`

## Failure modes
- Inventory drift: hàm mới trong source nhưng chưa có deep-dive section tương ứng.
- Signature drift: refactor chữ ký hàm nhưng không cập nhật docs gây lệch contract.
- Verify command sai path hoặc sai tên hàm khiến khó truy vết nhanh trong review.

## Verify commands
- `uv run python tests/artifacts/test_task719_function_deep_dive.py`
- `Select-String -Path tutorials/functions/cogmem_api_engine_search_types.md -Pattern "### Function:"`
- `Select-String -Path tutorials/functions/cogmem_api_engine_search_types.md -Pattern "- Verify command:"`

