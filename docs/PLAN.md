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
14. Sprint 5 - Runtime packaging gate (Docker-first) trước evaluation. Atomic Task T5.1: fork runtime entrypoint cần thiết để `cogmem_api` chạy như service độc lập tương tự HINDSIGHT (CLI + ASGI app + health path), ưu tiên copy từ hindsight_api/main.py, hindsight_api/server.py, hindsight_api/api/http.py theo nguyên tắc fork-isolated; output gồm cogmem_api/main.py, cogmem_api/server.py, cogmem_api/api/*, logs/task_501_summary.md, tests/artifacts/test_task501_runtime_entrypoints.py; verification gồm Drift đối chiếu flow startup/shutdown và route tối thiểu, Behavioral test khởi tạo app + probe health endpoint local, Isolation check không import trực tiếp hindsight_api.
15. Sprint 5 - Atomic Task T5.2: hoàn thiện dependency/config packaging để chạy được trong container, bao gồm script entrypoint package (`cogmem-api`), biến môi trường runtime, và support `pg0` cho embedded DB mode; output gồm cập nhật pyproject.toml, cogmem_api/config.py (nếu cần), logs/task_502_summary.md, tests/artifacts/test_task502_packaging_config.py; verification gồm Drift giữ semantics config quan trọng từ HINDSIGHT (host/port/database/llm), Behavioral test parse env và boot không lỗi, Isolation check import chain chỉ nằm trong cogmem_api.
16. Sprint 5 - Atomic Task T5.3: migrate Docker assets theo 2 chế độ chạy chính của HINDSIGHT: standalone embedded pg0 và compose external PostgreSQL; output gồm docker/standalone/Dockerfile, docker/standalone/start-all.sh, docker/docker-compose/external-pg/docker-compose.yaml, .env.example cập nhật cho CogMem, logs/task_503_summary.md, tests/artifacts/test_task503_docker_assets.py; verification gồm Drift map trực tiếp từ F:/ai-ml/hindsight/docker/standalone và docker/docker-compose/external-pg, Behavioral test `docker build` + smoke `GET /health` thành công, Isolation check image chỉ chạy cogmem_api entrypoint.
17. Sprint 5 - Atomic Task T5.4: tạo smoke scripts và tài liệu vận hành Docker cho CogMem (tương tự test-image.sh + quick-start), đảm bảo tương thích yêu cầu pg0-in-docker; output gồm scripts/docker (hoặc docker/test-image.sh), README.md cập nhật mục Docker, logs/task_504_summary.md, tests/artifacts/test_task504_docker_smoke_contract.py; verification gồm Drift so với chiến lược smoke test của HINDSIGHT, Behavioral test retain/recall smoke tối thiểu qua container, Isolation check script không gọi binary/package hindsight.
18. Sprint 6 - Completeness Gate trước evaluation (sau khi Sprint 5 pass). Atomic Task T6.1: khôi phục đầy đủ retain extraction path theo HINDSIGHT (LLM-driven extraction + prompt modes concise/custom/verbatim/verbose) vào cogmem_api, đồng thời giữ đúng phạm vi Idea (không observation, không consolidation chủ động); output gồm cập nhật cogmem_api/engine/retain/fact_extraction.py, cogmem_api/engine/retain/orchestrator.py, cogmem_api/engine/llm_wrapper.py (nếu cần), logs/task_601_summary.md, tests/artifacts/test_task601_retain_prompt_parity.py; verification gồm Drift map chi tiết source prompt logic từ hindsight_api/engine/retain/fact_extraction.py sang CogMem với bảng phần giữ/phần lược bỏ theo Idea, Behavioral test đủ 4 mode prompt và assert parse schema/fact types đúng, Isolation check không còn import hindsight_api trong toàn bộ retain chain.
19. Sprint 6 - Atomic Task T6.2: hoàn thiện retain behavior parity cho metadata và edge intent của CogMem (raw_snippet, causal, transition, action_effect) trên luồng LLM thực tế; output gồm cập nhật cogmem_api/engine/retain/types.py, link_creation.py, fact_storage.py, logs/task_602_summary.md, tests/artifacts/test_task602_retain_behavior_parity.py; verification gồm Drift đối chiếu semantics từ HINDSIGHT rồi áp mapping sang 6-network CogMem, Behavioral test conversation nhiều phiên tạo đúng node/link và lifecycle intention, Isolation check chạy retain e2e mà không cần hindsight_api runtime.
20. Sprint 6 - Atomic Task T6.3: dựng harness evaluation/ablation E1-E7 với 2 pipeline tách bạch và có hook ablation cài cắm được: (A) pipeline full gồm recall + generation + judge để đo end-to-end accuracy, (B) pipeline recall-only để đo riêng độ chính xác recall; gate triển khai theo thứ tự test fixture hội thoại ngắn trước (không cần dữ liệu thực), sau đó mới mở rộng dữ liệu small và subset stratified; output gồm scripts/eval_cogmem.py, scripts/ablation_runner.py, logs/task_603_summary.md, tests/artifacts/test_task603_eval_harness.py, logs/eval/*.json; verification gồm Drift xác nhận metric/judge setup theo docs/CogMem-Idea.md và contract cấu hình LLM chỉ dùng namespace COGMEM (tham số endpoint/model/timeout tham chiếu từ ví dụ run_hindsight), Behavioral test chạy fixture hội thoại ngắn cho cả 2 pipeline + profile E1-E7 và sau đó chạy mini split từ data/longmemeval_s_distilled_small.json sinh thống kê per-category, Isolation check runner không gọi package hindsight_api trực tiếp.
21. Sprint 6 - Atomic Task T6.4: phân tích lỗi theo category và chốt backlog fix bắt buộc trước Full CogMem; output gồm logs/task_604_summary.md và logs/error_analysis_report.md; verification gồm Drift kiểm tra kết luận bám đúng artifact thực nghiệm, Behavioral kiểm tra report có wins/losses theo category + nguyên nhân gốc, Isolation check không phát sinh dependency ngoài phạm vi.
22. Sprint 7 - Reliability Hardening sau E1-E7. Atomic Task T7.1: xử lý các regression hạng P0/P1 từ T6.4 (ưu tiên multi-hop, temporal, causal, prospective) bằng sửa logic trong search/retain/reflect; output gồm các file code liên quan, logs/task_701_summary.md, tests/artifacts/test_task701_regression_fixes.py; verification gồm Drift xác nhận chỉ sửa logic nghiệp vụ được chỉ ra bởi error analysis, Behavioral test replay bộ case lỗi và phải pass, Isolation check import/runtime độc lập trong cogmem_api.
23. Sprint 7 - Atomic Task T7.2: đóng gói reproducibility cho kết quả E1-E7 (config freeze, seed, command contract, artifact index); output gồm logs/task_702_summary.md, docs/PGNV/cogmem_eval_repro.md, tests/artifacts/test_task702_repro_contract.py; verification gồm Drift giữ nguyên evaluator semantics, Behavioral test chạy lại 2 lần cho variance trong ngưỡng định nghĩa, Isolation check script chỉ dùng cogmem_api.
24. Sprint 8 - Hierarchical KG (Contribution 5) để hoàn thiện Full CogMem. Atomic Task T8.1: triển khai schema + retrieval support cho level abstract/basic/specific và rule mapping từ facts hiện hữu; output gồm cập nhật cogmem_api/models.py, migration mới ở cogmem_api/alembic/versions/, cập nhật cogmem_api/engine/search/*, logs/task_801_summary.md, tests/artifacts/test_task801_hierarchical_kg_schema.py; verification gồm Drift đối chiếu section 3.5 trong docs/CogMem-Idea.md và giữ tương thích hạ tầng hiện tại, Behavioral test ingest + retrieve across levels đúng anchor behavior, Isolation check không kéo dependency từ hindsight_api.
25. Sprint 8 - Atomic Task T8.2: chạy E8 ablation và so sánh E7 vs E8 theo từng category; output gồm logs/task_802_summary.md, logs/eval/e8_*.json, tests/artifacts/test_task802_e8_ablation.py; verification gồm Drift đảm bảo cùng judge setup và cùng subset protocol, Behavioral test báo cáo chênh lệch per-category và case studies, Isolation check pipeline đánh giá độc lập.
26. Sprint 9 - Release Gate cho dự án CogMem đầy đủ. Atomic Task T9.1: tổng hợp final QA matrix (Drift/Behavior/Isolation toàn sprint), chuẩn hóa vận hành và checklist phát hành; output gồm logs/task_901_summary.md, logs/final_release_report.md, tests/artifacts/test_task901_release_gate.py, README.md cập nhật đường chạy chuẩn; verification gồm Drift xác nhận mọi contribution trong Idea đã có mã + artifact + test, Behavioral test full smoke retain/recall/eval pass, Isolation check toàn repo cogmem_api không còn import hindsight_api.

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
- f:/ai-ml/agent-memory-cognitive/hindsight_api/main.py - CLI startup flow baseline cho runtime packaging
- f:/ai-ml/agent-memory-cognitive/hindsight_api/server.py - ASGI app bootstrap baseline
- f:/ai-ml/agent-memory-cognitive/hindsight_api/api/http.py - API route surface baseline
- f:/ai-ml/agent-memory-cognitive/scripts/docker - quick docker run command đang dùng hiện tại
- f:/ai-ml/hindsight/docker/standalone/Dockerfile - source-of-truth cho container standalone mode
- f:/ai-ml/hindsight/docker/standalone/start-all.sh - source-of-truth startup orchestration trong container
- f:/ai-ml/hindsight/docker/docker-compose/external-pg/docker-compose.yaml - source-of-truth external PostgreSQL mode
- f:/ai-ml/agent-memory-cognitive/scripts/test_hindsight.py - mẫu script eval hiện hữu
- f:/ai-ml/agent-memory-cognitive/pyproject.toml - dependency/tooling surface

**Verification**
1. Chuẩn Drift Check toàn dự án: mỗi task có bảng so sánh Source (hindsight_api) vs Fork (cogmem_api) trong logs/task_<id>_summary.md, chỉ rõ phần hạ tầng giữ nguyên và phần nghiệp vụ thay đổi.
2. Chuẩn Behavioral Testing toàn dự án: mỗi task có tests/artifacts/test_<task_name>.py chạy độc lập bằng uv run python <script> với assert input/output rõ ràng.
3. Chuẩn Isolation Check toàn dự án: sau mỗi task chạy tìm kiếm import chéo (import hindsight_api hoặc from hindsight_api) trong cogmem_api và fail nếu còn.
4. Regression checkpoints theo sprint: cuối mỗi sprint chạy lại toàn bộ tests/artifacts liên quan sprint đó và cập nhật log tổng hợp.
5. Evaluation checkpoints: E1 làm mốc; E2-E7 chạy cùng pipeline judge/metric để so sánh công bằng theo category.

**Decisions**
- Bao gồm trong phạm vi hiện tại: Contribution 1-5 + E1-E8 theo docs/CogMem-Idea.md, với stage-gate kiểm soát rủi ro giữa các sprint.
- Stage-gate mới: chỉ bắt đầu evaluation từ T6.3 sau khi T6.1-T6.2 pass (retain logic completeness + behavior parity) và Sprint 5 đã pass Docker smoke.
- E8 Hierarchical KG được triển khai trong Sprint 8 để hoàn thiện Full CogMem; chỉ được phép hoãn khi có blocker hạ tầng đã được ghi nhận bằng artifact và kế hoạch xử lý cụ thể.
- Chiến lược kiến trúc: fork-then-modify, tuyệt đối không import trực tiếp từ hindsight_api vào cogmem_api.
- Chuẩn artifact bắt buộc cho mỗi atomic task: logs/task_<id>_summary.md và tests/artifacts/test_<task_name>.py.

**Further Considerations**
1. Threshold cho Habit và cycle guards sẽ được cố định bằng config và hiệu chỉnh sau E1 dựa trên kết quả subset, không hardcode rải rác.
2. Raw snippet storage mặc định để trong DB column trước; nếu phát sinh vấn đề kích thước sẽ tách sang storage abstraction ở sprint sau.
3. Nếu cần rút ngắn thời gian, có thể chạy song song nhóm task T2.2/T2.3/T2.4 sau khi T2.1 ổn định vì chúng chia sẻ retain nền nhưng ít phụ thuộc trực tiếp vào nhau.
4. Trong Sprint 6, file `data/longmemeval_s_distilled_small.json` là dataset bắt buộc cho vòng test nhanh đầu tiên; chỉ mở rộng sang subset lớn hơn sau khi T6.1-T6.2 và harness ở T6.3 đã ổn định.

## Audit Addendum - Backfill Sprint 1->5 (Mandatory Before Full Evaluation)

Kết luận audit: Sprint 1->5 có nhiều phần được triển khai theo baseline/minimal để gate Docker và smoke contract. Trước khi claim "Full CogMem", bắt buộc hoàn tất các task backfill sau.

1. Backfill Task B1 - Config Contract Parity (retain/runtime/retrieval)
- Phạm vi: mở rộng `cogmem_api/config.py` để hỗ trợ đầy đủ các biến cấu hình cần cho retain prompt path và runtime tương đương luồng HINDSIGHT (LLM base URL, timeout tổng, timeout retain/reflect, extraction mode, retain max completion tokens, embeddings/reranker provider knobs cần thiết cho recall chất lượng).
- Output: cập nhật `cogmem_api/config.py`, cập nhật `.env.example`, `logs/task_611_summary.md`, `tests/artifacts/test_task611_config_contract.py`.
- Verification:
	- Drift Check: bảng map ENV HINDSIGHT -> ENV COGMEM cho các trường giữ lại theo Idea.
	- Behavioral Testing: parse env matrix và assert fallback/default đúng.
	- Isolation Check: không import `hindsight_api`.

2. Backfill Task B2 - Retain LLM Path + Prompt Parity
- Phạm vi: thay baseline seeded/fallback extraction bằng LLM-driven extraction path với 4 mode prompt (concise/custom/verbatim/verbose), giữ domain CogMem 6 networks và không đưa observation/consolidation chủ động trở lại.
- Output: cập nhật `cogmem_api/engine/retain/fact_extraction.py`, bổ sung module LLM cần thiết trong `cogmem_api/engine/*`, `logs/task_612_summary.md`, `tests/artifacts/test_task612_retain_prompt_parity.py`.
- Verification:
	- Drift Check: map prompt constants và extraction flow từ `hindsight_api/engine/retain/fact_extraction.py`.
	- Behavioral Testing: chạy retain với mock LLM cho đủ mode + schema parse + transition/action-effect metadata.
	- Isolation Check: grep import chain chỉ còn `cogmem_api`.

3. Backfill Task B3 - Runtime API Completeness (No Smoke-Only Buffer)
- Phạm vi: thay endpoint retain/recall kiểu in-memory smoke bằng API gọi trực tiếp memory engine thật (retain_batch/recall stack), giữ health/version endpoint và contract Docker.
- Output: cập nhật `cogmem_api/api/http.py`, `cogmem_api/engine/memory_engine.py`, `logs/task_613_summary.md`, `tests/artifacts/test_task613_runtime_api_e2e.py`.
- Verification:
	- Drift Check: đối chiếu route contract với `hindsight_api/api/http.py`, lược bỏ đúng các phần ngoài phạm vi Idea.
	- Behavioral Testing: retain -> DB -> recall roundtrip trên fixture DB.
	- Isolation Check: không có runtime path gọi package HINDSIGHT.

4. Backfill Task B4 - Retrieval Quality Parity (Reranker/Embeddings)
- Phạm vi: thay `RRFPassthroughCrossEncoder` bằng tùy chọn reranker thật theo config và đảm bảo pipeline recall dùng embedding/reranking providers hợp lệ để không suy giảm chất lượng retrieval.
- Output: cập nhật `cogmem_api/engine/cross_encoder.py`, các module search liên quan, `logs/task_614_summary.md`, `tests/artifacts/test_task614_retrieval_quality_contract.py`.
- Verification:
	- Drift Check: giữ orchestrator retrieval và RRF logic; chỉ thay adapter baseline.
	- Behavioral Testing: benchmark mini-case cho reranking reorder có ý nghĩa.
	- Isolation Check: không import `hindsight_api`.

5. Backfill Task B5 - Docker Run Contract Parity
- Phạm vi: cập nhật `scripts/docker` và runbook để phản ánh đầy đủ config tối thiểu cần cho retain LLM thực chiến (base_url/model/timeouts/retain knobs), tương thích cả embedded pg0 và external PostgreSQL.
- Output: cập nhật `scripts/docker`, `README.md`, `docker/test-image.sh`, `logs/task_615_summary.md`, `tests/artifacts/test_task615_docker_runtime_contract.py`.
- Verification:
	- Drift Check: map tham số với `scripts/run_hindsight.ps1` theo namespace CogMem.
	- Behavioral Testing: smoke retain/recall thật qua container với LLM endpoint cấu hình được.
	- Isolation Check: script không gọi image/package HINDSIGHT.

6. Gate Rule
- Chỉ được bắt đầu evaluation E1-E7/E8 khi B1-B5 đều pass và có artifact tương ứng.

## Canonical Execution Order (From Current State)

Thứ tự bắt buộc để hoàn thiện Full CogMem từ trạng thái hiện tại:

1. Hoàn tất Backfill B1 (Config Contract Parity).
2. Hoàn tất Backfill B2 (Retain LLM Path + Prompt Parity).
3. Hoàn tất Backfill B3 (Runtime API Completeness, bỏ smoke-only buffer).
4. Hoàn tất Backfill B4 (Retrieval Quality Parity: reranker/embeddings thật).
5. Hoàn tất Backfill B5 (Docker Run Contract Parity).
6. Gate kiểm tra: B1-B5 phải pass đầy đủ Drift/Behavior/Isolation + artifact.
7. Chạy Sprint 6 theo thứ tự T6.1 -> T6.2 -> T6.3 -> T6.4.
8. Chạy Sprint 7 theo thứ tự T7.1 -> T7.2.
9. Chạy Sprint 8 theo thứ tự T8.1 -> T8.2.
10. Chạy Sprint 9 với T9.1 (final release gate).

Chuỗi ngắn gọn để vận hành hàng ngày:
B1 -> B2 -> B3 -> B4 -> B5 -> Gate -> T6.1 -> T6.2 -> T6.3 -> T6.4 -> T7.1 -> T7.2 -> T8.1 -> T8.2 -> T9.1.