## Plan: CogMem Migration End-to-End

Mục tiêu là triển khai CogMem theo mô hình fork-isolated từ HINDSIGHT sang cogmem_api, đi theo Sprint và Atomic Task. Mỗi task đều có output bắt buộc (code + artifact) và chiến lược kiểm tra 3 lớp: Drift Check, Behavioral Testing, Isolation Check.

**Steps**
1. Sprint 0 - Khóa phạm vi và chuẩn hóa quy trình thực thi. Atomic Task T0.1: chốt baseline và mapping module nguồn; output gồm logs/task_001_summary.md mô tả phạm vi copy-first và tests/artifacts/test_task001_inventory.py kiểm tra hiện trạng file/enum/schema; verification gồm Drift so với docs/CogMem-Idea.md và hindsight_api/models.py, Behavioral kiểm tra script không fail, Isolation kiểm tra cogmem_api chưa import hindsight_api. *khởi tạo cho toàn bộ sprint sau*
2. Sprint 0 - Atomic Task T0.2: thiết lập convention artifact và đường chạy eval/test; output gồm logs/task_002_summary.md + tests/artifacts/test_task002_artifact_conventions.py; verification gồm Drift với AGENTS.md (đúng cấu trúc artifact), Behavioral xác nhận tạo/ghi đúng thư mục logs và tests/artifacts, Isolation xác nhận artifact test không phụ thuộc hindsight_api runtime.
3. Sprint 1 - Nền tảng schema fork. Atomic Task T1.1: fork schema lõi từ hindsight_api/models.py sang cogmem_api/models.py và đổi namespace; output gồm cogmem_api/models.py, logs/task_101_summary.md, tests/artifacts/test_task101_schema_fork.py; verification gồm Drift diff enum/fact/link giữ tương thích hạ tầng nhưng mở rộng đúng idea, Behavioral test import model + metadata table creation compile được, Isolation check bằng grep import path chỉ còn cogmem_api.*. *phụ thuộc bước 1-2*
4. Sprint 1 - Atomic Task T1.2: thêm Lossless Metadata (raw_snippet) và mở rộng fact/network types cho 6 mạng CogMem (world/experience/opinion/habit/intention/action_effect) + transition typing; output gồm migration mới ở cogmem_api/alembic/versions/, cập nhật cogmem_api/models.py, logs/task_102_summary.md, tests/artifacts/test_task102_schema_extensions.py; verification gồm Drift đối chiếu idea section 3.1-3.2 và giữ nguyên cột hạ tầng cũ, Behavioral test migration upgrade/downgrade + assert cột/enum mới, Isolation check chạy model import không dùng hindsight_api.
5. Sprint 1 - Atomic Task T1.3: fork db utils + memory engine khung để cogmem_api chạy độc lập; output gồm cogmem_api/engine/db_utils.py, cogmem_api/engine/memory_engine.py, logs/task_103_summary.md, tests/artifacts/test_task103_engine_bootstrap.py; verification gồm Drift so với hindsight_api/engine/db_utils.py và memory_engine.py không đổi sai behavior hạ tầng, Behavioral test khởi tạo engine + schema qualification, Isolation check query namespace và import chain.
6. Sprint 2 - Core retain pipeline fork. Atomic Task T2.1: fork retain pipeline nền (orchestrator, fact_extraction, fact_storage, entity_processing, link_creation, embedding_processing) sang cogmem_api/engine/retain; output gồm các file retain mới + logs/task_201_summary.md + tests/artifacts/test_task201_retain_baseline.py; verification gồm Drift theo module nguồn tương ứng trong hindsight_api/engine/retain, Behavioral test retain mẫu một batch hội thoại nhỏ tạo được world/experience/opinion/habit/intention/action_effect nodes (không có observation), Isolation check không import hindsight_api.*.
7. Sprint 2 - Atomic Task T2.2: thêm Habit Network + S-R links; output gồm cập nhật extraction/link rules trong cogmem_api/engine/retain, logs/task_202_summary.md, tests/artifacts/test_task202_habit_network.py; verification gồm Drift đảm bảo chỉ mở rộng logic nghiệp vụ, Behavioral test input chứa pattern lặp tạo node habit + edge s_r_link đúng entity, Isolation check toàn bộ resolver chạy trong cogmem_api.
8. Sprint 2 - Atomic Task T2.3: thêm Intention Network + lifecycle transition rules (fulfilled_by, abandoned, triggered, enabled_by); output gồm logic lifecycle ở retain/link layer, logs/task_203_summary.md, tests/artifacts/test_task203_intention_lifecycle.py; verification gồm Drift đối chiếu đặc tả lifecycle trong idea, Behavioral test chuỗi planning->fulfilled tạo experience liên kết đúng và abandoned không tạo experience mới, Isolation check import + runtime độc lập.
9. Sprint 2 - Atomic Task T2.4: thêm Action-Effect Network + A-O causal edges; output gồm parser/extractor cho precondition-action-outcome, cập nhật link creation, logs/task_204_summary.md, tests/artifacts/test_task204_action_effect.py; verification gồm Drift so với schema mục tiêu và giữ nguyên flow cũ, Behavioral test causal utterance tạo node action_effect + edge a_o_causal + confidence/devalue flag hợp lệ, Isolation check dependency graph.
10. Sprint 3 - Retrieval intelligence fork. Atomic Task T3.1: fork search baseline (retrieval, graph_retrieval/mpfp/link_expansion, fusion, reranking, temporal_extraction, types) sang cogmem_api/engine/search; output gồm cụm search files + logs/task_301_summary.md + tests/artifacts/test_task301_search_fork.py; verification gồm Drift bám behavior HINDSIGHT trước khi thêm cải tiến, Behavioral test recall smoke cho 4-channel chạy end-to-end, Isolation check grep import.
11. Sprint 3 - Atomic Task T3.2: thay MAX bằng SUM spreading activation + 3 cycle guards (refractory, firing quota, saturation A_max); output gồm cập nhật cogmem_api/engine/search/graph_retrieval.py (và/hoặc mpfp_retrieval.py), logs/task_302_summary.md, tests/artifacts/test_task302_sum_activation.py; verification gồm Drift kiểm tra chỉ thay propagation core và không phá truy hồi khác, Behavioral test bộ case multi-hop có nhiều đường bằng chứng và test anti-loop không phân kỳ, Isolation check không phụ thuộc class từ hindsight_api.
12. Sprint 3 - Atomic Task T3.3: Adaptive Query Routing với 6 query types và trọng số RRF động, bao gồm rule Causal/Prospective; output gồm cập nhật cogmem_api/engine/query_analyzer.py, cogmem_api/engine/search/fusion.py, cogmem_api/engine/search/retrieval.py, logs/task_303_summary.md, tests/artifacts/test_task303_adaptive_router.py; verification gồm Drift so với RRF baseline để bảo toàn đường chạy cũ khi fallback semantic, Behavioral test ma trận query type -> weights -> ranking outcome đúng kỳ vọng, Isolation check import/runtime.
13. Sprint 4 - Reflect lazy synthesis cho mạng mới. Atomic Task T4.1: fork reflect tối thiểu cần thiết và mở rộng xử lý node mới, không mang theo pipeline consolidation chủ động; output gồm cogmem_api/engine/reflect/*, logs/task_401_summary.md, tests/artifacts/test_task401_reflect_lazy_synthesis.py; verification gồm Drift bảo toàn stripped-down CARA behavior quan trọng, Behavioral test trả lời có thể tổng hợp thông tin lazy từ facts + raw_snippet sau retrieve, Isolation check công cụ reflect chỉ gọi cogmem_api engine.
14. Sprint 5 - Evaluation và ablation có kiểm soát. Atomic Task T5.1: dựng harness E1-E7 trên subset LongMemEval/LoCoMo; output gồm scripts/eval_cogmem.py, scripts/ablation_runner.py, logs/task_501_summary.md, tests/artifacts/test_task501_eval_harness.py, logs/eval/*.json; verification gồm Drift xác nhận metric end-to-end accuracy cùng judge setup định nghĩa trong idea, Behavioral test chạy ít nhất một mini-split và sinh thống kê per-category, Isolation check runner không gọi package hindsight_api trực tiếp.
15. Sprint 5 - Atomic Task T5.2: báo cáo phân tích lỗi và quyết định phạm vi E8 (hierarchical KG); output gồm logs/task_502_summary.md và logs/error_analysis_report.md; verification gồm Drift kiểm tra kết luận dựa trên artifact thực nghiệm, Behavioral kiểm tra report có đủ category-level wins/losses, Isolation check không phát sinh phụ thuộc mới ngoài phạm vi.

**Relevant files**
- f:/ai-ml/agent-memory-cognitive/AGENTS.md - quy trình bắt buộc về sprint/task/artifact/verification
- f:/ai-ml/agent-memory-cognitive/docs/CogMem-Idea.md - đặc tả đóng góp kỹ thuật và thứ tự thực nghiệm E1-E8
- f:/ai-ml/agent-memory-cognitive/hindsight_api/models.py - schema nguồn để fork và kiểm tra drift
- f:/ai-ml/agent-memory-cognitive/hindsight_api/engine/db_utils.py - hạ tầng DB nguồn
- f:/ai-ml/agent-memory-cognitive/hindsight_api/engine/memory_engine.py - orchestration retain/recall nguồn
- f:/ai-ml/agent-memory-cognitive/hindsight_api/engine/retain/orchestrator.py - retain coordinator nguồn
- f:/ai-ml/agent-memory-cognitive/hindsight_api/engine/retain/fact_extraction.py - extraction nguồn
- f:/ai-ml/agent-memory-cognitive/hindsight_api/engine/retain/link_creation.py - edge creation nguồn
- f:/ai-ml/agent-memory-cognitive/hindsight_api/engine/search/retrieval.py - recall orchestrator nguồn
- f:/ai-ml/agent-memory-cognitive/hindsight_api/engine/search/graph_retrieval.py - propagation nguồn (MAX -> SUM)
- f:/ai-ml/agent-memory-cognitive/hindsight_api/engine/search/fusion.py - RRF baseline nguồn
- f:/ai-ml/agent-memory-cognitive/hindsight_api/engine/query_analyzer.py - query analysis baseline
- f:/ai-ml/agent-memory-cognitive/hindsight_api/engine/reflect/agent.py - reflect baseline
- f:/ai-ml/agent-memory-cognitive/scripts/test_hindsight.py - mẫu script eval hiện hữu
- f:/ai-ml/agent-memory-cognitive/pyproject.toml - dependency/tooling surface

**Verification**
1. Chuẩn Drift Check toàn dự án: mỗi task có bảng so sánh Source (hindsight_api) vs Fork (cogmem_api) trong logs/task_<id>_summary.md, chỉ rõ phần hạ tầng giữ nguyên và phần nghiệp vụ thay đổi.
2. Chuẩn Behavioral Testing toàn dự án: mỗi task có tests/artifacts/test_<task_name>.py chạy độc lập bằng uv run python <script> với assert input/output rõ ràng.
3. Chuẩn Isolation Check toàn dự án: sau mỗi task chạy tìm kiếm import chéo (import hindsight_api hoặc from hindsight_api) trong cogmem_api và fail nếu còn.
4. Regression checkpoints theo sprint: cuối mỗi sprint chạy lại toàn bộ tests/artifacts liên quan sprint đó và cập nhật log tổng hợp.
5. Evaluation checkpoints: E1 làm mốc; E2-E7 chạy cùng pipeline judge/metric để so sánh công bằng theo category.

**Decisions**
- Bao gồm trong phạm vi hiện tại: Contribution 1-4 + E1-E7 theo docs/CogMem-Idea.md.
- Tạm loại khỏi phạm vi bắt buộc: E8 Hierarchical KG, chỉ thực hiện khi sprint trước đạt ổn định.
- Chiến lược kiến trúc: fork-then-modify, tuyệt đối không import trực tiếp từ hindsight_api vào cogmem_api.
- Chuẩn artifact bắt buộc cho mỗi atomic task: logs/task_<id>_summary.md và tests/artifacts/test_<task_name>.py.

**Further Considerations**
1. Threshold cho Habit và cycle guards sẽ được cố định bằng config và hiệu chỉnh sau E1 dựa trên kết quả subset, không hardcode rải rác.
2. Raw snippet storage mặc định để trong DB column trước; nếu phát sinh vấn đề kích thước sẽ tách sang storage abstraction ở sprint sau.
3. Nếu cần rút ngắn thời gian, có thể chạy song song nhóm task T2.2/T2.3/T2.4 sau khi T2.1 ổn định vì chúng chia sẻ retain nền nhưng ít phụ thuộc trực tiếp vào nhau.