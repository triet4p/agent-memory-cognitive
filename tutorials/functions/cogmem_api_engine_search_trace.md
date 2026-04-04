# Function Deep Dive - cogmem_api/engine/search/trace.py

## Purpose
- Mô tả chi tiết các hàm retrieval, fusion, reranking và routing của recall pipeline.
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
- Source module: `cogmem_api/engine/search/trace.py`.
- Public/private breakdown: public=6, private=0.
- Bối cảnh chi tiết từng hàm nằm ở phần Function inventory bên dưới.

## Function inventory (public/private)
| Owner | Function | Visibility | Signature | Location | Deep-dive status |
|---|---|---|---|---|---|
| SearchTrace | to_json | public | to_json(self, **kwargs) -> str | cogmem_api/engine/search/trace.py:221 | documented |
| SearchTrace | to_dict | public | to_dict(self) -> dict | cogmem_api/engine/search/trace.py:225 | documented |
| SearchTrace | get_visit_by_node_id | public | get_visit_by_node_id(self, node_id: str) -> NodeVisit \| None | cogmem_api/engine/search/trace.py:229 | documented |
| SearchTrace | get_search_path_to_node | public | get_search_path_to_node(self, node_id: str) -> list[NodeVisit] | cogmem_api/engine/search/trace.py:236 | documented |
| SearchTrace | get_nodes_by_link_type | public | get_nodes_by_link_type(self, link_type: Literal['temporal', 'semantic', 'entity']) -> list[NodeVisit] | cogmem_api/engine/search/trace.py:250 | documented |
| SearchTrace | get_entry_point_nodes | public | get_entry_point_nodes(self) -> list[NodeVisit] | cogmem_api/engine/search/trace.py:254 | documented |

### Function: SearchTrace.to_json
- Signature: `to_json(self, **kwargs) -> str`
- Visibility: `public`
- Location: `cogmem_api/engine/search/trace.py:221`
- Purpose:
  - Thực thi nghiệp vụ `to_json` trong phạm vi `SearchTrace` của module `cogmem_api/engine/search/trace.py`.
- Inputs:
  - Theo chữ ký: `to_json(self, **kwargs) -> str`.
- Outputs:
  - Trả về kiểu: `str`.
- Side effects:
  - Không phát hiện side effect rõ ràng từ phân tích static call graph.
- Dependency calls:
  - `model_dump_json`
- Failure modes:
  - Không phát hiện raise tường minh; lỗi có thể phát sinh từ dependency gọi bên trong.
- Pre-conditions:
  - Các tham số bắt buộc theo chữ ký phải hợp lệ kiểu dữ liệu trước khi gọi.
- Post-conditions:
  - Hàm kết thúc với giá trị trả về theo contract; trạng thái ngoài hàm chỉ thay đổi khi có side effect nêu ở trên.
- Verify command:
  - `Select-String -Path cogmem_api/engine/search/trace.py -Pattern "def to_json|async def to_json"`

### Function: SearchTrace.to_dict
- Signature: `to_dict(self) -> dict`
- Visibility: `public`
- Location: `cogmem_api/engine/search/trace.py:225`
- Purpose:
  - Thực thi nghiệp vụ `to_dict` trong phạm vi `SearchTrace` của module `cogmem_api/engine/search/trace.py`.
- Inputs:
  - Theo chữ ký: `to_dict(self) -> dict`.
- Outputs:
  - Trả về kiểu: `dict`.
- Side effects:
  - Không phát hiện side effect rõ ràng từ phân tích static call graph.
- Dependency calls:
  - `model_dump`
- Failure modes:
  - Không phát hiện raise tường minh; lỗi có thể phát sinh từ dependency gọi bên trong.
- Pre-conditions:
  - Các tham số bắt buộc theo chữ ký phải hợp lệ kiểu dữ liệu trước khi gọi.
- Post-conditions:
  - Hàm kết thúc với giá trị trả về theo contract; trạng thái ngoài hàm chỉ thay đổi khi có side effect nêu ở trên.
- Verify command:
  - `Select-String -Path cogmem_api/engine/search/trace.py -Pattern "def to_dict|async def to_dict"`

### Function: SearchTrace.get_visit_by_node_id
- Signature: `get_visit_by_node_id(self, node_id: str) -> NodeVisit | None`
- Visibility: `public`
- Location: `cogmem_api/engine/search/trace.py:229`
- Purpose:
  - Thực thi nghiệp vụ `get_visit_by_node_id` trong phạm vi `SearchTrace` của module `cogmem_api/engine/search/trace.py`.
- Inputs:
  - Theo chữ ký: `get_visit_by_node_id(self, node_id: str) -> NodeVisit | None`.
- Outputs:
  - Trả về kiểu: `NodeVisit | None`.
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
  - `Select-String -Path cogmem_api/engine/search/trace.py -Pattern "def get_visit_by_node_id|async def get_visit_by_node_id"`

### Function: SearchTrace.get_search_path_to_node
- Signature: `get_search_path_to_node(self, node_id: str) -> list[NodeVisit]`
- Visibility: `public`
- Location: `cogmem_api/engine/search/trace.py:236`
- Purpose:
  - Thực thi nghiệp vụ `get_search_path_to_node` trong phạm vi `SearchTrace` của module `cogmem_api/engine/search/trace.py`.
- Inputs:
  - Theo chữ ký: `get_search_path_to_node(self, node_id: str) -> list[NodeVisit]`.
- Outputs:
  - Trả về kiểu: `list[NodeVisit]`.
- Side effects:
  - Có khả năng tạo side effect qua call `insert`.
- Dependency calls:
  - `get_visit_by_node_id`, `insert`
- Failure modes:
  - Không phát hiện raise tường minh; lỗi có thể phát sinh từ dependency gọi bên trong.
- Pre-conditions:
  - Các tham số bắt buộc theo chữ ký phải hợp lệ kiểu dữ liệu trước khi gọi.
- Post-conditions:
  - Hàm kết thúc với giá trị trả về theo contract; trạng thái ngoài hàm chỉ thay đổi khi có side effect nêu ở trên.
- Verify command:
  - `Select-String -Path cogmem_api/engine/search/trace.py -Pattern "def get_search_path_to_node|async def get_search_path_to_node"`

### Function: SearchTrace.get_nodes_by_link_type
- Signature: `get_nodes_by_link_type(self, link_type: Literal['temporal', 'semantic', 'entity']) -> list[NodeVisit]`
- Visibility: `public`
- Location: `cogmem_api/engine/search/trace.py:250`
- Purpose:
  - Thực thi nghiệp vụ `get_nodes_by_link_type` trong phạm vi `SearchTrace` của module `cogmem_api/engine/search/trace.py`.
- Inputs:
  - Theo chữ ký: `get_nodes_by_link_type(self, link_type: Literal['temporal', 'semantic', 'entity']) -> list[NodeVisit]`.
- Outputs:
  - Trả về kiểu: `list[NodeVisit]`.
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
  - `Select-String -Path cogmem_api/engine/search/trace.py -Pattern "def get_nodes_by_link_type|async def get_nodes_by_link_type"`

### Function: SearchTrace.get_entry_point_nodes
- Signature: `get_entry_point_nodes(self) -> list[NodeVisit]`
- Visibility: `public`
- Location: `cogmem_api/engine/search/trace.py:254`
- Purpose:
  - Thực thi nghiệp vụ `get_entry_point_nodes` trong phạm vi `SearchTrace` của module `cogmem_api/engine/search/trace.py`.
- Inputs:
  - Theo chữ ký: `get_entry_point_nodes(self) -> list[NodeVisit]`.
- Outputs:
  - Trả về kiểu: `list[NodeVisit]`.
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
  - `Select-String -Path cogmem_api/engine/search/trace.py -Pattern "def get_entry_point_nodes|async def get_entry_point_nodes"`

## Failure modes
- Inventory drift: hàm mới trong source nhưng chưa có deep-dive section tương ứng.
- Signature drift: refactor chữ ký hàm nhưng không cập nhật docs gây lệch contract.
- Verify command sai path hoặc sai tên hàm khiến khó truy vết nhanh trong review.

## Verify commands
- `uv run python tests/artifacts/test_task719_function_deep_dive.py`
- `Select-String -Path tutorials/functions/cogmem_api_engine_search_trace.md -Pattern "### Function:"`
- `Select-String -Path tutorials/functions/cogmem_api_engine_search_trace.md -Pattern "- Verify command:"`

