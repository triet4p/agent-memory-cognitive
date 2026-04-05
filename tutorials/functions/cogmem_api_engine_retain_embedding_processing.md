# Function Deep Dive - [cogmem_api/engine/retain/embedding_processing.py](https://github.com/triet4p/agent-memory-cognitive/blob/master/cogmem_api/engine/retain/embedding_processing.py)

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
- Source module: `cogmem_api/engine/retain/embedding_processing.py`.
- Public/private breakdown: public=2, private=0.
- Bối cảnh chi tiết từng hàm nằm ở phần Function inventory bên dưới.

## Function inventory (public/private)
| Owner | Function | Visibility | Signature | Location | Deep-dive status |
|---|---|---|---|---|---|
| (module) | augment_texts_with_dates | public | augment_texts_with_dates(facts: list[ExtractedFact], format_date_fn) -> list[str] | [cogmem_api/engine/retain/embedding_processing.py](https://github.com/triet4p/agent-memory-cognitive/blob/master/cogmem_api/engine/retain/embedding_processing.py):11 | documented |
| (module) | generate_embeddings_batch | public | async generate_embeddings_batch(embeddings_model, texts: list[str]) -> list[list[float]] | [cogmem_api/engine/retain/embedding_processing.py](https://github.com/triet4p/agent-memory-cognitive/blob/master/cogmem_api/engine/retain/embedding_processing.py):28 | documented |

### Function: (module).augment_texts_with_dates
- Signature: `augment_texts_with_dates(facts: list[ExtractedFact], format_date_fn) -> list[str]`
- Visibility: `public`
- Location: `cogmem_api/engine/retain/embedding_processing.py:11`
- Purpose:
  - Thực thi nghiệp vụ `augment_texts_with_dates` trong phạm vi `(module)` của module `cogmem_api/engine/retain/embedding_processing.py`.
- Inputs:
  - Theo chữ ký: `augment_texts_with_dates(facts: list[ExtractedFact], format_date_fn) -> list[str]`.
- Outputs:
  - Trả về kiểu: `list[str]`.
- Side effects:
  - Không phát hiện side effect rõ ràng từ phân tích static call graph.
- Dependency calls:
  - `isinstance`, `append`, `join`, `format_date_fn`
- Failure modes:
  - Không phát hiện raise tường minh; lỗi có thể phát sinh từ dependency gọi bên trong.
- Pre-conditions:
  - Các tham số bắt buộc theo chữ ký phải hợp lệ kiểu dữ liệu trước khi gọi.
- Post-conditions:
  - Hàm kết thúc với giá trị trả về theo contract; trạng thái ngoài hàm chỉ thay đổi khi có side effect nêu ở trên.
- Verify command:
  - `Select-String -Path cogmem_api/engine/retain/embedding_processing.py -Pattern "def augment_texts_with_dates|async def augment_texts_with_dates"`

### Function: (module).generate_embeddings_batch
- Signature: `async generate_embeddings_batch(embeddings_model, texts: list[str]) -> list[list[float]]`
- Visibility: `public`
- Location: `cogmem_api/engine/retain/embedding_processing.py:28`
- Purpose:
  - Thực thi nghiệp vụ `generate_embeddings_batch` trong phạm vi `(module)` của module `cogmem_api/engine/retain/embedding_processing.py`.
- Inputs:
  - Theo chữ ký: `async generate_embeddings_batch(embeddings_model, texts: list[str]) -> list[list[float]]`.
- Outputs:
  - Trả về kiểu: `list[list[float]]`.
- Side effects:
  - Không phát hiện side effect rõ ràng từ phân tích static call graph.
- Dependency calls:
  - `generate_embeddings_batch`
- Failure modes:
  - Không phát hiện raise tường minh; lỗi có thể phát sinh từ dependency gọi bên trong.
- Pre-conditions:
  - Các tham số bắt buộc theo chữ ký phải hợp lệ kiểu dữ liệu trước khi gọi.
- Post-conditions:
  - Hàm kết thúc với giá trị trả về theo contract; trạng thái ngoài hàm chỉ thay đổi khi có side effect nêu ở trên.
- Verify command:
  - `Select-String -Path cogmem_api/engine/retain/embedding_processing.py -Pattern "def generate_embeddings_batch|async def generate_embeddings_batch"`

## Failure modes
- Inventory drift: hàm mới trong source nhưng chưa có deep-dive section tương ứng.
- Signature drift: refactor chữ ký hàm nhưng không cập nhật docs gây lệch contract.
- Verify command sai path hoặc sai tên hàm khiến khó truy vết nhanh trong review.

## Verify commands
- `uv run python tests/artifacts/test_task719_function_deep_dive.py`
- `Select-String -Path tutorials/functions/cogmem_api_engine_retain_embedding_processing.md -Pattern "### Function:"`
- `Select-String -Path tutorials/functions/cogmem_api_engine_retain_embedding_processing.md -Pattern "- Verify command:"`

