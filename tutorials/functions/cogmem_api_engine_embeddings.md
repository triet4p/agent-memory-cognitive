# Function Deep Dive - cogmem_api/engine/embeddings.py

## Purpose
- Mô tả chi tiết các hàm trong module và contract input/output ở mức function-level.
- Đảm bảo mọi hàm public/private trong module đều có contract docs phục vụ onboarding và traceability.

## Inputs
- Nguồn từ function inventory S18.1 (`tutorials/functions/function-inventory.json`).
- Chữ ký hàm, kiểu trả về, và vị trí dòng trong source module tương ứng.

## Outputs
- Tài liệu deep-dive cho 21 hàm/method trong module này.
- Mỗi hàm có purpose, inputs, outputs, side effects, dependency calls, failure modes, pre/post-conditions, verify command.

## Top-down level
- Function

## Prerequisites
- `tutorials/functions/function-inventory.md`
- `tutorials/module-map.md`
- Module dossier tương ứng trong `tutorials/modules/`

## Module responsibility
- Source module: `cogmem_api/engine/embeddings.py`.
- Public/private breakdown: public=17, private=4.
- Bối cảnh chi tiết từng hàm nằm ở phần Function inventory bên dưới.

## Function inventory (public/private)
| Owner | Function | Visibility | Signature | Location | Deep-dive status |
|---|---|---|---|---|---|
| (module) | create_embeddings_from_env | public | create_embeddings_from_env() -> Embeddings | cogmem_api/engine/embeddings.py:179 | documented |
| DeterministicEmbeddings | __init__ | private | __init__(self, dimension: int=EMBEDDING_DIMENSION) | cogmem_api/engine/embeddings.py:44 | documented |
| DeterministicEmbeddings | provider_name | public | provider_name(self) -> str | cogmem_api/engine/embeddings.py:48 | documented |
| DeterministicEmbeddings | dimension | public | dimension(self) -> int | cogmem_api/engine/embeddings.py:52 | documented |
| DeterministicEmbeddings | initialize | public | async initialize(self) -> None | cogmem_api/engine/embeddings.py:55 | documented |
| DeterministicEmbeddings | _embed_one | private | _embed_one(self, text: str) -> list[float] | cogmem_api/engine/embeddings.py:58 | documented |
| DeterministicEmbeddings | encode | public | encode(self, texts: list[str]) -> list[list[float]] | cogmem_api/engine/embeddings.py:74 | documented |
| Embeddings | provider_name | public | provider_name(self) -> str | cogmem_api/engine/embeddings.py:21 | documented |
| Embeddings | dimension | public | dimension(self) -> int | cogmem_api/engine/embeddings.py:26 | documented |
| Embeddings | initialize | public | async initialize(self) -> None | cogmem_api/engine/embeddings.py:30 | documented |
| Embeddings | encode | public | encode(self, texts: list[str]) -> list[list[float]] | cogmem_api/engine/embeddings.py:34 | documented |
| LocalSTEmbeddings | __init__ | private | __init__(self, model_name: str) | cogmem_api/engine/embeddings.py:81 | documented |
| LocalSTEmbeddings | provider_name | public | provider_name(self) -> str | cogmem_api/engine/embeddings.py:87 | documented |
| LocalSTEmbeddings | dimension | public | dimension(self) -> int | cogmem_api/engine/embeddings.py:91 | documented |
| LocalSTEmbeddings | initialize | public | async initialize(self) -> None | cogmem_api/engine/embeddings.py:96 | documented |
| LocalSTEmbeddings | encode | public | encode(self, texts: list[str]) -> list[list[float]] | cogmem_api/engine/embeddings.py:112 | documented |
| OpenAIEmbeddings | __init__ | private | __init__(self, api_key: str, model: str, base_url: str \| None=None) | cogmem_api/engine/embeddings.py:128 | documented |
| OpenAIEmbeddings | provider_name | public | provider_name(self) -> str | cogmem_api/engine/embeddings.py:136 | documented |
| OpenAIEmbeddings | dimension | public | dimension(self) -> int | cogmem_api/engine/embeddings.py:140 | documented |
| OpenAIEmbeddings | initialize | public | async initialize(self) -> None | cogmem_api/engine/embeddings.py:145 | documented |
| OpenAIEmbeddings | encode | public | encode(self, texts: list[str]) -> list[list[float]] | cogmem_api/engine/embeddings.py:168 | documented |

### Function: (module).create_embeddings_from_env
- Signature: `create_embeddings_from_env() -> Embeddings`
- Visibility: `public`
- Location: `cogmem_api/engine/embeddings.py:179`
- Purpose:
  - Thực thi nghiệp vụ `create_embeddings_from_env` trong phạm vi `(module)` của module `cogmem_api/engine/embeddings.py`.
- Inputs:
  - Theo chữ ký: `create_embeddings_from_env() -> Embeddings`.
- Outputs:
  - Trả về kiểu: `Embeddings`.
- Side effects:
  - Không phát hiện side effect rõ ràng từ phân tích static call graph.
- Dependency calls:
  - `get_config`, `lower`, `ValueError`, `LocalSTEmbeddings`, `OpenAIEmbeddings`, `DeterministicEmbeddings`
- Failure modes:
  - Có thể raise: `ValueError`.
- Pre-conditions:
  - Các tham số bắt buộc theo chữ ký phải hợp lệ kiểu dữ liệu trước khi gọi.
- Post-conditions:
  - Hàm kết thúc với giá trị trả về theo contract; trạng thái ngoài hàm chỉ thay đổi khi có side effect nêu ở trên.
- Verify command:
  - `Select-String -Path cogmem_api/engine/embeddings.py -Pattern "def create_embeddings_from_env|async def create_embeddings_from_env"`

### Function: DeterministicEmbeddings.__init__
- Signature: `__init__(self, dimension: int=EMBEDDING_DIMENSION)`
- Visibility: `private`
- Location: `cogmem_api/engine/embeddings.py:44`
- Purpose:
  - Thực thi nghiệp vụ `__init__` trong phạm vi `DeterministicEmbeddings` của module `cogmem_api/engine/embeddings.py`.
- Inputs:
  - Theo chữ ký: `__init__(self, dimension: int=EMBEDDING_DIMENSION)`.
- Outputs:
  - Không khai báo kiểu trả về tường minh; hành vi phụ thuộc implementation.
- Side effects:
  - Không phát hiện side effect rõ ràng từ phân tích static call graph.
- Dependency calls:
  - `max`, `int`
- Failure modes:
  - Không phát hiện raise tường minh; lỗi có thể phát sinh từ dependency gọi bên trong.
- Pre-conditions:
  - Các tham số bắt buộc theo chữ ký phải hợp lệ kiểu dữ liệu trước khi gọi.
- Post-conditions:
  - Hàm kết thúc với giá trị trả về theo contract; trạng thái ngoài hàm chỉ thay đổi khi có side effect nêu ở trên.
- Verify command:
  - `Select-String -Path cogmem_api/engine/embeddings.py -Pattern "def __init__|async def __init__"`

### Function: DeterministicEmbeddings.provider_name
- Signature: `provider_name(self) -> str`
- Visibility: `public`
- Location: `cogmem_api/engine/embeddings.py:48`
- Purpose:
  - Thực thi nghiệp vụ `provider_name` trong phạm vi `DeterministicEmbeddings` của module `cogmem_api/engine/embeddings.py`.
- Inputs:
  - Theo chữ ký: `provider_name(self) -> str`.
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
  - `Select-String -Path cogmem_api/engine/embeddings.py -Pattern "def provider_name|async def provider_name"`

### Function: DeterministicEmbeddings.dimension
- Signature: `dimension(self) -> int`
- Visibility: `public`
- Location: `cogmem_api/engine/embeddings.py:52`
- Purpose:
  - Thực thi nghiệp vụ `dimension` trong phạm vi `DeterministicEmbeddings` của module `cogmem_api/engine/embeddings.py`.
- Inputs:
  - Theo chữ ký: `dimension(self) -> int`.
- Outputs:
  - Trả về kiểu: `int`.
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
  - `Select-String -Path cogmem_api/engine/embeddings.py -Pattern "def dimension|async def dimension"`

### Function: DeterministicEmbeddings.initialize
- Signature: `async initialize(self) -> None`
- Visibility: `public`
- Location: `cogmem_api/engine/embeddings.py:55`
- Purpose:
  - Thực thi nghiệp vụ `initialize` trong phạm vi `DeterministicEmbeddings` của module `cogmem_api/engine/embeddings.py`.
- Inputs:
  - Theo chữ ký: `async initialize(self) -> None`.
- Outputs:
  - Trả về kiểu: `None`.
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
  - `Select-String -Path cogmem_api/engine/embeddings.py -Pattern "def initialize|async def initialize"`

### Function: DeterministicEmbeddings._embed_one
- Signature: `_embed_one(self, text: str) -> list[float]`
- Visibility: `private`
- Location: `cogmem_api/engine/embeddings.py:58`
- Purpose:
  - Thực thi nghiệp vụ `_embed_one` trong phạm vi `DeterministicEmbeddings` của module `cogmem_api/engine/embeddings.py`.
- Inputs:
  - Theo chữ ký: `_embed_one(self, text: str) -> list[float]`.
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
  - `Select-String -Path cogmem_api/engine/embeddings.py -Pattern "def _embed_one|async def _embed_one"`

### Function: DeterministicEmbeddings.encode
- Signature: `encode(self, texts: list[str]) -> list[list[float]]`
- Visibility: `public`
- Location: `cogmem_api/engine/embeddings.py:74`
- Purpose:
  - Thực thi nghiệp vụ `encode` trong phạm vi `DeterministicEmbeddings` của module `cogmem_api/engine/embeddings.py`.
- Inputs:
  - Theo chữ ký: `encode(self, texts: list[str]) -> list[list[float]]`.
- Outputs:
  - Trả về kiểu: `list[list[float]]`.
- Side effects:
  - Không phát hiện side effect rõ ràng từ phân tích static call graph.
- Dependency calls:
  - `_embed_one`
- Failure modes:
  - Không phát hiện raise tường minh; lỗi có thể phát sinh từ dependency gọi bên trong.
- Pre-conditions:
  - Các tham số bắt buộc theo chữ ký phải hợp lệ kiểu dữ liệu trước khi gọi.
- Post-conditions:
  - Hàm kết thúc với giá trị trả về theo contract; trạng thái ngoài hàm chỉ thay đổi khi có side effect nêu ở trên.
- Verify command:
  - `Select-String -Path cogmem_api/engine/embeddings.py -Pattern "def encode|async def encode"`

### Function: Embeddings.provider_name
- Signature: `provider_name(self) -> str`
- Visibility: `public`
- Location: `cogmem_api/engine/embeddings.py:21`
- Purpose:
  - Thực thi nghiệp vụ `provider_name` trong phạm vi `Embeddings` của module `cogmem_api/engine/embeddings.py`.
- Inputs:
  - Theo chữ ký: `provider_name(self) -> str`.
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
  - `Select-String -Path cogmem_api/engine/embeddings.py -Pattern "def provider_name|async def provider_name"`

### Function: Embeddings.dimension
- Signature: `dimension(self) -> int`
- Visibility: `public`
- Location: `cogmem_api/engine/embeddings.py:26`
- Purpose:
  - Thực thi nghiệp vụ `dimension` trong phạm vi `Embeddings` của module `cogmem_api/engine/embeddings.py`.
- Inputs:
  - Theo chữ ký: `dimension(self) -> int`.
- Outputs:
  - Trả về kiểu: `int`.
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
  - `Select-String -Path cogmem_api/engine/embeddings.py -Pattern "def dimension|async def dimension"`

### Function: Embeddings.initialize
- Signature: `async initialize(self) -> None`
- Visibility: `public`
- Location: `cogmem_api/engine/embeddings.py:30`
- Purpose:
  - Thực thi nghiệp vụ `initialize` trong phạm vi `Embeddings` của module `cogmem_api/engine/embeddings.py`.
- Inputs:
  - Theo chữ ký: `async initialize(self) -> None`.
- Outputs:
  - Trả về kiểu: `None`.
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
  - `Select-String -Path cogmem_api/engine/embeddings.py -Pattern "def initialize|async def initialize"`

### Function: Embeddings.encode
- Signature: `encode(self, texts: list[str]) -> list[list[float]]`
- Visibility: `public`
- Location: `cogmem_api/engine/embeddings.py:34`
- Purpose:
  - Thực thi nghiệp vụ `encode` trong phạm vi `Embeddings` của module `cogmem_api/engine/embeddings.py`.
- Inputs:
  - Theo chữ ký: `encode(self, texts: list[str]) -> list[list[float]]`.
- Outputs:
  - Trả về kiểu: `list[list[float]]`.
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
  - `Select-String -Path cogmem_api/engine/embeddings.py -Pattern "def encode|async def encode"`

### Function: LocalSTEmbeddings.__init__
- Signature: `__init__(self, model_name: str)`
- Visibility: `private`
- Location: `cogmem_api/engine/embeddings.py:81`
- Purpose:
  - Thực thi nghiệp vụ `__init__` trong phạm vi `LocalSTEmbeddings` của module `cogmem_api/engine/embeddings.py`.
- Inputs:
  - Theo chữ ký: `__init__(self, model_name: str)`.
- Outputs:
  - Không khai báo kiểu trả về tường minh; hành vi phụ thuộc implementation.
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
  - `Select-String -Path cogmem_api/engine/embeddings.py -Pattern "def __init__|async def __init__"`

### Function: LocalSTEmbeddings.provider_name
- Signature: `provider_name(self) -> str`
- Visibility: `public`
- Location: `cogmem_api/engine/embeddings.py:87`
- Purpose:
  - Thực thi nghiệp vụ `provider_name` trong phạm vi `LocalSTEmbeddings` của module `cogmem_api/engine/embeddings.py`.
- Inputs:
  - Theo chữ ký: `provider_name(self) -> str`.
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
  - `Select-String -Path cogmem_api/engine/embeddings.py -Pattern "def provider_name|async def provider_name"`

### Function: LocalSTEmbeddings.dimension
- Signature: `dimension(self) -> int`
- Visibility: `public`
- Location: `cogmem_api/engine/embeddings.py:91`
- Purpose:
  - Thực thi nghiệp vụ `dimension` trong phạm vi `LocalSTEmbeddings` của module `cogmem_api/engine/embeddings.py`.
- Inputs:
  - Theo chữ ký: `dimension(self) -> int`.
- Outputs:
  - Trả về kiểu: `int`.
- Side effects:
  - Không phát hiện side effect rõ ràng từ phân tích static call graph.
- Dependency calls:
  - `RuntimeError`
- Failure modes:
  - Có thể raise: `RuntimeError`.
- Pre-conditions:
  - Các tham số bắt buộc theo chữ ký phải hợp lệ kiểu dữ liệu trước khi gọi.
- Post-conditions:
  - Hàm kết thúc với giá trị trả về theo contract; trạng thái ngoài hàm chỉ thay đổi khi có side effect nêu ở trên.
- Verify command:
  - `Select-String -Path cogmem_api/engine/embeddings.py -Pattern "def dimension|async def dimension"`

### Function: LocalSTEmbeddings.initialize
- Signature: `async initialize(self) -> None`
- Visibility: `public`
- Location: `cogmem_api/engine/embeddings.py:96`
- Purpose:
  - Thực thi nghiệp vụ `initialize` trong phạm vi `LocalSTEmbeddings` của module `cogmem_api/engine/embeddings.py`.
- Inputs:
  - Theo chữ ký: `async initialize(self) -> None`.
- Outputs:
  - Trả về kiểu: `None`.
- Side effects:
  - Không phát hiện side effect rõ ràng từ phân tích static call graph.
- Dependency calls:
  - `SentenceTransformer`, `int`, `info`, `import_module`, `getattr`, `get_sentence_embedding_dimension`, `ImportError`
- Failure modes:
  - Có thể raise: `ImportError`.
- Pre-conditions:
  - Các tham số bắt buộc theo chữ ký phải hợp lệ kiểu dữ liệu trước khi gọi.
- Post-conditions:
  - Hàm kết thúc với giá trị trả về theo contract; trạng thái ngoài hàm chỉ thay đổi khi có side effect nêu ở trên.
- Verify command:
  - `Select-String -Path cogmem_api/engine/embeddings.py -Pattern "def initialize|async def initialize"`

### Function: LocalSTEmbeddings.encode
- Signature: `encode(self, texts: list[str]) -> list[list[float]]`
- Visibility: `public`
- Location: `cogmem_api/engine/embeddings.py:112`
- Purpose:
  - Thực thi nghiệp vụ `encode` trong phạm vi `LocalSTEmbeddings` của module `cogmem_api/engine/embeddings.py`.
- Inputs:
  - Theo chữ ký: `encode(self, texts: list[str]) -> list[list[float]]`.
- Outputs:
  - Trả về kiểu: `list[list[float]]`.
- Side effects:
  - Không phát hiện side effect rõ ràng từ phân tích static call graph.
- Dependency calls:
  - `encode`, `RuntimeError`, `tolist`
- Failure modes:
  - Có thể raise: `RuntimeError`.
- Pre-conditions:
  - Các tham số bắt buộc theo chữ ký phải hợp lệ kiểu dữ liệu trước khi gọi.
- Post-conditions:
  - Hàm kết thúc với giá trị trả về theo contract; trạng thái ngoài hàm chỉ thay đổi khi có side effect nêu ở trên.
- Verify command:
  - `Select-String -Path cogmem_api/engine/embeddings.py -Pattern "def encode|async def encode"`

### Function: OpenAIEmbeddings.__init__
- Signature: `__init__(self, api_key: str, model: str, base_url: str | None=None)`
- Visibility: `private`
- Location: `cogmem_api/engine/embeddings.py:128`
- Purpose:
  - Thực thi nghiệp vụ `__init__` trong phạm vi `OpenAIEmbeddings` của module `cogmem_api/engine/embeddings.py`.
- Inputs:
  - Theo chữ ký: `__init__(self, api_key: str, model: str, base_url: str | None=None)`.
- Outputs:
  - Không khai báo kiểu trả về tường minh; hành vi phụ thuộc implementation.
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
  - `Select-String -Path cogmem_api/engine/embeddings.py -Pattern "def __init__|async def __init__"`

### Function: OpenAIEmbeddings.provider_name
- Signature: `provider_name(self) -> str`
- Visibility: `public`
- Location: `cogmem_api/engine/embeddings.py:136`
- Purpose:
  - Thực thi nghiệp vụ `provider_name` trong phạm vi `OpenAIEmbeddings` của module `cogmem_api/engine/embeddings.py`.
- Inputs:
  - Theo chữ ký: `provider_name(self) -> str`.
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
  - `Select-String -Path cogmem_api/engine/embeddings.py -Pattern "def provider_name|async def provider_name"`

### Function: OpenAIEmbeddings.dimension
- Signature: `dimension(self) -> int`
- Visibility: `public`
- Location: `cogmem_api/engine/embeddings.py:140`
- Purpose:
  - Thực thi nghiệp vụ `dimension` trong phạm vi `OpenAIEmbeddings` của module `cogmem_api/engine/embeddings.py`.
- Inputs:
  - Theo chữ ký: `dimension(self) -> int`.
- Outputs:
  - Trả về kiểu: `int`.
- Side effects:
  - Không phát hiện side effect rõ ràng từ phân tích static call graph.
- Dependency calls:
  - `RuntimeError`
- Failure modes:
  - Có thể raise: `RuntimeError`.
- Pre-conditions:
  - Các tham số bắt buộc theo chữ ký phải hợp lệ kiểu dữ liệu trước khi gọi.
- Post-conditions:
  - Hàm kết thúc với giá trị trả về theo contract; trạng thái ngoài hàm chỉ thay đổi khi có side effect nêu ở trên.
- Verify command:
  - `Select-String -Path cogmem_api/engine/embeddings.py -Pattern "def dimension|async def dimension"`

### Function: OpenAIEmbeddings.initialize
- Signature: `async initialize(self) -> None`
- Visibility: `public`
- Location: `cogmem_api/engine/embeddings.py:145`
- Purpose:
  - Thực thi nghiệp vụ `initialize` trong phạm vi `OpenAIEmbeddings` của module `cogmem_api/engine/embeddings.py`.
- Inputs:
  - Theo chữ ký: `async initialize(self) -> None`.
- Outputs:
  - Trả về kiểu: `None`.
- Side effects:
  - Không phát hiện side effect rõ ràng từ phân tích static call graph.
- Dependency calls:
  - `OpenAI`, `info`, `import_module`, `getattr`, `create`, `len`, `ImportError`
- Failure modes:
  - Có thể raise: `ImportError`.
- Pre-conditions:
  - Các tham số bắt buộc theo chữ ký phải hợp lệ kiểu dữ liệu trước khi gọi.
- Post-conditions:
  - Hàm kết thúc với giá trị trả về theo contract; trạng thái ngoài hàm chỉ thay đổi khi có side effect nêu ở trên.
- Verify command:
  - `Select-String -Path cogmem_api/engine/embeddings.py -Pattern "def initialize|async def initialize"`

### Function: OpenAIEmbeddings.encode
- Signature: `encode(self, texts: list[str]) -> list[list[float]]`
- Visibility: `public`
- Location: `cogmem_api/engine/embeddings.py:168`
- Purpose:
  - Thực thi nghiệp vụ `encode` trong phạm vi `OpenAIEmbeddings` của module `cogmem_api/engine/embeddings.py`.
- Inputs:
  - Theo chữ ký: `encode(self, texts: list[str]) -> list[list[float]]`.
- Outputs:
  - Trả về kiểu: `list[list[float]]`.
- Side effects:
  - Không phát hiện side effect rõ ràng từ phân tích static call graph.
- Dependency calls:
  - `create`, `sorted`, `RuntimeError`
- Failure modes:
  - Có thể raise: `RuntimeError`.
- Pre-conditions:
  - Các tham số bắt buộc theo chữ ký phải hợp lệ kiểu dữ liệu trước khi gọi.
- Post-conditions:
  - Hàm kết thúc với giá trị trả về theo contract; trạng thái ngoài hàm chỉ thay đổi khi có side effect nêu ở trên.
- Verify command:
  - `Select-String -Path cogmem_api/engine/embeddings.py -Pattern "def encode|async def encode"`

## Failure modes
- Inventory drift: hàm mới trong source nhưng chưa có deep-dive section tương ứng.
- Signature drift: refactor chữ ký hàm nhưng không cập nhật docs gây lệch contract.
- Verify command sai path hoặc sai tên hàm khiến khó truy vết nhanh trong review.

## Verify commands
- `uv run python tests/artifacts/test_task719_function_deep_dive.py`
- `Select-String -Path tutorials/functions/cogmem_api_engine_embeddings.md -Pattern "### Function:"`
- `Select-String -Path tutorials/functions/cogmem_api_engine_embeddings.md -Pattern "- Verify command:"`

