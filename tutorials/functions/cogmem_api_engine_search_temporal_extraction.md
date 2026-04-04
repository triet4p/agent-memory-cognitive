# Function Deep Dive - cogmem_api/engine/search/temporal_extraction.py

## Purpose
- Mô tả chi tiết các hàm retrieval, fusion, reranking và routing của recall pipeline.
- Đảm bảo mọi hàm public/private trong module đều có contract docs phục vụ onboarding và traceability.

## Inputs
- Nguồn từ function inventory S18.1 (`tutorials/functions/function-inventory.json`).
- Chữ ký hàm, kiểu trả về, và vị trí dòng trong source module tương ứng.

## Outputs
- Tài liệu deep-dive cho 2 hàm/method trong module này.
- Mỗi hàm có purpose, inputs, outputs, side effects, dependency calls, failure modes, pre/post-conditions, verify command.

## Top-down level
- Function

## Prerequisites
- `tutorials/functions/function-inventory.md`
- `tutorials/module-map.md`
- Module dossier tương ứng trong `tutorials/modules/`

## Module responsibility
- Source module: `cogmem_api/engine/search/temporal_extraction.py`.
- Public/private breakdown: public=2, private=0.
- Bối cảnh chi tiết từng hàm nằm ở phần Function inventory bên dưới.

## Function inventory (public/private)
| Owner | Function | Visibility | Signature | Location | Deep-dive status |
|---|---|---|---|---|---|
| (module) | get_default_analyzer | public | get_default_analyzer() -> QueryAnalyzer | cogmem_api/engine/search/temporal_extraction.py:19 | documented |
| (module) | extract_temporal_constraint | public | extract_temporal_constraint(query: str, reference_date: datetime \| None=None, analyzer: QueryAnalyzer \| None=None) -> tuple[datetime, datetime] \| None | cogmem_api/engine/search/temporal_extraction.py:34 | documented |

### Function: (module).get_default_analyzer
- Signature: `get_default_analyzer() -> QueryAnalyzer`
- Visibility: `public`
- Location: `cogmem_api/engine/search/temporal_extraction.py:19`
- Purpose:
  - Thực thi nghiệp vụ `get_default_analyzer` trong phạm vi `(module)` của module `cogmem_api/engine/search/temporal_extraction.py`.
- Inputs:
  - Theo chữ ký: `get_default_analyzer() -> QueryAnalyzer`.
- Outputs:
  - Trả về kiểu: `QueryAnalyzer`.
- Side effects:
  - Không phát hiện side effect rõ ràng từ phân tích static call graph.
- Dependency calls:
  - `DateparserQueryAnalyzer`
- Failure modes:
  - Không phát hiện raise tường minh; lỗi có thể phát sinh từ dependency gọi bên trong.
- Pre-conditions:
  - Các tham số bắt buộc theo chữ ký phải hợp lệ kiểu dữ liệu trước khi gọi.
- Post-conditions:
  - Hàm kết thúc với giá trị trả về theo contract; trạng thái ngoài hàm chỉ thay đổi khi có side effect nêu ở trên.
- Verify command:
  - `Select-String -Path cogmem_api/engine/search/temporal_extraction.py -Pattern "def get_default_analyzer|async def get_default_analyzer"`

### Function: (module).extract_temporal_constraint
- Signature: `extract_temporal_constraint(query: str, reference_date: datetime | None=None, analyzer: QueryAnalyzer | None=None) -> tuple[datetime, datetime] | None`
- Visibility: `public`
- Location: `cogmem_api/engine/search/temporal_extraction.py:34`
- Purpose:
  - Thực thi nghiệp vụ `extract_temporal_constraint` trong phạm vi `(module)` của module `cogmem_api/engine/search/temporal_extraction.py`.
- Inputs:
  - Theo chữ ký: `extract_temporal_constraint(query: str, reference_date: datetime | None=None, analyzer: QueryAnalyzer | None=None) -> tuple[datetime, datetime] | None`.
- Outputs:
  - Trả về kiểu: `tuple[datetime, datetime] | None`.
- Side effects:
  - Không phát hiện side effect rõ ràng từ phân tích static call graph.
- Dependency calls:
  - `analyze`, `get_default_analyzer`
- Failure modes:
  - Không phát hiện raise tường minh; lỗi có thể phát sinh từ dependency gọi bên trong.
- Pre-conditions:
  - Các tham số bắt buộc theo chữ ký phải hợp lệ kiểu dữ liệu trước khi gọi.
- Post-conditions:
  - Hàm kết thúc với giá trị trả về theo contract; trạng thái ngoài hàm chỉ thay đổi khi có side effect nêu ở trên.
- Verify command:
  - `Select-String -Path cogmem_api/engine/search/temporal_extraction.py -Pattern "def extract_temporal_constraint|async def extract_temporal_constraint"`

## Failure modes
- Inventory drift: hàm mới trong source nhưng chưa có deep-dive section tương ứng.
- Signature drift: refactor chữ ký hàm nhưng không cập nhật docs gây lệch contract.
- Verify command sai path hoặc sai tên hàm khiến khó truy vết nhanh trong review.

## Verify commands
- `uv run python tests/artifacts/test_task719_function_deep_dive.py`
- `Select-String -Path tutorials/functions/cogmem_api_engine_search_temporal_extraction.md -Pattern "### Function:"`
- `Select-String -Path tutorials/functions/cogmem_api_engine_search_temporal_extraction.md -Pattern "- Verify command:"`

