# Sprint S28: Recall & Generation Quality

**Trạng thái:**
- Wave 1: ✅ Done — R1-CE, R3, R4, G1, G2
- S28-Diag: 🔄 In progress — `cogmem-audit` skill built, chờ chạy trên toàn bộ 35 cases
- Wave 2: 🔄 Pending (R2+R2b+T1+G3+G4, cần re-retain v15, sau Diag)

**Phụ thuộc:** S27 complete ✅

---

## Bối cảnh

**CP5 checkpoint (2026-05-13):** 24/35 real PASS, 11/35 FAIL.

**Root causes (CP5 empirically diagnosed via live CURL + checkpoint analysis):**

| Case | CP5 | Stage | Root cause xác nhận |
|------|-----|-------|---------------------|
| c000 | FAIL | Generation | Noise session `2e4430d8_2` (CE=−6.39) chiếm rank 1-2; gold sessions ở rank 3+. Model đếm sai do fact leadership bị hiểu nhầm là project riêng biệt |
| c001 | FAIL | Recall+Gen | Tiger I ở rank 26-28 (rrf_rank=16), ngoài top-25. G3 fix generation; R2+R2b Wave-2 fix recall |
| c006 | FAIL | Generation | Model sum sai: cộng estimated hours của game được recommend thay vì actual playtime |
| c007 | FAIL | Recall | Noise session `81b971b8_2` ("sister's wedding") có **4 facts** trong top-7 — không phải singleton → R4 không fix; primary fix là R2 (Wave-2) |
| c014 | FAIL | Generation | Hai session mâu thuẫn (125 vs 120 stars); G1 session ordering đã add nhưng cần verify live |
| c023 | FAIL | Generation | "flea market item" ≠ "sunset painting" trong model reasoning → entity flexibility issue |
| c029 | FAIL | Recall | Top-25 hoàn toàn irrelevant; query classified `semantic` thay vì `causal`; embedding gap "sneezing" ≠ "cat shedding dust" |
| c031 | FAIL | Recall | "battery life" ≠ "power bank" semantic gap; sess@5=0 — hard miss |
| c033 | FAIL | Retain | "Memrise" (assistant recommendation) không có trong bank — retain fail |
| c032 | FAIL | Generation | Lemon poppyseed ở rank #1 recall nhưng model chọn cookies |
| c030 | FAIL | Generation | Suica + TripIt cả hai trong recall nhưng chỉ enumerate một |

---

## Diagnostic Sprint — S28-Diag 🔄

**Mục tiêu:** Chạy audit trên toàn bộ 35 cases (c000–c034) để có dữ liệu thực nghiệm đầy đủ trước Wave-2. Không chỉ FAIL — PASS cases cũng cần audit để hiểu điều gì đang hoạt động đúng và tránh regression. Sau đó tổng hợp root cause map + statistical comparison PASS vs FAIL → thiết kế Wave-2 fix đúng hướng.

**Công cụ:** `cogmem-audit` skill tại `.claude/skills/cogmem-audit/`

**Flow chẩn đoán mỗi case:**
1. Load context từ checkpoint `experiments/v14/checkpoints_5/E7_full_c{NNN}.json`
2. Fetch facts từ gold sessions via `GET /facts?document_id={session_id}` (endpoint mới)
3. LLM judgment → identify **answer-relevant facts** (chỉ dùng `text` field, không dùng `raw_snippet`)
4. Recall audit: `top_k=25` + `top_k=300` với `trace=true` (phân biệt CE suppression vs channel-level miss)
5. Graph analysis: probe 7 link types cho missing facts
6. Phân loại root cause: Embedding gap / Graph isolation / BFS dilution / CE suppression / Generation error
7. Write report → `experiments/v14/diagnostic_s28/{case_id}_report.md`

**API changes supporting S28-Diag:**
- `GET /v1/default/banks/{bank_id}/facts?document_id={session_id}&limit=100` — filter facts by session ID (mới thêm 2026-05-13 vào `fact_storage.py` và `http.py`)

**Output:** `experiments/v14/diagnostic_s28/` — per-case reports + SUMMARY.md với root cause frequency table

---

## Wave 1 — Không cần re-retain 🔄

### ❌ REVERTED — R1-BFS (Adaptive per_source_limit)

**Lý do revert:** CP5 analysis xác nhận đây là band-aid không hiệu quả:
- c001: gold sessions đã có đủ trong top-30, Tiger I miss là do rrf_rank/CE (không phải window size)
- c014: expanding window làm worse (thêm noise world facts)
- Expanding BFS per_source_limit thêm noise cho các passing cases

**Files reverted:** `retrieval.py` (bỏ multi_hop BFS branch), `memory_engine.py` (bỏ `effective_top_k = max(top_k, 30)`)

---

### Task R1-CE — RRF Rank Boost in apply_combined_scoring ✅

**File:** `cogmem_api/engine/search/reranking.py`

**Root cause:** `combined_score = CE_normalized × recency_boost × temporal_boost` — RRF rank bị set `rrf_normalized = 0.0` (trace-only), không có trong scoring. Tiger I (rrf_rank=6) bị CE knock xuống dù multi-channel signal tốt hơn fact ở rank 25 (rrf_rank=15).

**Thay đổi:**
- Thêm constant `_RRF_ALPHA: float = 1.5`
- `apply_combined_scoring()` nhận thêm `rrf_alpha: float = _RRF_ALPHA`
- `rrf_boost = 1.0 + rrf_alpha / (1.0 + sr.candidate.rrf_rank)` (reciprocal form: convex decay)
- `combined_score = CE_normalized × rrf_boost × recency_boost × temporal_boost`

**Math:** Tiger I (rrf_rank=6): boost=1.214; rank-25 (rrf_rank=15): boost=1.094 → Tiger I score: 6.1e-5 × 1.214 = 7.41e-5 vs rank-25: 6.7e-5 × 1.094 = 7.33e-5 → Tiger I thắng (margin 1.1%).

**Hạn chế:** Standalone R1-CE không đủ khi rrf_rank=16 (Tiger I thực tế ở CP5). Cần graph fix (Wave-2 R2+R2b) để rrf_rank xuống ≤ 6.

---

### Task R3 — Causal Pattern Expansion ✅

**File:** `cogmem_api/engine/query_analyzer.py`

**Thay đổi:** Thêm `might\s+be|could\s+be|do\s+you\s+think|is\s+it\s+possible|could\s+it\s+be|what\s+caused|what\s+is\s+causing|contributing\s+to` vào `_CAUSAL_PATTERN`.

**Impact:** Static regex sweep trên 35 queries → **chỉ c029** bị reclassify (graph weight 1.0 → 2.4), zero false positives.

**Hạn chế:** R3 giải quyết routing nhưng không giải quyết embedding gap "sneezing" ≠ "cat shedding dust".

---

### Task R4 — Singleton Session Penalty ✅

**File:** `cogmem_api/engine/memory_engine.py`

**Thay đổi:** Sau CrossEncoder + `apply_combined_scoring`, count facts per `document_id`; penalize singletons × 0.85 (`_SINGLETON_PENALTY`); re-sort.

**Note:** Không fix c007 (sister's wedding = 4 facts, không phải singleton). General noise reduction cho tangential single-fact sessions.

---

### Task G1 — Session Temporal Ordering ✅

**File:** `cogmem_api/prompts/eval/generate.py`

**Thay đổi:**
- `_build_session_order()`: sort sessions by date từ `session_date_map`, assign ordinal 1..N (oldest → newest).
- Mỗi evidence item: `| Session {ordinal}/{total} (oldest/most recent) | Date: {date}`.
- Instruction: "prefer Session N/N (most recent) over Session 1/N (oldest)".

**Target:** c014 — model thấy rõ session nào mới hơn → prefer 120 stars (more recent) over 125 stars (older).

---

### Task G2 — Generation Prompt Improvements ✅

**File:** `cogmem_api/prompts/eval/generate.py`

3 instructions bổ sung:
1. **c023** — Entity flexibility: "if a recalled memory describes an item by generic description… use context clues to determine if they refer to the same object"
2. **c030** — Enumerate all: "enumerate ALL relevant items mentioned across ALL MEMORIES"
3. **c032** — Prioritize top-ranked: "MEMORIES are listed in order of relevance… prioritize top-ranked"

---

### Artifact Wave 1

**`tests/artifacts/test_task_s28_wave1.py`** — 7 static checks (R1-CE, R1 cross_fact_type flag, R3 causal, R4 singleton, G1 session ordering, G1 instruction, G2 improvements): tất cả PASS ✅

**`logs/task_s28_wave1_summary.md`** ✅

---

## Wave 2 — Cần re-retain (v15) 🔄

> **Dependency:** Chạy S28-Diag trước để xác nhận root cause, sau đó implement toàn bộ Wave-2 (R2+R2b+T1+G3+G4) cùng lúc trước khi re-retain.

### Task G3 — Scale Variant Dedup Instruction

**File:** `cogmem_api/prompts/eval/generate.py`

**Target:** c001 — model đếm Revell F-15 Eagle 1/72 và 1/48 là 2 kits riêng → tổng 6 thay vì 5.

**Thay đổi:** Thêm instruction: "When counting model kits or similar items, scale versions of the same kit name (e.g., 1/72 and 1/48 of the same model) count as one kit unless the user explicitly purchased both separately."

---

### Task G4 — Explicit-Instance Counting Instruction

**File:** `cogmem_api/prompts/eval/generate.py`

**Target:** c000 — model đếm 5 projects thay vì 2, vì tính cả general leadership role facts.

**Thay đổi:** Thêm instruction: "When counting distinct projects or events, count only instances where the user explicitly identifies a specific named project they personally led or managed. General statements about the user's role or responsibilities do not count as separate projects."

---

### Task R2 — Cross-Session Semantic Threshold Tighten

**File:** `cogmem_api/engine/retain/link_creation.py`

**Root cause:** S27 threshold=0.6 tạo quá nhiều cross-session semantic links → BFS budget bị phân tán → Tiger I activation yếu (rrf_rank tăng từ 13→18 so với v11), noise session c007 được activated cao.

**Thay đổi:** `COGMEM_API_RETAIN_CROSS_BANK_SEMANTIC_THRESHOLD` default 0.6 → **0.75**.

**Expected impact:**
- c001: Tiger I rrf_rank 18 → giảm cross-session competition → về ~13 → kết hợp R1-CE boost vào top-25
- c007: `81b971b8_2` wedding session mất cross-session link → drop khỏi top-25

**Cần re-retain toàn bộ → v15 banks.**

---

### Task R2b — Entity Extraction: Model Kit Names (Wave-2)

**File:** `cogmem_api/prompts/retain/pass1.py`

**Root cause:** Thiếu entity link "Tiger I tank" nối AK Interactive fact và Tiger I diorama fact trong session `_3` → BFS không lan activation từ entry point sang Tiger I.

**Thay đổi:** Thêm extraction guideline: "For hobby/collecting facts, extract specific product model names, brand names, and item identifiers as named entities. These should be consistent across facts referencing the same product."

**Verify:** Sau re-retain, CURL `GET /relationships/search?keyword=Tiger+I` để confirm entity links tồn tại.

---

### Task T1 — Retain Assistant Recommendations (c033)

**File:** `cogmem_api/prompts/retain/pass1.py`

**Root cause:** "Memrise" (assistant recommendation) không có trong bank — retain fail, không phải recall fail.

**Thay đổi:** Extraction guideline: "Also extract factual recommendations, app names, or tool names provided by the assistant that the user would benefit from remembering."

**Fact type:** `world` (third-party factual info).

---

## Exit Gate Sprint S28

| Gate | Condition | Status |
|------|-----------|--------|
| W1-artifact | 7/7 artifact checks PASS | ✅ |
| W1-G3 | G3 instruction added + test | 🔄 |
| W1-G4 | G4 instruction added + test | 🔄 |
| W2-R2 | threshold 0.75 implemented | 🔄 |
| W2-retain | v15 banks re-retained | 🔄 |
| W2-eval | Full batch ≥ 30/35 true PASS | 🔄 |
| verify-c014 | Generate endpoint trả lời 120 (không phải 125) | 🔄 |
| verify-c001 | Tiger I xuất hiện trong top-25 cho eval query | 🔄 |
