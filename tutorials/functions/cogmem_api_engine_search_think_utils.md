# Function Deep Dive - cogmem_api/engine/search/think_utils.py

## Purpose
- Mô tả chi tiết các hàm retrieval, fusion, reranking và routing của recall pipeline.
- Đảm bảo mọi hàm public/private trong module đều có contract docs phục vụ onboarding và traceability.

## Inputs
- Nguồn từ function inventory S18.1 (`tutorials/functions/function-inventory.json`).
- Chữ ký hàm, kiểu trả về, và vị trí dòng trong source module tương ứng.

## Outputs
- Tài liệu deep-dive cho 7 hàm/method trong module này.
- Mỗi hàm có purpose, inputs, outputs, side effects, dependency calls, failure modes, pre/post-conditions, verify command.

## Top-down level
- Function

## Prerequisites
- `tutorials/functions/function-inventory.md`
- `tutorials/module-map.md`
- Module dossier tương ứng trong `tutorials/modules/`

## Module responsibility
- Source module: `cogmem_api/engine/search/think_utils.py`.
- Public/private breakdown: public=7, private=0.
- Bối cảnh chi tiết từng hàm nằm ở phần Function inventory bên dưới.

## Function inventory (public/private)
| Owner | Function | Visibility | Signature | Location | Deep-dive status |
|---|---|---|---|---|---|
| (module) | describe_trait_level | public | describe_trait_level(value: int) -> str | cogmem_api/engine/search/think_utils.py:13 | documented |
| (module) | build_disposition_description | public | build_disposition_description(disposition: DispositionTraits) -> str | cogmem_api/engine/search/think_utils.py:19 | documented |
| (module) | format_facts_for_prompt | public | format_facts_for_prompt(facts: list[MemoryFact]) -> str | cogmem_api/engine/search/think_utils.py:51 | documented |
| (module) | format_entity_summaries_for_prompt | public | format_entity_summaries_for_prompt(entities: dict) -> str | cogmem_api/engine/search/think_utils.py:78 | documented |
| (module) | build_think_prompt | public | build_think_prompt(agent_facts_text: str, world_facts_text: str, query: str, name: str, disposition: DispositionTraits, background: str, context: str \| None=None, entity_summaries_text: str \| None=None) -> str | cogmem_api/engine/search/think_utils.py:112 | documented |
| (module) | get_system_message | public | get_system_message(disposition: DispositionTraits) -> str | cogmem_api/engine/search/think_utils.py:173 | documented |
| (module) | reflect | public | async reflect(llm_config, query: str, experience_facts: list[str]=None, world_facts: list[str]=None, name: str='Assistant', disposition: DispositionTraits=None, background: str='', context: str=None) -> str | cogmem_api/engine/search/think_utils.py:203 | documented |

### Function: (module).describe_trait_level
- Signature: `describe_trait_level(value: int) -> str`
- Visibility: `public`
- Location: `cogmem_api/engine/search/think_utils.py:13`
- Purpose:
  - Thực thi nghiệp vụ `describe_trait_level` trong phạm vi `(module)` của module `cogmem_api/engine/search/think_utils.py`.
- Inputs:
  - Theo chữ ký: `describe_trait_level(value: int) -> str`.
- Outputs:
  - Trả về kiểu: `str`.
- Side effects:
  - Không phát hiện side effect rõ ràng từ phân tích static call graph.
- Dependency calls:
  - `get`
- Failure modes:
  - Không phát hiện raise tường minh; lỗi có thể phát sinh từ dependency gọi bên trong.
- Pre-conditions:
  - Các tham số bắt buộc theo chữ ký phải hợp lệ kiểu dữ liệu trước khi gọi.
- Post-conditions:
  - Hàm kết thúc với giá trị trả về theo contract; trạng thái ngoài hàm chỉ thay đổi khi có side effect nêu ở trên.
- Verify command:
  - `Select-String -Path cogmem_api/engine/search/think_utils.py -Pattern "def describe_trait_level|async def describe_trait_level"`

### Function: (module).build_disposition_description
- Signature: `build_disposition_description(disposition: DispositionTraits) -> str`
- Visibility: `public`
- Location: `cogmem_api/engine/search/think_utils.py:19`
- Purpose:
  - Thực thi nghiệp vụ `build_disposition_description` trong phạm vi `(module)` của module `cogmem_api/engine/search/think_utils.py`.
- Inputs:
  - Theo chữ ký: `build_disposition_description(disposition: DispositionTraits) -> str`.
- Outputs:
  - Trả về kiểu: `str`.
- Side effects:
  - Không phát hiện side effect rõ ràng từ phân tích static call graph.
- Dependency calls:
  - `describe_trait_level`, `get`
- Failure modes:
  - Không phát hiện raise tường minh; lỗi có thể phát sinh từ dependency gọi bên trong.
- Pre-conditions:
  - Các tham số bắt buộc theo chữ ký phải hợp lệ kiểu dữ liệu trước khi gọi.
- Post-conditions:
  - Hàm kết thúc với giá trị trả về theo contract; trạng thái ngoài hàm chỉ thay đổi khi có side effect nêu ở trên.
- Verify command:
  - `Select-String -Path cogmem_api/engine/search/think_utils.py -Pattern "def build_disposition_description|async def build_disposition_description"`

### Function: (module).format_facts_for_prompt
- Signature: `format_facts_for_prompt(facts: list[MemoryFact]) -> str`
- Visibility: `public`
- Location: `cogmem_api/engine/search/think_utils.py:51`
- Purpose:
  - Thực thi nghiệp vụ `format_facts_for_prompt` trong phạm vi `(module)` của module `cogmem_api/engine/search/think_utils.py`.
- Inputs:
  - Theo chữ ký: `format_facts_for_prompt(facts: list[MemoryFact]) -> str`.
- Outputs:
  - Trả về kiểu: `str`.
- Side effects:
  - Không phát hiện side effect rõ ràng từ phân tích static call graph.
- Dependency calls:
  - `dumps`, `append`, `isinstance`, `strftime`
- Failure modes:
  - Không phát hiện raise tường minh; lỗi có thể phát sinh từ dependency gọi bên trong.
- Pre-conditions:
  - Các tham số bắt buộc theo chữ ký phải hợp lệ kiểu dữ liệu trước khi gọi.
- Post-conditions:
  - Hàm kết thúc với giá trị trả về theo contract; trạng thái ngoài hàm chỉ thay đổi khi có side effect nêu ở trên.
- Verify command:
  - `Select-String -Path cogmem_api/engine/search/think_utils.py -Pattern "def format_facts_for_prompt|async def format_facts_for_prompt"`

### Function: (module).format_entity_summaries_for_prompt
- Signature: `format_entity_summaries_for_prompt(entities: dict) -> str`
- Visibility: `public`
- Location: `cogmem_api/engine/search/think_utils.py:78`
- Purpose:
  - Thực thi nghiệp vụ `format_entity_summaries_for_prompt` trong phạm vi `(module)` của module `cogmem_api/engine/search/think_utils.py`.
- Inputs:
  - Theo chữ ký: `format_entity_summaries_for_prompt(entities: dict) -> str`.
- Outputs:
  - Trả về kiểu: `str`.
- Side effects:
  - Không phát hiện side effect rõ ràng từ phân tích static call graph.
- Dependency calls:
  - `items`, `join`, `isinstance`, `get`, `getattr`, `append`
- Failure modes:
  - Không phát hiện raise tường minh; lỗi có thể phát sinh từ dependency gọi bên trong.
- Pre-conditions:
  - Các tham số bắt buộc theo chữ ký phải hợp lệ kiểu dữ liệu trước khi gọi.
- Post-conditions:
  - Hàm kết thúc với giá trị trả về theo contract; trạng thái ngoài hàm chỉ thay đổi khi có side effect nêu ở trên.
- Verify command:
  - `Select-String -Path cogmem_api/engine/search/think_utils.py -Pattern "def format_entity_summaries_for_prompt|async def format_entity_summaries_for_prompt"`

### Function: (module).build_think_prompt
- Signature: `build_think_prompt(agent_facts_text: str, world_facts_text: str, query: str, name: str, disposition: DispositionTraits, background: str, context: str | None=None, entity_summaries_text: str | None=None) -> str`
- Visibility: `public`
- Location: `cogmem_api/engine/search/think_utils.py:112`
- Purpose:
  - Thực thi nghiệp vụ `build_think_prompt` trong phạm vi `(module)` của module `cogmem_api/engine/search/think_utils.py`.
- Inputs:
  - Theo chữ ký: `build_think_prompt(agent_facts_text: str, world_facts_text: str, query: str, name: str, disposition: DispositionTraits, background: str, context: str | None=None, entity_summaries_text: str | None=None) -> str`.
- Outputs:
  - Trả về kiểu: `str`.
- Side effects:
  - Không phát hiện side effect rõ ràng từ phân tích static call graph.
- Dependency calls:
  - `build_disposition_description`
- Failure modes:
  - Không phát hiện raise tường minh; lỗi có thể phát sinh từ dependency gọi bên trong.
- Pre-conditions:
  - Các tham số bắt buộc theo chữ ký phải hợp lệ kiểu dữ liệu trước khi gọi.
- Post-conditions:
  - Hàm kết thúc với giá trị trả về theo contract; trạng thái ngoài hàm chỉ thay đổi khi có side effect nêu ở trên.
- Verify command:
  - `Select-String -Path cogmem_api/engine/search/think_utils.py -Pattern "def build_think_prompt|async def build_think_prompt"`

### Function: (module).get_system_message
- Signature: `get_system_message(disposition: DispositionTraits) -> str`
- Visibility: `public`
- Location: `cogmem_api/engine/search/think_utils.py:173`
- Purpose:
  - Thực thi nghiệp vụ `get_system_message` trong phạm vi `(module)` của module `cogmem_api/engine/search/think_utils.py`.
- Inputs:
  - Theo chữ ký: `get_system_message(disposition: DispositionTraits) -> str`.
- Outputs:
  - Trả về kiểu: `str`.
- Side effects:
  - Không phát hiện side effect rõ ràng từ phân tích static call graph.
- Dependency calls:
  - `append`, `join`
- Failure modes:
  - Không phát hiện raise tường minh; lỗi có thể phát sinh từ dependency gọi bên trong.
- Pre-conditions:
  - Các tham số bắt buộc theo chữ ký phải hợp lệ kiểu dữ liệu trước khi gọi.
- Post-conditions:
  - Hàm kết thúc với giá trị trả về theo contract; trạng thái ngoài hàm chỉ thay đổi khi có side effect nêu ở trên.
- Verify command:
  - `Select-String -Path cogmem_api/engine/search/think_utils.py -Pattern "def get_system_message|async def get_system_message"`

### Function: (module).reflect
- Signature: `async reflect(llm_config, query: str, experience_facts: list[str]=None, world_facts: list[str]=None, name: str='Assistant', disposition: DispositionTraits=None, background: str='', context: str=None) -> str`
- Visibility: `public`
- Location: `cogmem_api/engine/search/think_utils.py:203`
- Purpose:
  - Thực thi nghiệp vụ `reflect` trong phạm vi `(module)` của module `cogmem_api/engine/search/think_utils.py`.
- Inputs:
  - Theo chữ ký: `async reflect(llm_config, query: str, experience_facts: list[str]=None, world_facts: list[str]=None, name: str='Assistant', disposition: DispositionTraits=None, background: str='', context: str=None) -> str`.
- Outputs:
  - Trả về kiểu: `str`.
- Side effects:
  - Không phát hiện side effect rõ ràng từ phân tích static call graph.
- Dependency calls:
  - `to_memory_facts`, `format_facts_for_prompt`, `build_think_prompt`, `get_system_message`, `strip`, `DispositionTraits`, `call`, `MemoryFact`, `enumerate`
- Failure modes:
  - Không phát hiện raise tường minh; lỗi có thể phát sinh từ dependency gọi bên trong.
- Pre-conditions:
  - Các tham số bắt buộc theo chữ ký phải hợp lệ kiểu dữ liệu trước khi gọi.
- Post-conditions:
  - Hàm kết thúc với giá trị trả về theo contract; trạng thái ngoài hàm chỉ thay đổi khi có side effect nêu ở trên.
- Verify command:
  - `Select-String -Path cogmem_api/engine/search/think_utils.py -Pattern "def reflect|async def reflect"`

## Failure modes
- Inventory drift: hàm mới trong source nhưng chưa có deep-dive section tương ứng.
- Signature drift: refactor chữ ký hàm nhưng không cập nhật docs gây lệch contract.
- Verify command sai path hoặc sai tên hàm khiến khó truy vết nhanh trong review.

## Verify commands
- `uv run python tests/artifacts/test_task719_function_deep_dive.py`
- `Select-String -Path tutorials/functions/cogmem_api_engine_search_think_utils.md -Pattern "### Function:"`
- `Select-String -Path tutorials/functions/cogmem_api_engine_search_think_utils.md -Pattern "- Verify command:"`

