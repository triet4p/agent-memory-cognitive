# Function Deep Dive - [cogmem_api/engine/retain/embedding_utils.py](https://github.com/triet4p/agent-memory-cognitive/blob/master/cogmem_api/engine/retain/embedding_utils.py)

## Purpose
- Mô tả chi tiết các hàm ingestion/retain và chuẩn hóa dữ liệu trước khi ghi graph.
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
- Source module: `cogmem_api/engine/retain/embedding_utils.py`.
- Public/private breakdown: public=1, private=1.
- Bối cảnh chi tiết từng hàm nằm ở phần Function inventory bên dưới.

## Function inventory (public/private)
| Owner | Function | Visibility | Signature | Location | Deep-dive status |
|---|---|---|---|---|---|
| (module) | _deterministic_embedding | private | _deterministic_embedding(text: str, dimension: int) -> list[float] | [cogmem_api/engine/retain/embedding_utils.py](https://github.com/triet4p/agent-memory-cognitive/blob/master/cogmem_api/engine/retain/embedding_utils.py):12 | documented |
| (module) | generate_embeddings_batch | public | async generate_embeddings_batch(embeddings_model, texts: list[str], dimension: int \| None=None) -> list[list[float]] | [cogmem_api/engine/retain/embedding_utils.py](https://github.com/triet4p/agent-memory-cognitive/blob/master/cogmem_api/engine/retain/embedding_utils.py):33 | documented |

### Function: (module)._deterministic_embedding
- Signature: `_deterministic_embedding(text: str, dimension: int) -> list[float]`
- Visibility: `private`
- Location: `cogmem_api/engine/retain/embedding_utils.py:12`
- Purpose:
  - Thực thi nghiệp vụ `_deterministic_embedding` trong phạm vi `(module)` của module `cogmem_api/engine/retain/embedding_utils.py`.
- Inputs:
  - Theo chữ ký: `_deterministic_embedding(text: str, dimension: int) -> list[float]`.
- Outputs:
  - Trả về kiểu: `list[float]`.
- Side effects:
  - Không phát hiện side effect rõ ràng từ phân tích static call graph.
- Dependency calls:
  - `split`, `sqrt`, `digest`, `sum`, `from_bytes`, `sha256`, `encode`
- Failure modes:
  - Không phát hiện raise tường minh; lỗi có thể phát sinh từ dependency gọi bên trong.
- Pre-conditions:
  - Các tham số bắt buộc theo chữ ký phải hợp lệ kiểu dữ liệu trước khi gọi.
- Post-conditions:
  - Hàm kết thúc với giá trị trả về theo contract; trạng thái ngoài hàm chỉ thay đổi khi có side effect nêu ở trên.
- Verify command:
  - `Select-String -Path cogmem_api/engine/retain/embedding_utils.py -Pattern "def _deterministic_embedding|async def _deterministic_embedding"`

### Function: (module).generate_embeddings_batch
- Signature: `async generate_embeddings_batch(embeddings_model, texts: list[str], dimension: int | None=None) -> list[list[float]]`
- Visibility: `public`
- Location: `cogmem_api/engine/retain/embedding_utils.py:33`
- Purpose:
  - Thực thi nghiệp vụ `generate_embeddings_batch` trong phạm vi `(module)` của module `cogmem_api/engine/retain/embedding_utils.py`.
- Inputs:
  - Theo chữ ký: `async generate_embeddings_batch(embeddings_model, texts: list[str], dimension: int | None=None) -> list[list[float]]`.
- Outputs:
  - Trả về kiểu: `list[list[float]]`.
- Side effects:
  - Không phát hiện side effect rõ ràng từ phân tích static call graph.
- Dependency calls:
  - `hasattr`, `encode`, `isinstance`, `_deterministic_embedding`, `list`, `map`
- Failure modes:
  - Không phát hiện raise tường minh; lỗi có thể phát sinh từ dependency gọi bên trong.
- Pre-conditions:
  - Các tham số bắt buộc theo chữ ký phải hợp lệ kiểu dữ liệu trước khi gọi.
- Post-conditions:
  - Hàm kết thúc với giá trị trả về theo contract; trạng thái ngoài hàm chỉ thay đổi khi có side effect nêu ở trên.
- Verify command:
  - `Select-String -Path cogmem_api/engine/retain/embedding_utils.py -Pattern "def generate_embeddings_batch|async def generate_embeddings_batch"`

## Failure modes
- Inventory drift: hàm mới trong source nhưng chưa có deep-dive section tương ứng.
- Signature drift: refactor chữ ký hàm nhưng không cập nhật docs gây lệch contract.
- Verify command sai path hoặc sai tên hàm khiến khó truy vết nhanh trong review.

## Verify commands
- `uv run python tests/artifacts/test_task719_function_deep_dive.py`
- `Select-String -Path tutorials/functions/cogmem_api_engine_retain_embedding_utils.md -Pattern "### Function:"`
- `Select-String -Path tutorials/functions/cogmem_api_engine_retain_embedding_utils.md -Pattern "- Verify command:"`

