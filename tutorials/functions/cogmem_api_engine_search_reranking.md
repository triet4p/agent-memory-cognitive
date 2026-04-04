# Function Deep Dive - cogmem_api/engine/search/reranking.py

## Purpose
- Mô tả chi tiết các hàm retrieval, fusion, reranking và routing của recall pipeline.
- Đảm bảo mọi hàm public/private trong module đều có contract docs phục vụ onboarding và traceability.

## Inputs
- Nguồn từ function inventory S18.1 (`tutorials/functions/function-inventory.json`).
- Chữ ký hàm, kiểu trả về, và vị trí dòng trong source module tương ứng.

## Outputs
- Tài liệu deep-dive cho 4 hàm/method trong module này.
- Mỗi hàm có purpose, inputs, outputs, side effects, dependency calls, failure modes, pre/post-conditions, verify command.

## Top-down level
- Function

## Prerequisites
- `tutorials/functions/function-inventory.md`
- `tutorials/module-map.md`
- Module dossier tương ứng trong `tutorials/modules/`

## Module responsibility
- Source module: `cogmem_api/engine/search/reranking.py`.
- Public/private breakdown: public=3, private=1.
- Bối cảnh chi tiết từng hàm nằm ở phần Function inventory bên dưới.

## Function inventory (public/private)
| Owner | Function | Visibility | Signature | Location | Deep-dive status |
|---|---|---|---|---|---|
| (module) | apply_combined_scoring | public | apply_combined_scoring(scored_results: list[ScoredResult], now: datetime, recency_alpha: float=_RECENCY_ALPHA, temporal_alpha: float=_TEMPORAL_ALPHA) -> None | cogmem_api/engine/search/reranking.py:19 | documented |
| CrossEncoderReranker | __init__ | private | __init__(self, cross_encoder=None) | cogmem_api/engine/search/reranking.py:81 | documented |
| CrossEncoderReranker | ensure_initialized | public | async ensure_initialized(self) | cogmem_api/engine/search/reranking.py:96 | documented |
| CrossEncoderReranker | rerank | public | async rerank(self, query: str, candidates: list[MergedCandidate]) -> list[ScoredResult] | cogmem_api/engine/search/reranking.py:104 | documented |

### Function: (module).apply_combined_scoring
- Signature: `apply_combined_scoring(scored_results: list[ScoredResult], now: datetime, recency_alpha: float=_RECENCY_ALPHA, temporal_alpha: float=_TEMPORAL_ALPHA) -> None`
- Visibility: `public`
- Location: `cogmem_api/engine/search/reranking.py:19`
- Purpose:
  - Thực thi nghiệp vụ `apply_combined_scoring` trong phạm vi `(module)` của module `cogmem_api/engine/search/reranking.py`.
- Inputs:
  - Theo chữ ký: `apply_combined_scoring(scored_results: list[ScoredResult], now: datetime, recency_alpha: float=_RECENCY_ALPHA, temporal_alpha: float=_TEMPORAL_ALPHA) -> None`.
- Outputs:
  - Trả về kiểu: `None`.
- Side effects:
  - Không phát hiện side effect rõ ràng từ phân tích static call graph.
- Dependency calls:
  - `replace`, `max`, `total_seconds`, `min`
- Failure modes:
  - Không phát hiện raise tường minh; lỗi có thể phát sinh từ dependency gọi bên trong.
- Pre-conditions:
  - Các tham số bắt buộc theo chữ ký phải hợp lệ kiểu dữ liệu trước khi gọi.
- Post-conditions:
  - Hàm kết thúc với giá trị trả về theo contract; trạng thái ngoài hàm chỉ thay đổi khi có side effect nêu ở trên.
- Verify command:
  - `Select-String -Path cogmem_api/engine/search/reranking.py -Pattern "def apply_combined_scoring|async def apply_combined_scoring"`

### Function: CrossEncoderReranker.__init__
- Signature: `__init__(self, cross_encoder=None)`
- Visibility: `private`
- Location: `cogmem_api/engine/search/reranking.py:81`
- Purpose:
  - Thực thi nghiệp vụ `__init__` trong phạm vi `CrossEncoderReranker` của module `cogmem_api/engine/search/reranking.py`.
- Inputs:
  - Theo chữ ký: `__init__(self, cross_encoder=None)`.
- Outputs:
  - Không khai báo kiểu trả về tường minh; hành vi phụ thuộc implementation.
- Side effects:
  - Không phát hiện side effect rõ ràng từ phân tích static call graph.
- Dependency calls:
  - `create_cross_encoder_from_env`
- Failure modes:
  - Không phát hiện raise tường minh; lỗi có thể phát sinh từ dependency gọi bên trong.
- Pre-conditions:
  - Các tham số bắt buộc theo chữ ký phải hợp lệ kiểu dữ liệu trước khi gọi.
- Post-conditions:
  - Hàm kết thúc với giá trị trả về theo contract; trạng thái ngoài hàm chỉ thay đổi khi có side effect nêu ở trên.
- Verify command:
  - `Select-String -Path cogmem_api/engine/search/reranking.py -Pattern "def __init__|async def __init__"`

### Function: CrossEncoderReranker.ensure_initialized
- Signature: `async ensure_initialized(self)`
- Visibility: `public`
- Location: `cogmem_api/engine/search/reranking.py:96`
- Purpose:
  - Thực thi nghiệp vụ `ensure_initialized` trong phạm vi `CrossEncoderReranker` của module `cogmem_api/engine/search/reranking.py`.
- Inputs:
  - Theo chữ ký: `async ensure_initialized(self)`.
- Outputs:
  - Không khai báo kiểu trả về tường minh; hành vi phụ thuộc implementation.
- Side effects:
  - Không phát hiện side effect rõ ràng từ phân tích static call graph.
- Dependency calls:
  - `initialize`
- Failure modes:
  - Không phát hiện raise tường minh; lỗi có thể phát sinh từ dependency gọi bên trong.
- Pre-conditions:
  - Các tham số bắt buộc theo chữ ký phải hợp lệ kiểu dữ liệu trước khi gọi.
- Post-conditions:
  - Hàm kết thúc với giá trị trả về theo contract; trạng thái ngoài hàm chỉ thay đổi khi có side effect nêu ở trên.
- Verify command:
  - `Select-String -Path cogmem_api/engine/search/reranking.py -Pattern "def ensure_initialized|async def ensure_initialized"`

### Function: CrossEncoderReranker.rerank
- Signature: `async rerank(self, query: str, candidates: list[MergedCandidate]) -> list[ScoredResult]`
- Visibility: `public`
- Location: `cogmem_api/engine/search/reranking.py:104`
- Purpose:
  - Thực thi nghiệp vụ `rerank` trong phạm vi `CrossEncoderReranker` của module `cogmem_api/engine/search/reranking.py`.
- Inputs:
  - Theo chữ ký: `async rerank(self, query: str, candidates: list[MergedCandidate]) -> list[ScoredResult]`.
- Outputs:
  - Trả về kiểu: `list[ScoredResult]`.
- Side effects:
  - Không phát hiện side effect rõ ràng từ phân tích static call graph.
- Dependency calls:
  - `zip`, `sort`, `append`, `predict`, `sigmoid`, `ScoredResult`, `strftime`, `exp`, `float`
- Failure modes:
  - Không phát hiện raise tường minh; lỗi có thể phát sinh từ dependency gọi bên trong.
- Pre-conditions:
  - Các tham số bắt buộc theo chữ ký phải hợp lệ kiểu dữ liệu trước khi gọi.
- Post-conditions:
  - Hàm kết thúc với giá trị trả về theo contract; trạng thái ngoài hàm chỉ thay đổi khi có side effect nêu ở trên.
- Verify command:
  - `Select-String -Path cogmem_api/engine/search/reranking.py -Pattern "def rerank|async def rerank"`

## Failure modes
- Inventory drift: hàm mới trong source nhưng chưa có deep-dive section tương ứng.
- Signature drift: refactor chữ ký hàm nhưng không cập nhật docs gây lệch contract.
- Verify command sai path hoặc sai tên hàm khiến khó truy vết nhanh trong review.

## Verify commands
- `uv run python tests/artifacts/test_task719_function_deep_dive.py`
- `Select-String -Path tutorials/functions/cogmem_api_engine_search_reranking.md -Pattern "### Function:"`
- `Select-String -Path tutorials/functions/cogmem_api_engine_search_reranking.md -Pattern "- Verify command:"`

