# Function Deep Dive - [cogmem_api/engine/cross_encoder.py](https://github.com/triet4p/agent-memory-cognitive/blob/master/cogmem_api/engine/cross_encoder.py)

## Purpose
- Mô tả chi tiết các hàm trong module và contract input/output ở mức function-level.
- Đảm bảo mọi hàm public/private trong module đều có contract docs phục vụ onboarding và traceability.

## Inputs
- Nguồn từ function inventory S18.1 (`tutorials/functions/function-inventory.json`).
- Chữ ký hàm, kiểu trả về, và vị trí dòng trong source module tương ứng.

## Outputs
- Tài liệu deep-dive cho 17 hàm/method trong module này.
- Mỗi hàm có purpose, inputs, outputs, side effects, dependency calls, failure modes, pre/post-conditions, verify command.

## Top-down level
- Function

## Prerequisites
- `tutorials/functions/function-inventory.md`
- `tutorials/module-map.md`
- Module dossier tương ứng trong `tutorials/modules/`

## Module responsibility
- Source module: `cogmem_api/engine/cross_encoder.py`.
- Public/private breakdown: public=13, private=4.
- Bối cảnh chi tiết từng hàm nằm ở phần Function inventory bên dưới.

## Function inventory (public/private)
| Owner | Function | Visibility | Signature | Location | Deep-dive status |
|---|---|---|---|---|---|
| (module) | create_cross_encoder_from_env | public | create_cross_encoder_from_env() -> CrossEncoderModel | [cogmem_api/engine/cross_encoder.py](https://github.com/triet4p/agent-memory-cognitive/blob/master/cogmem_api/engine/cross_encoder.py):191 | documented |
| CrossEncoderModel | provider_name | public | provider_name(self) -> str | [cogmem_api/engine/cross_encoder.py](https://github.com/triet4p/agent-memory-cognitive/blob/master/cogmem_api/engine/cross_encoder.py):24 | documented |
| CrossEncoderModel | initialize | public | async initialize(self) -> None | [cogmem_api/engine/cross_encoder.py](https://github.com/triet4p/agent-memory-cognitive/blob/master/cogmem_api/engine/cross_encoder.py):28 | documented |
| CrossEncoderModel | predict | public | async predict(self, pairs: list[tuple[str, str]]) -> list[float] | [cogmem_api/engine/cross_encoder.py](https://github.com/triet4p/agent-memory-cognitive/blob/master/cogmem_api/engine/cross_encoder.py):32 | documented |
| LocalSTCrossEncoder | __init__ | private | __init__(self, model_name: str, max_concurrent: int=4) | [cogmem_api/engine/cross_encoder.py](https://github.com/triet4p/agent-memory-cognitive/blob/master/cogmem_api/engine/cross_encoder.py):41 | documented |
| LocalSTCrossEncoder | provider_name | public | provider_name(self) -> str | [cogmem_api/engine/cross_encoder.py](https://github.com/triet4p/agent-memory-cognitive/blob/master/cogmem_api/engine/cross_encoder.py):47 | documented |
| LocalSTCrossEncoder | initialize | public | async initialize(self) -> None | [cogmem_api/engine/cross_encoder.py](https://github.com/triet4p/agent-memory-cognitive/blob/master/cogmem_api/engine/cross_encoder.py):50 | documented |
| LocalSTCrossEncoder | _predict_sync | private | _predict_sync(self, pairs: list[tuple[str, str]]) -> list[float] | [cogmem_api/engine/cross_encoder.py](https://github.com/triet4p/agent-memory-cognitive/blob/master/cogmem_api/engine/cross_encoder.py):77 | documented |
| LocalSTCrossEncoder | predict | public | async predict(self, pairs: list[tuple[str, str]]) -> list[float] | [cogmem_api/engine/cross_encoder.py](https://github.com/triet4p/agent-memory-cognitive/blob/master/cogmem_api/engine/cross_encoder.py):85 | documented |
| RRFPassthroughCrossEncoder | provider_name | public | provider_name(self) -> str | [cogmem_api/engine/cross_encoder.py](https://github.com/triet4p/agent-memory-cognitive/blob/master/cogmem_api/engine/cross_encoder.py):181 | documented |
| RRFPassthroughCrossEncoder | initialize | public | async initialize(self) -> None | [cogmem_api/engine/cross_encoder.py](https://github.com/triet4p/agent-memory-cognitive/blob/master/cogmem_api/engine/cross_encoder.py):184 | documented |
| RRFPassthroughCrossEncoder | predict | public | async predict(self, pairs: list[tuple[str, str]]) -> list[float] | [cogmem_api/engine/cross_encoder.py](https://github.com/triet4p/agent-memory-cognitive/blob/master/cogmem_api/engine/cross_encoder.py):187 | documented |
| RemoteTEICrossEncoder | __init__ | private | __init__(self, base_url: str, timeout: float=30.0, batch_size: int=128, max_concurrent: int=8) | [cogmem_api/engine/cross_encoder.py](https://github.com/triet4p/agent-memory-cognitive/blob/master/cogmem_api/engine/cross_encoder.py):100 | documented |
| RemoteTEICrossEncoder | provider_name | public | provider_name(self) -> str | [cogmem_api/engine/cross_encoder.py](https://github.com/triet4p/agent-memory-cognitive/blob/master/cogmem_api/engine/cross_encoder.py):111 | documented |
| RemoteTEICrossEncoder | initialize | public | async initialize(self) -> None | [cogmem_api/engine/cross_encoder.py](https://github.com/triet4p/agent-memory-cognitive/blob/master/cogmem_api/engine/cross_encoder.py):114 | documented |
| RemoteTEICrossEncoder | _rerank_batch | private | async _rerank_batch(self, query: str, texts: list[str]) -> list[tuple[int, float]] | [cogmem_api/engine/cross_encoder.py](https://github.com/triet4p/agent-memory-cognitive/blob/master/cogmem_api/engine/cross_encoder.py):123 | documented |
| RemoteTEICrossEncoder | predict | public | async predict(self, pairs: list[tuple[str, str]]) -> list[float] | [cogmem_api/engine/cross_encoder.py](https://github.com/triet4p/agent-memory-cognitive/blob/master/cogmem_api/engine/cross_encoder.py):142 | documented |

### Function: (module).create_cross_encoder_from_env
- Signature: `create_cross_encoder_from_env() -> CrossEncoderModel`
- Visibility: `public`
- Location: `cogmem_api/engine/cross_encoder.py:191`
- Purpose:
  - Thực thi nghiệp vụ `create_cross_encoder_from_env` trong phạm vi `(module)` của module `cogmem_api/engine/cross_encoder.py`.
- Inputs:
  - Theo chữ ký: `create_cross_encoder_from_env() -> CrossEncoderModel`.
- Outputs:
  - Trả về kiểu: `CrossEncoderModel`.
- Side effects:
  - Không phát hiện side effect rõ ràng từ phân tích static call graph.
- Dependency calls:
  - `get_config`, `lower`, `warning`, `RRFPassthroughCrossEncoder`, `LocalSTCrossEncoder`, `RemoteTEICrossEncoder`, `ValueError`
- Failure modes:
  - Có thể raise: `ValueError`.
- Pre-conditions:
  - Các tham số bắt buộc theo chữ ký phải hợp lệ kiểu dữ liệu trước khi gọi.
- Post-conditions:
  - Hàm kết thúc với giá trị trả về theo contract; trạng thái ngoài hàm chỉ thay đổi khi có side effect nêu ở trên.
- Verify command:
  - `Select-String -Path cogmem_api/engine/cross_encoder.py -Pattern "def create_cross_encoder_from_env|async def create_cross_encoder_from_env"`

### Function: CrossEncoderModel.provider_name
- Signature: `provider_name(self) -> str`
- Visibility: `public`
- Location: `cogmem_api/engine/cross_encoder.py:24`
- Purpose:
  - Thực thi nghiệp vụ `provider_name` trong phạm vi `CrossEncoderModel` của module `cogmem_api/engine/cross_encoder.py`.
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
  - `Select-String -Path cogmem_api/engine/cross_encoder.py -Pattern "def provider_name|async def provider_name"`

### Function: CrossEncoderModel.initialize
- Signature: `async initialize(self) -> None`
- Visibility: `public`
- Location: `cogmem_api/engine/cross_encoder.py:28`
- Purpose:
  - Thực thi nghiệp vụ `initialize` trong phạm vi `CrossEncoderModel` của module `cogmem_api/engine/cross_encoder.py`.
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
  - `Select-String -Path cogmem_api/engine/cross_encoder.py -Pattern "def initialize|async def initialize"`

### Function: CrossEncoderModel.predict
- Signature: `async predict(self, pairs: list[tuple[str, str]]) -> list[float]`
- Visibility: `public`
- Location: `cogmem_api/engine/cross_encoder.py:32`
- Purpose:
  - Thực thi nghiệp vụ `predict` trong phạm vi `CrossEncoderModel` của module `cogmem_api/engine/cross_encoder.py`.
- Inputs:
  - Theo chữ ký: `async predict(self, pairs: list[tuple[str, str]]) -> list[float]`.
- Outputs:
  - Trả về kiểu: `list[float]`.
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
  - `Select-String -Path cogmem_api/engine/cross_encoder.py -Pattern "def predict|async def predict"`

### Function: LocalSTCrossEncoder.__init__
- Signature: `__init__(self, model_name: str, max_concurrent: int=4)`
- Visibility: `private`
- Location: `cogmem_api/engine/cross_encoder.py:41`
- Purpose:
  - Thực thi nghiệp vụ `__init__` trong phạm vi `LocalSTCrossEncoder` của module `cogmem_api/engine/cross_encoder.py`.
- Inputs:
  - Theo chữ ký: `__init__(self, model_name: str, max_concurrent: int=4)`.
- Outputs:
  - Không khai báo kiểu trả về tường minh; hành vi phụ thuộc implementation.
- Side effects:
  - Không phát hiện side effect rõ ràng từ phân tích static call graph.
- Dependency calls:
  - `max`
- Failure modes:
  - Không phát hiện raise tường minh; lỗi có thể phát sinh từ dependency gọi bên trong.
- Pre-conditions:
  - Các tham số bắt buộc theo chữ ký phải hợp lệ kiểu dữ liệu trước khi gọi.
- Post-conditions:
  - Hàm kết thúc với giá trị trả về theo contract; trạng thái ngoài hàm chỉ thay đổi khi có side effect nêu ở trên.
- Verify command:
  - `Select-String -Path cogmem_api/engine/cross_encoder.py -Pattern "def __init__|async def __init__"`

### Function: LocalSTCrossEncoder.provider_name
- Signature: `provider_name(self) -> str`
- Visibility: `public`
- Location: `cogmem_api/engine/cross_encoder.py:47`
- Purpose:
  - Thực thi nghiệp vụ `provider_name` trong phạm vi `LocalSTCrossEncoder` của module `cogmem_api/engine/cross_encoder.py`.
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
  - `Select-String -Path cogmem_api/engine/cross_encoder.py -Pattern "def provider_name|async def provider_name"`

### Function: LocalSTCrossEncoder.initialize
- Signature: `async initialize(self) -> None`
- Visibility: `public`
- Location: `cogmem_api/engine/cross_encoder.py:50`
- Purpose:
  - Thực thi nghiệp vụ `initialize` trong phạm vi `LocalSTCrossEncoder` của module `cogmem_api/engine/cross_encoder.py`.
- Inputs:
  - Theo chữ ký: `async initialize(self) -> None`.
- Outputs:
  - Trả về kiểu: `None`.
- Side effects:
  - Không phát hiện side effect rõ ràng từ phân tích static call graph.
- Dependency calls:
  - `info`, `import_module`, `getattr`, `catch_warnings`, `filterwarnings`, `CrossEncoder`, `ThreadPoolExecutor`, `ImportError`
- Failure modes:
  - Có thể raise: `ImportError`.
- Pre-conditions:
  - Các tham số bắt buộc theo chữ ký phải hợp lệ kiểu dữ liệu trước khi gọi.
- Post-conditions:
  - Hàm kết thúc với giá trị trả về theo contract; trạng thái ngoài hàm chỉ thay đổi khi có side effect nêu ở trên.
- Verify command:
  - `Select-String -Path cogmem_api/engine/cross_encoder.py -Pattern "def initialize|async def initialize"`

### Function: LocalSTCrossEncoder._predict_sync
- Signature: `_predict_sync(self, pairs: list[tuple[str, str]]) -> list[float]`
- Visibility: `private`
- Location: `cogmem_api/engine/cross_encoder.py:77`
- Purpose:
  - Thực thi nghiệp vụ `_predict_sync` trong phạm vi `LocalSTCrossEncoder` của module `cogmem_api/engine/cross_encoder.py`.
- Inputs:
  - Theo chữ ký: `_predict_sync(self, pairs: list[tuple[str, str]]) -> list[float]`.
- Outputs:
  - Trả về kiểu: `list[float]`.
- Side effects:
  - Không phát hiện side effect rõ ràng từ phân tích static call graph.
- Dependency calls:
  - `predict`, `hasattr`, `RuntimeError`, `float`, `tolist`
- Failure modes:
  - Có thể raise: `RuntimeError`.
- Pre-conditions:
  - Các tham số bắt buộc theo chữ ký phải hợp lệ kiểu dữ liệu trước khi gọi.
- Post-conditions:
  - Hàm kết thúc với giá trị trả về theo contract; trạng thái ngoài hàm chỉ thay đổi khi có side effect nêu ở trên.
- Verify command:
  - `Select-String -Path cogmem_api/engine/cross_encoder.py -Pattern "def _predict_sync|async def _predict_sync"`

### Function: LocalSTCrossEncoder.predict
- Signature: `async predict(self, pairs: list[tuple[str, str]]) -> list[float]`
- Visibility: `public`
- Location: `cogmem_api/engine/cross_encoder.py:85`
- Purpose:
  - Thực thi nghiệp vụ `predict` trong phạm vi `LocalSTCrossEncoder` của module `cogmem_api/engine/cross_encoder.py`.
- Inputs:
  - Theo chữ ký: `async predict(self, pairs: list[tuple[str, str]]) -> list[float]`.
- Outputs:
  - Trả về kiểu: `list[float]`.
- Side effects:
  - Không phát hiện side effect rõ ràng từ phân tích static call graph.
- Dependency calls:
  - `get_event_loop`, `RuntimeError`, `run_in_executor`
- Failure modes:
  - Có thể raise: `RuntimeError`.
- Pre-conditions:
  - Các tham số bắt buộc theo chữ ký phải hợp lệ kiểu dữ liệu trước khi gọi.
- Post-conditions:
  - Hàm kết thúc với giá trị trả về theo contract; trạng thái ngoài hàm chỉ thay đổi khi có side effect nêu ở trên.
- Verify command:
  - `Select-String -Path cogmem_api/engine/cross_encoder.py -Pattern "def predict|async def predict"`

### Function: RRFPassthroughCrossEncoder.provider_name
- Signature: `provider_name(self) -> str`
- Visibility: `public`
- Location: `cogmem_api/engine/cross_encoder.py:181`
- Purpose:
  - Thực thi nghiệp vụ `provider_name` trong phạm vi `RRFPassthroughCrossEncoder` của module `cogmem_api/engine/cross_encoder.py`.
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
  - `Select-String -Path cogmem_api/engine/cross_encoder.py -Pattern "def provider_name|async def provider_name"`

### Function: RRFPassthroughCrossEncoder.initialize
- Signature: `async initialize(self) -> None`
- Visibility: `public`
- Location: `cogmem_api/engine/cross_encoder.py:184`
- Purpose:
  - Thực thi nghiệp vụ `initialize` trong phạm vi `RRFPassthroughCrossEncoder` của module `cogmem_api/engine/cross_encoder.py`.
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
  - `Select-String -Path cogmem_api/engine/cross_encoder.py -Pattern "def initialize|async def initialize"`

### Function: RRFPassthroughCrossEncoder.predict
- Signature: `async predict(self, pairs: list[tuple[str, str]]) -> list[float]`
- Visibility: `public`
- Location: `cogmem_api/engine/cross_encoder.py:187`
- Purpose:
  - Thực thi nghiệp vụ `predict` trong phạm vi `RRFPassthroughCrossEncoder` của module `cogmem_api/engine/cross_encoder.py`.
- Inputs:
  - Theo chữ ký: `async predict(self, pairs: list[tuple[str, str]]) -> list[float]`.
- Outputs:
  - Trả về kiểu: `list[float]`.
- Side effects:
  - Không phát hiện side effect rõ ràng từ phân tích static call graph.
- Dependency calls:
  - `len`
- Failure modes:
  - Không phát hiện raise tường minh; lỗi có thể phát sinh từ dependency gọi bên trong.
- Pre-conditions:
  - Các tham số bắt buộc theo chữ ký phải hợp lệ kiểu dữ liệu trước khi gọi.
- Post-conditions:
  - Hàm kết thúc với giá trị trả về theo contract; trạng thái ngoài hàm chỉ thay đổi khi có side effect nêu ở trên.
- Verify command:
  - `Select-String -Path cogmem_api/engine/cross_encoder.py -Pattern "def predict|async def predict"`

### Function: RemoteTEICrossEncoder.__init__
- Signature: `__init__(self, base_url: str, timeout: float=30.0, batch_size: int=128, max_concurrent: int=8)`
- Visibility: `private`
- Location: `cogmem_api/engine/cross_encoder.py:100`
- Purpose:
  - Thực thi nghiệp vụ `__init__` trong phạm vi `RemoteTEICrossEncoder` của module `cogmem_api/engine/cross_encoder.py`.
- Inputs:
  - Theo chữ ký: `__init__(self, base_url: str, timeout: float=30.0, batch_size: int=128, max_concurrent: int=8)`.
- Outputs:
  - Không khai báo kiểu trả về tường minh; hành vi phụ thuộc implementation.
- Side effects:
  - Không phát hiện side effect rõ ràng từ phân tích static call graph.
- Dependency calls:
  - `rstrip`, `max`, `Semaphore`
- Failure modes:
  - Không phát hiện raise tường minh; lỗi có thể phát sinh từ dependency gọi bên trong.
- Pre-conditions:
  - Các tham số bắt buộc theo chữ ký phải hợp lệ kiểu dữ liệu trước khi gọi.
- Post-conditions:
  - Hàm kết thúc với giá trị trả về theo contract; trạng thái ngoài hàm chỉ thay đổi khi có side effect nêu ở trên.
- Verify command:
  - `Select-String -Path cogmem_api/engine/cross_encoder.py -Pattern "def __init__|async def __init__"`

### Function: RemoteTEICrossEncoder.provider_name
- Signature: `provider_name(self) -> str`
- Visibility: `public`
- Location: `cogmem_api/engine/cross_encoder.py:111`
- Purpose:
  - Thực thi nghiệp vụ `provider_name` trong phạm vi `RemoteTEICrossEncoder` của module `cogmem_api/engine/cross_encoder.py`.
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
  - `Select-String -Path cogmem_api/engine/cross_encoder.py -Pattern "def provider_name|async def provider_name"`

### Function: RemoteTEICrossEncoder.initialize
- Signature: `async initialize(self) -> None`
- Visibility: `public`
- Location: `cogmem_api/engine/cross_encoder.py:114`
- Purpose:
  - Thực thi nghiệp vụ `initialize` trong phạm vi `RemoteTEICrossEncoder` của module `cogmem_api/engine/cross_encoder.py`.
- Inputs:
  - Theo chữ ký: `async initialize(self) -> None`.
- Outputs:
  - Trả về kiểu: `None`.
- Side effects:
  - Không phát hiện side effect rõ ràng từ phân tích static call graph.
- Dependency calls:
  - `AsyncClient`, `raise_for_status`, `info`, `get`
- Failure modes:
  - Không phát hiện raise tường minh; lỗi có thể phát sinh từ dependency gọi bên trong.
- Pre-conditions:
  - Các tham số bắt buộc theo chữ ký phải hợp lệ kiểu dữ liệu trước khi gọi.
- Post-conditions:
  - Hàm kết thúc với giá trị trả về theo contract; trạng thái ngoài hàm chỉ thay đổi khi có side effect nêu ở trên.
- Verify command:
  - `Select-String -Path cogmem_api/engine/cross_encoder.py -Pattern "def initialize|async def initialize"`

### Function: RemoteTEICrossEncoder._rerank_batch
- Signature: `async _rerank_batch(self, query: str, texts: list[str]) -> list[tuple[int, float]]`
- Visibility: `private`
- Location: `cogmem_api/engine/cross_encoder.py:123`
- Purpose:
  - Thực thi nghiệp vụ `_rerank_batch` trong phạm vi `RemoteTEICrossEncoder` của module `cogmem_api/engine/cross_encoder.py`.
- Inputs:
  - Theo chữ ký: `async _rerank_batch(self, query: str, texts: list[str]) -> list[tuple[int, float]]`.
- Outputs:
  - Trả về kiểu: `list[tuple[int, float]]`.
- Side effects:
  - Có khả năng tạo side effect qua call `post`.
- Dependency calls:
  - `RuntimeError`, `Semaphore`, `raise_for_status`, `json`, `post`, `int`, `float`
- Failure modes:
  - Có thể raise: `RuntimeError`.
- Pre-conditions:
  - Các tham số bắt buộc theo chữ ký phải hợp lệ kiểu dữ liệu trước khi gọi.
- Post-conditions:
  - Hàm kết thúc với giá trị trả về theo contract; trạng thái ngoài hàm chỉ thay đổi khi có side effect nêu ở trên.
- Verify command:
  - `Select-String -Path cogmem_api/engine/cross_encoder.py -Pattern "def _rerank_batch|async def _rerank_batch"`

### Function: RemoteTEICrossEncoder.predict
- Signature: `async predict(self, pairs: list[tuple[str, str]]) -> list[float]`
- Visibility: `public`
- Location: `cogmem_api/engine/cross_encoder.py:142`
- Purpose:
  - Thực thi nghiệp vụ `predict` trong phạm vi `RemoteTEICrossEncoder` của module `cogmem_api/engine/cross_encoder.py`.
- Inputs:
  - Theo chữ ký: `async predict(self, pairs: list[tuple[str, str]]) -> list[float]`.
- Outputs:
  - Trả về kiểu: `list[float]`.
- Side effects:
  - Không phát hiện side effect rõ ràng từ phân tích static call graph.
- Dependency calls:
  - `enumerate`, `items`, `zip`, `RuntimeError`, `append`, `range`, `len`, `gather`, `float`, `setdefault`, `_rerank_batch`
- Failure modes:
  - Có thể raise: `RuntimeError`.
- Pre-conditions:
  - Các tham số bắt buộc theo chữ ký phải hợp lệ kiểu dữ liệu trước khi gọi.
- Post-conditions:
  - Hàm kết thúc với giá trị trả về theo contract; trạng thái ngoài hàm chỉ thay đổi khi có side effect nêu ở trên.
- Verify command:
  - `Select-String -Path cogmem_api/engine/cross_encoder.py -Pattern "def predict|async def predict"`

## Failure modes
- Inventory drift: hàm mới trong source nhưng chưa có deep-dive section tương ứng.
- Signature drift: refactor chữ ký hàm nhưng không cập nhật docs gây lệch contract.
- Verify command sai path hoặc sai tên hàm khiến khó truy vết nhanh trong review.

## Verify commands
- `uv run python tests/artifacts/test_task719_function_deep_dive.py`
- `Select-String -Path tutorials/functions/cogmem_api_engine_cross_encoder.md -Pattern "### Function:"`
- `Select-String -Path tutorials/functions/cogmem_api_engine_cross_encoder.md -Pattern "- Verify command:"`

