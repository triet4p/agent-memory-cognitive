# Function Deep Dive - [cogmem_api/engine/search/fusion.py](https://github.com/triet4p/agent-memory-cognitive/blob/master/cogmem_api/engine/search/fusion.py)

## Purpose
- Mô tả chi tiết các hàm retrieval, fusion, reranking và routing của recall pipeline.
- Đảm bảo mọi hàm public/private trong module đều có contract docs phục vụ onboarding và traceability.

## Inputs
- Nguồn từ function inventory S18.1 (`tutorials/functions/function-inventory.json`).
- Chữ ký hàm, kiểu trả về, và vị trí dòng trong source module tương ứng.

## Outputs
- Tài liệu deep-dive cho 3 hàm/method trong module này.
- Mỗi hàm có purpose, inputs, outputs, side effects, dependency calls, failure modes, pre/post-conditions, verify command.

## Top-down level
- Function

## Prerequisites
- `tutorials/functions/function-inventory.md`
- `tutorials/module-map.md`
- Module dossier tương ứng trong `tutorials/modules/`

## Module responsibility
- Source module: `cogmem_api/engine/search/fusion.py`.
- Public/private breakdown: public=3, private=0.
- Bối cảnh chi tiết từng hàm nằm ở phần Function inventory bên dưới.

## Function inventory (public/private)
| Owner | Function | Visibility | Signature | Location | Deep-dive status |
|---|---|---|---|---|---|
| (module) | weighted_reciprocal_rank_fusion | public | weighted_reciprocal_rank_fusion(result_lists: list[list[RetrievalResult]], source_weights: dict[str, float] \| None=None, k: int=60, source_names: list[str] \| None=None) -> list[MergedCandidate] | [cogmem_api/engine/search/fusion.py](https://github.com/triet4p/agent-memory-cognitive/blob/master/cogmem_api/engine/search/fusion.py):10 | documented |
| (module) | reciprocal_rank_fusion | public | reciprocal_rank_fusion(result_lists: list[list[RetrievalResult]], k: int=60) -> list[MergedCandidate] | [cogmem_api/engine/search/fusion.py](https://github.com/triet4p/agent-memory-cognitive/blob/master/cogmem_api/engine/search/fusion.py):85 | documented |
| (module) | normalize_scores_on_deltas | public | normalize_scores_on_deltas(results: list[dict[str, Any]], score_keys: list[str]) -> list[dict[str, Any]] | [cogmem_api/engine/search/fusion.py](https://github.com/triet4p/agent-memory-cognitive/blob/master/cogmem_api/engine/search/fusion.py):109 | documented |

### Function: (module).weighted_reciprocal_rank_fusion
- Signature: `weighted_reciprocal_rank_fusion(result_lists: list[list[RetrievalResult]], source_weights: dict[str, float] | None=None, k: int=60, source_names: list[str] | None=None) -> list[MergedCandidate]`
- Visibility: `public`
- Location: `cogmem_api/engine/search/fusion.py:10`
- Purpose:
  - Thực thi nghiệp vụ `weighted_reciprocal_rank_fusion` trong phạm vi `(module)` của module `cogmem_api/engine/search/fusion.py`.
- Inputs:
  - Theo chữ ký: `weighted_reciprocal_rank_fusion(result_lists: list[list[RetrievalResult]], source_weights: dict[str, float] | None=None, k: int=60, source_names: list[str] | None=None) -> list[MergedCandidate]`.
- Outputs:
  - Trả về kiểu: `list[MergedCandidate]`.
- Side effects:
  - Không phát hiện side effect rõ ràng từ phân tích static call graph.
- Dependency calls:
  - `enumerate`, `max`, `sorted`, `MergedCandidate`, `append`, `float`, `isinstance`, `items`, `len`, `get`, `TypeError`, `type`
- Failure modes:
  - Có thể raise: `TypeError`.
- Pre-conditions:
  - Các tham số bắt buộc theo chữ ký phải hợp lệ kiểu dữ liệu trước khi gọi.
- Post-conditions:
  - Hàm kết thúc với giá trị trả về theo contract; trạng thái ngoài hàm chỉ thay đổi khi có side effect nêu ở trên.
- Verify command:
  - `Select-String -Path cogmem_api/engine/search/fusion.py -Pattern "def weighted_reciprocal_rank_fusion|async def weighted_reciprocal_rank_fusion"`

### Function: (module).reciprocal_rank_fusion
- Signature: `reciprocal_rank_fusion(result_lists: list[list[RetrievalResult]], k: int=60) -> list[MergedCandidate]`
- Visibility: `public`
- Location: `cogmem_api/engine/search/fusion.py:85`
- Purpose:
  - Thực thi nghiệp vụ `reciprocal_rank_fusion` trong phạm vi `(module)` của module `cogmem_api/engine/search/fusion.py`.
- Inputs:
  - Theo chữ ký: `reciprocal_rank_fusion(result_lists: list[list[RetrievalResult]], k: int=60) -> list[MergedCandidate]`.
- Outputs:
  - Trả về kiểu: `list[MergedCandidate]`.
- Side effects:
  - Không phát hiện side effect rõ ràng từ phân tích static call graph.
- Dependency calls:
  - `weighted_reciprocal_rank_fusion`
- Failure modes:
  - Không phát hiện raise tường minh; lỗi có thể phát sinh từ dependency gọi bên trong.
- Pre-conditions:
  - Các tham số bắt buộc theo chữ ký phải hợp lệ kiểu dữ liệu trước khi gọi.
- Post-conditions:
  - Hàm kết thúc với giá trị trả về theo contract; trạng thái ngoài hàm chỉ thay đổi khi có side effect nêu ở trên.
- Verify command:
  - `Select-String -Path cogmem_api/engine/search/fusion.py -Pattern "def reciprocal_rank_fusion|async def reciprocal_rank_fusion"`

### Function: (module).normalize_scores_on_deltas
- Signature: `normalize_scores_on_deltas(results: list[dict[str, Any]], score_keys: list[str]) -> list[dict[str, Any]]`
- Visibility: `public`
- Location: `cogmem_api/engine/search/fusion.py:109`
- Purpose:
  - Thực thi nghiệp vụ `normalize_scores_on_deltas` trong phạm vi `(module)` của module `cogmem_api/engine/search/fusion.py`.
- Inputs:
  - Theo chữ ký: `normalize_scores_on_deltas(results: list[dict[str, Any]], score_keys: list[str]) -> list[dict[str, Any]]`.
- Outputs:
  - Trả về kiểu: `list[dict[str, Any]]`.
- Side effects:
  - Không phát hiện side effect rõ ràng từ phân tích static call graph.
- Dependency calls:
  - `min`, `max`, `get`
- Failure modes:
  - Không phát hiện raise tường minh; lỗi có thể phát sinh từ dependency gọi bên trong.
- Pre-conditions:
  - Các tham số bắt buộc theo chữ ký phải hợp lệ kiểu dữ liệu trước khi gọi.
- Post-conditions:
  - Hàm kết thúc với giá trị trả về theo contract; trạng thái ngoài hàm chỉ thay đổi khi có side effect nêu ở trên.
- Verify command:
  - `Select-String -Path cogmem_api/engine/search/fusion.py -Pattern "def normalize_scores_on_deltas|async def normalize_scores_on_deltas"`

## Failure modes
- Inventory drift: hàm mới trong source nhưng chưa có deep-dive section tương ứng.
- Signature drift: refactor chữ ký hàm nhưng không cập nhật docs gây lệch contract.
- Verify command sai path hoặc sai tên hàm khiến khó truy vết nhanh trong review.

## Verify commands
- `uv run python tests/artifacts/test_task719_function_deep_dive.py`
- `Select-String -Path tutorials/functions/cogmem_api_engine_search_fusion.md -Pattern "### Function:"`
- `Select-String -Path tutorials/functions/cogmem_api_engine_search_fusion.md -Pattern "- Verify command:"`

