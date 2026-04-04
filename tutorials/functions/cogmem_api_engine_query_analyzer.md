# Function Deep Dive - cogmem_api/engine/query_analyzer.py

## Purpose
- Mô tả chi tiết các hàm phân loại query và trích temporal constraint.
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
- Source module: `cogmem_api/engine/query_analyzer.py`.
- Public/private breakdown: public=9, private=8.
- Bối cảnh chi tiết từng hàm nằm ở phần Function inventory bên dưới.

## Function inventory (public/private)
| Owner | Function | Visibility | Signature | Location | Deep-dive status |
|---|---|---|---|---|---|
| (module) | get_adaptive_rrf_weights | public | get_adaptive_rrf_weights(query_type: QueryType) -> dict[str, float] | cogmem_api/engine/query_analyzer.py:83 | documented |
| (module) | classify_query_type | public | classify_query_type(query: str, temporal_constraint: TemporalConstraint \| None=None) -> QueryType | cogmem_api/engine/query_analyzer.py:94 | documented |
| (module) | build_query_analysis | public | build_query_analysis(query: str, temporal_constraint: TemporalConstraint \| None=None) -> QueryAnalysis | cogmem_api/engine/query_analyzer.py:112 | documented |
| DateparserQueryAnalyzer | __init__ | private | __init__(self) | cogmem_api/engine/query_analyzer.py:168 | documented |
| DateparserQueryAnalyzer | load | public | load(self) -> None | cogmem_api/engine/query_analyzer.py:172 | documented |
| DateparserQueryAnalyzer | analyze | public | analyze(self, query: str, reference_date: datetime \| None=None) -> QueryAnalysis | cogmem_api/engine/query_analyzer.py:185 | documented |
| DateparserQueryAnalyzer | _extract_period | private | _extract_period(self, query: str, reference_date: datetime) -> TemporalConstraint \| None | cogmem_api/engine/query_analyzer.py:242 | documented |
| QueryAnalyzer | load | public | load(self) -> None | cogmem_api/engine/query_analyzer.py:131 | documented |
| QueryAnalyzer | analyze | public | analyze(self, query: str, reference_date: datetime \| None=None) -> QueryAnalysis | cogmem_api/engine/query_analyzer.py:141 | documented |
| TemporalConstraint | __str__ | private | __str__(self) -> str | cogmem_api/engine/query_analyzer.py:62 | documented |
| TransformerQueryAnalyzer | __init__ | private | __init__(self, model_name: str='google/flan-t5-small', device: str='cpu') | cogmem_api/engine/query_analyzer.py:376 | documented |
| TransformerQueryAnalyzer | load | public | load(self) -> None | cogmem_api/engine/query_analyzer.py:391 | documented |
| TransformerQueryAnalyzer | _load_model | private | _load_model(self) | cogmem_api/engine/query_analyzer.py:410 | documented |
| TransformerQueryAnalyzer | _extract_with_rules | private | _extract_with_rules(self, query: str, reference_date: datetime) -> TemporalConstraint \| None | cogmem_api/engine/query_analyzer.py:414 | documented |
| TransformerQueryAnalyzer | analyze | public | analyze(self, query: str, reference_date: datetime \| None=None) -> QueryAnalysis | cogmem_api/engine/query_analyzer.py:498 | documented |
| TransformerQueryAnalyzer | _no_grad | private | _no_grad(self) | cogmem_api/engine/query_analyzer.py:555 | documented |
| TransformerQueryAnalyzer | _parse_generated_output | private | _parse_generated_output(self, result: str, reference_date: datetime) -> TemporalConstraint \| None | cogmem_api/engine/query_analyzer.py:566 | documented |

### Function: (module).get_adaptive_rrf_weights
- Signature: `get_adaptive_rrf_weights(query_type: QueryType) -> dict[str, float]`
- Visibility: `public`
- Location: `cogmem_api/engine/query_analyzer.py:83`
- Purpose:
  - Thực thi nghiệp vụ `get_adaptive_rrf_weights` trong phạm vi `(module)` của module `cogmem_api/engine/query_analyzer.py`.
- Inputs:
  - Theo chữ ký: `get_adaptive_rrf_weights(query_type: QueryType) -> dict[str, float]`.
- Outputs:
  - Trả về kiểu: `dict[str, float]`.
- Side effects:
  - Không phát hiện side effect rõ ràng từ phân tích static call graph.
- Dependency calls:
  - `get`, `max`, `sum`, `dict`, `float`, `values`
- Failure modes:
  - Không phát hiện raise tường minh; lỗi có thể phát sinh từ dependency gọi bên trong.
- Pre-conditions:
  - Các tham số bắt buộc theo chữ ký phải hợp lệ kiểu dữ liệu trước khi gọi.
- Post-conditions:
  - Hàm kết thúc với giá trị trả về theo contract; trạng thái ngoài hàm chỉ thay đổi khi có side effect nêu ở trên.
- Example input/output:
  - Input mẫu: sử dụng tham số tối thiểu hợp lệ theo signature (xem test artifact và module dossier).
  - Output kỳ vọng: đúng kiểu trả về, không vi phạm pre/post-conditions.
- Verify command:
  - `Select-String -Path cogmem_api/engine/query_analyzer.py -Pattern "def get_adaptive_rrf_weights|async def get_adaptive_rrf_weights"`

### Function: (module).classify_query_type
- Signature: `classify_query_type(query: str, temporal_constraint: TemporalConstraint | None=None) -> QueryType`
- Visibility: `public`
- Location: `cogmem_api/engine/query_analyzer.py:94`
- Purpose:
  - Thực thi nghiệp vụ `classify_query_type` trong phạm vi `(module)` của module `cogmem_api/engine/query_analyzer.py`.
- Inputs:
  - Theo chữ ký: `classify_query_type(query: str, temporal_constraint: TemporalConstraint | None=None) -> QueryType`.
- Outputs:
  - Trả về kiểu: `QueryType`.
- Side effects:
  - Không phát hiện side effect rõ ràng từ phân tích static call graph.
- Dependency calls:
  - `lower`, `search`, `strip`
- Failure modes:
  - Không phát hiện raise tường minh; lỗi có thể phát sinh từ dependency gọi bên trong.
- Pre-conditions:
  - Các tham số bắt buộc theo chữ ký phải hợp lệ kiểu dữ liệu trước khi gọi.
- Post-conditions:
  - Hàm kết thúc với giá trị trả về theo contract; trạng thái ngoài hàm chỉ thay đổi khi có side effect nêu ở trên.
- Example input/output:
  - Input mẫu: sử dụng tham số tối thiểu hợp lệ theo signature (xem test artifact và module dossier).
  - Output kỳ vọng: đúng kiểu trả về, không vi phạm pre/post-conditions.
- Verify command:
  - `Select-String -Path cogmem_api/engine/query_analyzer.py -Pattern "def classify_query_type|async def classify_query_type"`

### Function: (module).build_query_analysis
- Signature: `build_query_analysis(query: str, temporal_constraint: TemporalConstraint | None=None) -> QueryAnalysis`
- Visibility: `public`
- Location: `cogmem_api/engine/query_analyzer.py:112`
- Purpose:
  - Thực thi nghiệp vụ `build_query_analysis` trong phạm vi `(module)` của module `cogmem_api/engine/query_analyzer.py`.
- Inputs:
  - Theo chữ ký: `build_query_analysis(query: str, temporal_constraint: TemporalConstraint | None=None) -> QueryAnalysis`.
- Outputs:
  - Trả về kiểu: `QueryAnalysis`.
- Side effects:
  - Không phát hiện side effect rõ ràng từ phân tích static call graph.
- Dependency calls:
  - `classify_query_type`, `QueryAnalysis`, `get_adaptive_rrf_weights`
- Failure modes:
  - Không phát hiện raise tường minh; lỗi có thể phát sinh từ dependency gọi bên trong.
- Pre-conditions:
  - Các tham số bắt buộc theo chữ ký phải hợp lệ kiểu dữ liệu trước khi gọi.
- Post-conditions:
  - Hàm kết thúc với giá trị trả về theo contract; trạng thái ngoài hàm chỉ thay đổi khi có side effect nêu ở trên.
- Example input/output:
  - Input mẫu: sử dụng tham số tối thiểu hợp lệ theo signature (xem test artifact và module dossier).
  - Output kỳ vọng: đúng kiểu trả về, không vi phạm pre/post-conditions.
- Verify command:
  - `Select-String -Path cogmem_api/engine/query_analyzer.py -Pattern "def build_query_analysis|async def build_query_analysis"`

### Function: DateparserQueryAnalyzer.__init__
- Signature: `__init__(self)`
- Visibility: `private`
- Location: `cogmem_api/engine/query_analyzer.py:168`
- Purpose:
  - Thực thi nghiệp vụ `__init__` trong phạm vi `DateparserQueryAnalyzer` của module `cogmem_api/engine/query_analyzer.py`.
- Inputs:
  - Theo chữ ký: `__init__(self)`.
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
  - `Select-String -Path cogmem_api/engine/query_analyzer.py -Pattern "def __init__|async def __init__"`

### Function: DateparserQueryAnalyzer.load
- Signature: `load(self) -> None`
- Visibility: `public`
- Location: `cogmem_api/engine/query_analyzer.py:172`
- Purpose:
  - Thực thi nghiệp vụ `load` trong phạm vi `DateparserQueryAnalyzer` của module `cogmem_api/engine/query_analyzer.py`.
- Inputs:
  - Theo chữ ký: `load(self) -> None`.
- Outputs:
  - Trả về kiểu: `None`.
- Side effects:
  - Không phát hiện side effect rõ ràng từ phân tích static call graph.
- Dependency calls:
  - `_search_dates`
- Failure modes:
  - Không phát hiện raise tường minh; lỗi có thể phát sinh từ dependency gọi bên trong.
- Pre-conditions:
  - Các tham số bắt buộc theo chữ ký phải hợp lệ kiểu dữ liệu trước khi gọi.
- Post-conditions:
  - Hàm kết thúc với giá trị trả về theo contract; trạng thái ngoài hàm chỉ thay đổi khi có side effect nêu ở trên.
- Example input/output:
  - Input mẫu: sử dụng tham số tối thiểu hợp lệ theo signature (xem test artifact và module dossier).
  - Output kỳ vọng: đúng kiểu trả về, không vi phạm pre/post-conditions.
- Verify command:
  - `Select-String -Path cogmem_api/engine/query_analyzer.py -Pattern "def load|async def load"`

### Function: DateparserQueryAnalyzer.analyze
- Signature: `analyze(self, query: str, reference_date: datetime | None=None) -> QueryAnalysis`
- Visibility: `public`
- Location: `cogmem_api/engine/query_analyzer.py:185`
- Purpose:
  - Thực thi nghiệp vụ `analyze` trong phạm vi `DateparserQueryAnalyzer` của module `cogmem_api/engine/query_analyzer.py`.
- Inputs:
  - Theo chữ ký: `analyze(self, query: str, reference_date: datetime | None=None) -> QueryAnalysis`.
- Outputs:
  - Trả về kiểu: `QueryAnalysis`.
- Side effects:
  - Không phát hiện side effect rõ ràng từ phân tích static call graph.
- Dependency calls:
  - `lower`, `_extract_period`, `load`, `_search_dates`, `replace`, `build_query_analysis`, `now`, `TemporalConstraint`, `len`
- Failure modes:
  - Không phát hiện raise tường minh; lỗi có thể phát sinh từ dependency gọi bên trong.
- Pre-conditions:
  - Các tham số bắt buộc theo chữ ký phải hợp lệ kiểu dữ liệu trước khi gọi.
- Post-conditions:
  - Hàm kết thúc với giá trị trả về theo contract; trạng thái ngoài hàm chỉ thay đổi khi có side effect nêu ở trên.
- Example input/output:
  - Input mẫu: sử dụng tham số tối thiểu hợp lệ theo signature (xem test artifact và module dossier).
  - Output kỳ vọng: đúng kiểu trả về, không vi phạm pre/post-conditions.
- Verify command:
  - `Select-String -Path cogmem_api/engine/query_analyzer.py -Pattern "def analyze|async def analyze"`

### Function: DateparserQueryAnalyzer._extract_period
- Signature: `_extract_period(self, query: str, reference_date: datetime) -> TemporalConstraint | None`
- Visibility: `private`
- Location: `cogmem_api/engine/query_analyzer.py:242`
- Purpose:
  - Thực thi nghiệp vụ `_extract_period` trong phạm vi `DateparserQueryAnalyzer` của module `cogmem_api/engine/query_analyzer.py`.
- Inputs:
  - Theo chữ ký: `_extract_period(self, query: str, reference_date: datetime) -> TemporalConstraint | None`.
- Outputs:
  - Trả về kiểu: `TemporalConstraint | None`.
- Side effects:
  - Không phát hiện side effect rõ ràng từ phân tích static call graph.
- Dependency calls:
  - `search`, `items`, `TemporalConstraint`, `constraint`, `replace`, `timedelta`, `datetime`, `int`, `weekday`, `group`
- Failure modes:
  - Không phát hiện raise tường minh; lỗi có thể phát sinh từ dependency gọi bên trong.
- Pre-conditions:
  - Các tham số bắt buộc theo chữ ký phải hợp lệ kiểu dữ liệu trước khi gọi.
- Post-conditions:
  - Hàm kết thúc với giá trị trả về theo contract; trạng thái ngoài hàm chỉ thay đổi khi có side effect nêu ở trên.
- Verify command:
  - `Select-String -Path cogmem_api/engine/query_analyzer.py -Pattern "def _extract_period|async def _extract_period"`

### Function: QueryAnalyzer.load
- Signature: `load(self) -> None`
- Visibility: `public`
- Location: `cogmem_api/engine/query_analyzer.py:131`
- Purpose:
  - Thực thi nghiệp vụ `load` trong phạm vi `QueryAnalyzer` của module `cogmem_api/engine/query_analyzer.py`.
- Inputs:
  - Theo chữ ký: `load(self) -> None`.
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
- Example input/output:
  - Input mẫu: sử dụng tham số tối thiểu hợp lệ theo signature (xem test artifact và module dossier).
  - Output kỳ vọng: đúng kiểu trả về, không vi phạm pre/post-conditions.
- Verify command:
  - `Select-String -Path cogmem_api/engine/query_analyzer.py -Pattern "def load|async def load"`

### Function: QueryAnalyzer.analyze
- Signature: `analyze(self, query: str, reference_date: datetime | None=None) -> QueryAnalysis`
- Visibility: `public`
- Location: `cogmem_api/engine/query_analyzer.py:141`
- Purpose:
  - Thực thi nghiệp vụ `analyze` trong phạm vi `QueryAnalyzer` của module `cogmem_api/engine/query_analyzer.py`.
- Inputs:
  - Theo chữ ký: `analyze(self, query: str, reference_date: datetime | None=None) -> QueryAnalysis`.
- Outputs:
  - Trả về kiểu: `QueryAnalysis`.
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
- Example input/output:
  - Input mẫu: sử dụng tham số tối thiểu hợp lệ theo signature (xem test artifact và module dossier).
  - Output kỳ vọng: đúng kiểu trả về, không vi phạm pre/post-conditions.
- Verify command:
  - `Select-String -Path cogmem_api/engine/query_analyzer.py -Pattern "def analyze|async def analyze"`

### Function: TemporalConstraint.__str__
- Signature: `__str__(self) -> str`
- Visibility: `private`
- Location: `cogmem_api/engine/query_analyzer.py:62`
- Purpose:
  - Thực thi nghiệp vụ `__str__` trong phạm vi `TemporalConstraint` của module `cogmem_api/engine/query_analyzer.py`.
- Inputs:
  - Theo chữ ký: `__str__(self) -> str`.
- Outputs:
  - Trả về kiểu: `str`.
- Side effects:
  - Không phát hiện side effect rõ ràng từ phân tích static call graph.
- Dependency calls:
  - `strftime`
- Failure modes:
  - Không phát hiện raise tường minh; lỗi có thể phát sinh từ dependency gọi bên trong.
- Pre-conditions:
  - Các tham số bắt buộc theo chữ ký phải hợp lệ kiểu dữ liệu trước khi gọi.
- Post-conditions:
  - Hàm kết thúc với giá trị trả về theo contract; trạng thái ngoài hàm chỉ thay đổi khi có side effect nêu ở trên.
- Verify command:
  - `Select-String -Path cogmem_api/engine/query_analyzer.py -Pattern "def __str__|async def __str__"`

### Function: TransformerQueryAnalyzer.__init__
- Signature: `__init__(self, model_name: str='google/flan-t5-small', device: str='cpu')`
- Visibility: `private`
- Location: `cogmem_api/engine/query_analyzer.py:376`
- Purpose:
  - Thực thi nghiệp vụ `__init__` trong phạm vi `TransformerQueryAnalyzer` của module `cogmem_api/engine/query_analyzer.py`.
- Inputs:
  - Theo chữ ký: `__init__(self, model_name: str='google/flan-t5-small', device: str='cpu')`.
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
  - `Select-String -Path cogmem_api/engine/query_analyzer.py -Pattern "def __init__|async def __init__"`

### Function: TransformerQueryAnalyzer.load
- Signature: `load(self) -> None`
- Visibility: `public`
- Location: `cogmem_api/engine/query_analyzer.py:391`
- Purpose:
  - Thực thi nghiệp vụ `load` trong phạm vi `TransformerQueryAnalyzer` của module `cogmem_api/engine/query_analyzer.py`.
- Inputs:
  - Theo chữ ký: `load(self) -> None`.
- Outputs:
  - Trả về kiểu: `None`.
- Side effects:
  - Không phát hiện side effect rõ ràng từ phân tích static call graph.
- Dependency calls:
  - `info`, `from_pretrained`, `to`, `eval`, `ImportError`
- Failure modes:
  - Có thể raise: `ImportError`.
- Pre-conditions:
  - Các tham số bắt buộc theo chữ ký phải hợp lệ kiểu dữ liệu trước khi gọi.
- Post-conditions:
  - Hàm kết thúc với giá trị trả về theo contract; trạng thái ngoài hàm chỉ thay đổi khi có side effect nêu ở trên.
- Example input/output:
  - Input mẫu: sử dụng tham số tối thiểu hợp lệ theo signature (xem test artifact và module dossier).
  - Output kỳ vọng: đúng kiểu trả về, không vi phạm pre/post-conditions.
- Verify command:
  - `Select-String -Path cogmem_api/engine/query_analyzer.py -Pattern "def load|async def load"`

### Function: TransformerQueryAnalyzer._load_model
- Signature: `_load_model(self)`
- Visibility: `private`
- Location: `cogmem_api/engine/query_analyzer.py:410`
- Purpose:
  - Thực thi nghiệp vụ `_load_model` trong phạm vi `TransformerQueryAnalyzer` của module `cogmem_api/engine/query_analyzer.py`.
- Inputs:
  - Theo chữ ký: `_load_model(self)`.
- Outputs:
  - Không khai báo kiểu trả về tường minh; hành vi phụ thuộc implementation.
- Side effects:
  - Không phát hiện side effect rõ ràng từ phân tích static call graph.
- Dependency calls:
  - `load`
- Failure modes:
  - Không phát hiện raise tường minh; lỗi có thể phát sinh từ dependency gọi bên trong.
- Pre-conditions:
  - Các tham số bắt buộc theo chữ ký phải hợp lệ kiểu dữ liệu trước khi gọi.
- Post-conditions:
  - Hàm kết thúc với giá trị trả về theo contract; trạng thái ngoài hàm chỉ thay đổi khi có side effect nêu ở trên.
- Verify command:
  - `Select-String -Path cogmem_api/engine/query_analyzer.py -Pattern "def _load_model|async def _load_model"`

### Function: TransformerQueryAnalyzer._extract_with_rules
- Signature: `_extract_with_rules(self, query: str, reference_date: datetime) -> TemporalConstraint | None`
- Visibility: `private`
- Location: `cogmem_api/engine/query_analyzer.py:414`
- Purpose:
  - Thực thi nghiệp vụ `_extract_with_rules` trong phạm vi `TransformerQueryAnalyzer` của module `cogmem_api/engine/query_analyzer.py`.
- Inputs:
  - Theo chữ ký: `_extract_with_rules(self, query: str, reference_date: datetime) -> TemporalConstraint | None`.
- Outputs:
  - Trả về kiểu: `TemporalConstraint | None`.
- Side effects:
  - Không phát hiện side effect rõ ràng từ phân tích static call graph.
- Dependency calls:
  - `lower`, `search`, `items`, `TemporalConstraint`, `constraint`, `replace`, `get_last_weekday`, `timedelta`, `datetime`, `int`, `weekday`, `group`
- Failure modes:
  - Không phát hiện raise tường minh; lỗi có thể phát sinh từ dependency gọi bên trong.
- Pre-conditions:
  - Các tham số bắt buộc theo chữ ký phải hợp lệ kiểu dữ liệu trước khi gọi.
- Post-conditions:
  - Hàm kết thúc với giá trị trả về theo contract; trạng thái ngoài hàm chỉ thay đổi khi có side effect nêu ở trên.
- Verify command:
  - `Select-String -Path cogmem_api/engine/query_analyzer.py -Pattern "def _extract_with_rules|async def _extract_with_rules"`

### Function: TransformerQueryAnalyzer.analyze
- Signature: `analyze(self, query: str, reference_date: datetime | None=None) -> QueryAnalysis`
- Visibility: `public`
- Location: `cogmem_api/engine/query_analyzer.py:498`
- Purpose:
  - Thực thi nghiệp vụ `analyze` trong phạm vi `TransformerQueryAnalyzer` của module `cogmem_api/engine/query_analyzer.py`.
- Inputs:
  - Theo chữ ký: `analyze(self, query: str, reference_date: datetime | None=None) -> QueryAnalysis`.
- Outputs:
  - Trả về kiểu: `QueryAnalysis`.
- Side effects:
  - Không phát hiện side effect rõ ràng từ phân tích static call graph.
- Dependency calls:
  - `_extract_with_rules`, `_load_model`, `get_last_weekday`, `_tokenizer`, `strip`, `_parse_generated_output`, `build_query_analysis`, `now`, `timedelta`, `to`, `_no_grad`, `generate`
- Failure modes:
  - Không phát hiện raise tường minh; lỗi có thể phát sinh từ dependency gọi bên trong.
- Pre-conditions:
  - Các tham số bắt buộc theo chữ ký phải hợp lệ kiểu dữ liệu trước khi gọi.
- Post-conditions:
  - Hàm kết thúc với giá trị trả về theo contract; trạng thái ngoài hàm chỉ thay đổi khi có side effect nêu ở trên.
- Example input/output:
  - Input mẫu: sử dụng tham số tối thiểu hợp lệ theo signature (xem test artifact và module dossier).
  - Output kỳ vọng: đúng kiểu trả về, không vi phạm pre/post-conditions.
- Verify command:
  - `Select-String -Path cogmem_api/engine/query_analyzer.py -Pattern "def analyze|async def analyze"`

### Function: TransformerQueryAnalyzer._no_grad
- Signature: `_no_grad(self)`
- Visibility: `private`
- Location: `cogmem_api/engine/query_analyzer.py:555`
- Purpose:
  - Thực thi nghiệp vụ `_no_grad` trong phạm vi `TransformerQueryAnalyzer` của module `cogmem_api/engine/query_analyzer.py`.
- Inputs:
  - Theo chữ ký: `_no_grad(self)`.
- Outputs:
  - Không khai báo kiểu trả về tường minh; hành vi phụ thuộc implementation.
- Side effects:
  - Không phát hiện side effect rõ ràng từ phân tích static call graph.
- Dependency calls:
  - `no_grad`, `nullcontext`
- Failure modes:
  - Không phát hiện raise tường minh; lỗi có thể phát sinh từ dependency gọi bên trong.
- Pre-conditions:
  - Các tham số bắt buộc theo chữ ký phải hợp lệ kiểu dữ liệu trước khi gọi.
- Post-conditions:
  - Hàm kết thúc với giá trị trả về theo contract; trạng thái ngoài hàm chỉ thay đổi khi có side effect nêu ở trên.
- Verify command:
  - `Select-String -Path cogmem_api/engine/query_analyzer.py -Pattern "def _no_grad|async def _no_grad"`

### Function: TransformerQueryAnalyzer._parse_generated_output
- Signature: `_parse_generated_output(self, result: str, reference_date: datetime) -> TemporalConstraint | None`
- Visibility: `private`
- Location: `cogmem_api/engine/query_analyzer.py:566`
- Purpose:
  - Thực thi nghiệp vụ `_parse_generated_output` trong phạm vi `TransformerQueryAnalyzer` của module `cogmem_api/engine/query_analyzer.py`.
- Inputs:
  - Theo chữ ký: `_parse_generated_output(self, result: str, reference_date: datetime) -> TemporalConstraint | None`.
- Outputs:
  - Trả về kiểu: `TemporalConstraint | None`.
- Side effects:
  - Không phát hiện side effect rõ ràng từ phân tích static call graph.
- Dependency calls:
  - `search`, `strip`, `group`, `strptime`, `replace`, `TemporalConstraint`, `warning`, `lower`
- Failure modes:
  - Không phát hiện raise tường minh; lỗi có thể phát sinh từ dependency gọi bên trong.
- Pre-conditions:
  - Các tham số bắt buộc theo chữ ký phải hợp lệ kiểu dữ liệu trước khi gọi.
- Post-conditions:
  - Hàm kết thúc với giá trị trả về theo contract; trạng thái ngoài hàm chỉ thay đổi khi có side effect nêu ở trên.
- Verify command:
  - `Select-String -Path cogmem_api/engine/query_analyzer.py -Pattern "def _parse_generated_output|async def _parse_generated_output"`

## Failure modes
- Inventory drift: hàm mới trong source nhưng chưa có deep-dive section tương ứng.
- Signature drift: refactor chữ ký hàm nhưng không cập nhật docs gây lệch contract.
- Verify command sai path hoặc sai tên hàm khiến khó truy vết nhanh trong review.

## Verify commands
- `uv run python tests/artifacts/test_task719_function_deep_dive.py`
- `Select-String -Path tutorials/functions/cogmem_api_engine_query_analyzer.md -Pattern "### Function:"`
- `Select-String -Path tutorials/functions/cogmem_api_engine_query_analyzer.md -Pattern "- Verify command:"`

