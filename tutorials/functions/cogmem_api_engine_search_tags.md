# Function Deep Dive - cogmem_api/engine/search/tags.py

## Purpose
- Mô tả chi tiết các hàm retrieval, fusion, reranking và routing của recall pipeline.
- Đảm bảo mọi hàm public/private trong module đều có contract docs phục vụ onboarding và traceability.

## Inputs
- Nguồn từ function inventory S18.1 (`tutorials/functions/function-inventory.json`).
- Chữ ký hàm, kiểu trả về, và vị trí dòng trong source module tương ứng.

## Outputs
- Tài liệu deep-dive cho 8 hàm/method trong module này.
- Mỗi hàm có purpose, inputs, outputs, side effects, dependency calls, failure modes, pre/post-conditions, verify command.

## Top-down level
- Function

## Prerequisites
- `tutorials/functions/function-inventory.md`
- `tutorials/module-map.md`
- Module dossier tương ứng trong `tutorials/modules/`

## Module responsibility
- Source module: `cogmem_api/engine/search/tags.py`.
- Public/private breakdown: public=5, private=3.
- Bối cảnh chi tiết từng hàm nằm ở phần Function inventory bên dưới.

## Function inventory (public/private)
| Owner | Function | Visibility | Signature | Location | Deep-dive status |
|---|---|---|---|---|---|
| (module) | _parse_tags_match | private | _parse_tags_match(match: TagsMatch) -> tuple[str, bool] | cogmem_api/engine/search/tags.py:24 | documented |
| (module) | build_tags_where_clause | public | build_tags_where_clause(tags: list[str] \| None, param_offset: int=1, table_alias: str='', match: TagsMatch='any') -> tuple[str, list, int] | cogmem_api/engine/search/tags.py:46 | documented |
| (module) | build_tags_where_clause_simple | public | build_tags_where_clause_simple(tags: list[str] \| None, param_num: int, table_alias: str='', match: TagsMatch='any') -> str | cogmem_api/engine/search/tags.py:93 | documented |
| (module) | filter_results_by_tags | public | filter_results_by_tags(results: list, tags: list[str] \| None, match: TagsMatch='any') -> list | cogmem_api/engine/search/tags.py:128 | documented |
| (module) | _build_group_clause | private | _build_group_clause(group: TagGroup, param_offset: int, table_alias: str) -> tuple[str, list, int] | cogmem_api/engine/search/tags.py:231 | documented |
| (module) | build_tag_groups_where_clause | public | build_tag_groups_where_clause(tag_groups: list[TagGroup] \| None, param_offset: int, table_alias: str='') -> tuple[str, list, int] | cogmem_api/engine/search/tags.py:282 | documented |
| (module) | _match_group | private | _match_group(result: object, group: TagGroup) -> bool | cogmem_api/engine/search/tags.py:330 | documented |
| (module) | filter_results_by_tag_groups | public | filter_results_by_tag_groups(results: list, tag_groups: list[TagGroup] \| None) -> list | cogmem_api/engine/search/tags.py:370 | documented |

### Function: (module)._parse_tags_match
- Signature: `_parse_tags_match(match: TagsMatch) -> tuple[str, bool]`
- Visibility: `private`
- Location: `cogmem_api/engine/search/tags.py:24`
- Purpose:
  - Thực thi nghiệp vụ `_parse_tags_match` trong phạm vi `(module)` của module `cogmem_api/engine/search/tags.py`.
- Inputs:
  - Theo chữ ký: `_parse_tags_match(match: TagsMatch) -> tuple[str, bool]`.
- Outputs:
  - Trả về kiểu: `tuple[str, bool]`.
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
  - `Select-String -Path cogmem_api/engine/search/tags.py -Pattern "def _parse_tags_match|async def _parse_tags_match"`

### Function: (module).build_tags_where_clause
- Signature: `build_tags_where_clause(tags: list[str] | None, param_offset: int=1, table_alias: str='', match: TagsMatch='any') -> tuple[str, list, int]`
- Visibility: `public`
- Location: `cogmem_api/engine/search/tags.py:46`
- Purpose:
  - Thực thi nghiệp vụ `build_tags_where_clause` trong phạm vi `(module)` của module `cogmem_api/engine/search/tags.py`.
- Inputs:
  - Theo chữ ký: `build_tags_where_clause(tags: list[str] | None, param_offset: int=1, table_alias: str='', match: TagsMatch='any') -> tuple[str, list, int]`.
- Outputs:
  - Trả về kiểu: `tuple[str, list, int]`.
- Side effects:
  - Không phát hiện side effect rõ ràng từ phân tích static call graph.
- Dependency calls:
  - `_parse_tags_match`
- Failure modes:
  - Không phát hiện raise tường minh; lỗi có thể phát sinh từ dependency gọi bên trong.
- Pre-conditions:
  - Các tham số bắt buộc theo chữ ký phải hợp lệ kiểu dữ liệu trước khi gọi.
- Post-conditions:
  - Hàm kết thúc với giá trị trả về theo contract; trạng thái ngoài hàm chỉ thay đổi khi có side effect nêu ở trên.
- Verify command:
  - `Select-String -Path cogmem_api/engine/search/tags.py -Pattern "def build_tags_where_clause|async def build_tags_where_clause"`

### Function: (module).build_tags_where_clause_simple
- Signature: `build_tags_where_clause_simple(tags: list[str] | None, param_num: int, table_alias: str='', match: TagsMatch='any') -> str`
- Visibility: `public`
- Location: `cogmem_api/engine/search/tags.py:93`
- Purpose:
  - Thực thi nghiệp vụ `build_tags_where_clause_simple` trong phạm vi `(module)` của module `cogmem_api/engine/search/tags.py`.
- Inputs:
  - Theo chữ ký: `build_tags_where_clause_simple(tags: list[str] | None, param_num: int, table_alias: str='', match: TagsMatch='any') -> str`.
- Outputs:
  - Trả về kiểu: `str`.
- Side effects:
  - Không phát hiện side effect rõ ràng từ phân tích static call graph.
- Dependency calls:
  - `_parse_tags_match`
- Failure modes:
  - Không phát hiện raise tường minh; lỗi có thể phát sinh từ dependency gọi bên trong.
- Pre-conditions:
  - Các tham số bắt buộc theo chữ ký phải hợp lệ kiểu dữ liệu trước khi gọi.
- Post-conditions:
  - Hàm kết thúc với giá trị trả về theo contract; trạng thái ngoài hàm chỉ thay đổi khi có side effect nêu ở trên.
- Verify command:
  - `Select-String -Path cogmem_api/engine/search/tags.py -Pattern "def build_tags_where_clause_simple|async def build_tags_where_clause_simple"`

### Function: (module).filter_results_by_tags
- Signature: `filter_results_by_tags(results: list, tags: list[str] | None, match: TagsMatch='any') -> list`
- Visibility: `public`
- Location: `cogmem_api/engine/search/tags.py:128`
- Purpose:
  - Thực thi nghiệp vụ `filter_results_by_tags` trong phạm vi `(module)` của module `cogmem_api/engine/search/tags.py`.
- Inputs:
  - Theo chữ ký: `filter_results_by_tags(results: list, tags: list[str] | None, match: TagsMatch='any') -> list`.
- Outputs:
  - Trả về kiểu: `list`.
- Side effects:
  - Không phát hiện side effect rõ ràng từ phân tích static call graph.
- Dependency calls:
  - `_parse_tags_match`, `set`, `getattr`, `len`, `append`
- Failure modes:
  - Không phát hiện raise tường minh; lỗi có thể phát sinh từ dependency gọi bên trong.
- Pre-conditions:
  - Các tham số bắt buộc theo chữ ký phải hợp lệ kiểu dữ liệu trước khi gọi.
- Post-conditions:
  - Hàm kết thúc với giá trị trả về theo contract; trạng thái ngoài hàm chỉ thay đổi khi có side effect nêu ở trên.
- Verify command:
  - `Select-String -Path cogmem_api/engine/search/tags.py -Pattern "def filter_results_by_tags|async def filter_results_by_tags"`

### Function: (module)._build_group_clause
- Signature: `_build_group_clause(group: TagGroup, param_offset: int, table_alias: str) -> tuple[str, list, int]`
- Visibility: `private`
- Location: `cogmem_api/engine/search/tags.py:231`
- Purpose:
  - Thực thi nghiệp vụ `_build_group_clause` trong phạm vi `(module)` của module `cogmem_api/engine/search/tags.py`.
- Inputs:
  - Theo chữ ký: `_build_group_clause(group: TagGroup, param_offset: int, table_alias: str) -> tuple[str, list, int]`.
- Outputs:
  - Trả về kiểu: `tuple[str, list, int]`.
- Side effects:
  - Không phát hiện side effect rõ ràng từ phân tích static call graph.
- Dependency calls:
  - `isinstance`, `_parse_tags_match`, `join`, `_build_group_clause`, `append`, `extend`
- Failure modes:
  - Không phát hiện raise tường minh; lỗi có thể phát sinh từ dependency gọi bên trong.
- Pre-conditions:
  - Các tham số bắt buộc theo chữ ký phải hợp lệ kiểu dữ liệu trước khi gọi.
- Post-conditions:
  - Hàm kết thúc với giá trị trả về theo contract; trạng thái ngoài hàm chỉ thay đổi khi có side effect nêu ở trên.
- Verify command:
  - `Select-String -Path cogmem_api/engine/search/tags.py -Pattern "def _build_group_clause|async def _build_group_clause"`

### Function: (module).build_tag_groups_where_clause
- Signature: `build_tag_groups_where_clause(tag_groups: list[TagGroup] | None, param_offset: int, table_alias: str='') -> tuple[str, list, int]`
- Visibility: `public`
- Location: `cogmem_api/engine/search/tags.py:282`
- Purpose:
  - Thực thi nghiệp vụ `build_tag_groups_where_clause` trong phạm vi `(module)` của module `cogmem_api/engine/search/tags.py`.
- Inputs:
  - Theo chữ ký: `build_tag_groups_where_clause(tag_groups: list[TagGroup] | None, param_offset: int, table_alias: str='') -> tuple[str, list, int]`.
- Outputs:
  - Trả về kiểu: `tuple[str, list, int]`.
- Side effects:
  - Không phát hiện side effect rõ ràng từ phân tích static call graph.
- Dependency calls:
  - `join`, `_build_group_clause`, `append`, `extend`
- Failure modes:
  - Không phát hiện raise tường minh; lỗi có thể phát sinh từ dependency gọi bên trong.
- Pre-conditions:
  - Các tham số bắt buộc theo chữ ký phải hợp lệ kiểu dữ liệu trước khi gọi.
- Post-conditions:
  - Hàm kết thúc với giá trị trả về theo contract; trạng thái ngoài hàm chỉ thay đổi khi có side effect nêu ở trên.
- Verify command:
  - `Select-String -Path cogmem_api/engine/search/tags.py -Pattern "def build_tag_groups_where_clause|async def build_tag_groups_where_clause"`

### Function: (module)._match_group
- Signature: `_match_group(result: object, group: TagGroup) -> bool`
- Visibility: `private`
- Location: `cogmem_api/engine/search/tags.py:330`
- Purpose:
  - Thực thi nghiệp vụ `_match_group` trong phạm vi `(module)` của module `cogmem_api/engine/search/tags.py`.
- Inputs:
  - Theo chữ ký: `_match_group(result: object, group: TagGroup) -> bool`.
- Outputs:
  - Trả về kiểu: `bool`.
- Side effects:
  - Không phát hiện side effect rõ ràng từ phân tích static call graph.
- Dependency calls:
  - `isinstance`, `getattr`, `_parse_tags_match`, `set`, `all`, `len`, `bool`, `any`, `_match_group`
- Failure modes:
  - Không phát hiện raise tường minh; lỗi có thể phát sinh từ dependency gọi bên trong.
- Pre-conditions:
  - Các tham số bắt buộc theo chữ ký phải hợp lệ kiểu dữ liệu trước khi gọi.
- Post-conditions:
  - Hàm kết thúc với giá trị trả về theo contract; trạng thái ngoài hàm chỉ thay đổi khi có side effect nêu ở trên.
- Verify command:
  - `Select-String -Path cogmem_api/engine/search/tags.py -Pattern "def _match_group|async def _match_group"`

### Function: (module).filter_results_by_tag_groups
- Signature: `filter_results_by_tag_groups(results: list, tag_groups: list[TagGroup] | None) -> list`
- Visibility: `public`
- Location: `cogmem_api/engine/search/tags.py:370`
- Purpose:
  - Thực thi nghiệp vụ `filter_results_by_tag_groups` trong phạm vi `(module)` của module `cogmem_api/engine/search/tags.py`.
- Inputs:
  - Theo chữ ký: `filter_results_by_tag_groups(results: list, tag_groups: list[TagGroup] | None) -> list`.
- Outputs:
  - Trả về kiểu: `list`.
- Side effects:
  - Không phát hiện side effect rõ ràng từ phân tích static call graph.
- Dependency calls:
  - `all`, `_match_group`
- Failure modes:
  - Không phát hiện raise tường minh; lỗi có thể phát sinh từ dependency gọi bên trong.
- Pre-conditions:
  - Các tham số bắt buộc theo chữ ký phải hợp lệ kiểu dữ liệu trước khi gọi.
- Post-conditions:
  - Hàm kết thúc với giá trị trả về theo contract; trạng thái ngoài hàm chỉ thay đổi khi có side effect nêu ở trên.
- Verify command:
  - `Select-String -Path cogmem_api/engine/search/tags.py -Pattern "def filter_results_by_tag_groups|async def filter_results_by_tag_groups"`

## Failure modes
- Inventory drift: hàm mới trong source nhưng chưa có deep-dive section tương ứng.
- Signature drift: refactor chữ ký hàm nhưng không cập nhật docs gây lệch contract.
- Verify command sai path hoặc sai tên hàm khiến khó truy vết nhanh trong review.

## Verify commands
- `uv run python tests/artifacts/test_task719_function_deep_dive.py`
- `Select-String -Path tutorials/functions/cogmem_api_engine_search_tags.md -Pattern "### Function:"`
- `Select-String -Path tutorials/functions/cogmem_api_engine_search_tags.md -Pattern "- Verify command:"`

