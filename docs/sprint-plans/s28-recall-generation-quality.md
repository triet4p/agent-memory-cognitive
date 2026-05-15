# Sprint S28: Recall & Generation Quality

**Trạng thái:**
- Wave 1: ✅ Done — R1-CE, R3, R4, G1, G2
- S28-Diag Parts 1-3: ✅ Done — audit (35 reports) + verify (VERDICTS.md) + diagnose (DIAGNOSIS.md)
- Wave 2: 🔄 PAUSED — re-plan after diagnostic analysis. Key findings: 24/35 PASS confirmed, 11 FAIL classified by root cause. Cross-session entity link over-bridging + BM25 gap are primary blockers.

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

**Trạng thái:**
- Part 1 (cogmem-audit): ✅ Done — 35 reports in `diagnostic_s28/`
- Part 2 (cogmem-verify): ✅ Done — VERDICTS.md (24 PASS, 11 FAIL, 0 Missing)
- Part 3 (cogmem-diagnose): ✅ Done — DIAGNOSIS.md (281 lines, 11 FAIL classified by root cause)

**Mục tiêu:** Chạy audit trên toàn bộ 35 cases (c000–c034) để có dữ liệu thực nghiệm đầy đủ trước Wave-2. Không chỉ FAIL — PASS cases cũng cần audit để hiểu điều gì đang hoạt động đúng và tránh regression.

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

**Output Part 1:** `experiments/v14/diagnostic_s28/` — per-case reports + SUMMARY.md với root cause frequency table

---

### S28-Diag Part 2 — cogmem-verify 🔄

**Công cụ:** `cogmem-verify` skill tại `.claude/skills/cogmem-verify/`

**Mục tiêu:** Xác định chính xác case nào là **truly PASS** (eval correct + recall correct), **truly FAIL** (eval wrong vì recall hoặc generation issue), hoặc **mislabeled** (eval PASS nhưng recall miss — có thể là eval lucky). Dùng checkpoint gold answers để verify recall quality per case.

**Input:** `experiments/v14/checkpoints_5/` (gold answers)

**Output:** `experiments/v14/diagnostic_s28/verification.md`:
- Table: case_id | eval_result | recall_evidence | truly_pass/truly_fail/mislabeled
- Phân biệt: recall miss vs generation error vs eval lucky

**Flow verify:**
1. Load eval result từ checkpoint
2. Kiểm tra recall evidence cho mỗi case (top-25 recall quality)
3. So sánh eval result vs recall evidence
4. Classify: truly_pass / truly_fail / mislabeled

---

### S28-Diag Part 3 — cogmem-diagnose 🔄

**Công cụ:** `cogmem-diagnose` skill tại `.claude/skills/cogmem-diagnose/`

**Mục tiêu:** Dựa trên Part 1 (audit reports) + Part 2 (verified PASS/FAIL classification), chạy diagnose trên các FAIL cases để phân loại failure types và xác định Wave-2 fix priority. Có thể chạy trên cả PASS cases nếu cần.

**Input:** `experiments/v14/diagnostic_s28/` (Part 1 audit reports + Part 2 verification.md) + `experiments/v14/checkpoints_5/` (gold answers)

**Output:** `experiments/v14/diagnostic_s28/DIAGNOSIS.md`:
- Failure type classification table (embedding gap, graph isolation, recall fail, generation error)
- PASS vs FAIL discriminating factors
- Wave-2 fix recommendations prioritized by impact

**Flow chẩn đoán:**
1. Load verified results từ Part 2 + audit reports từ Part 1
2. For each truly_fail case → classify root cause type
3. Aggregate frequency table
4. Compare truly_pass vs truly_fail cases → identify discriminating factors
5. Draft Wave-2 fix recommendations

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

## Wave 2 — MOVED TO S29

All Wave 2 tasks have been re-scoped and moved to a separate sprint **S29** based on S28-Diag findings. See [s29-recall-retain-routing-generation-quality.md](s29-recall-retain-routing-generation-quality.md).

Diagnostic confirmed:
- 24/35 PASS (confirmed working)
- 11/35 FAIL classified by root cause (8 mechanisms)
- Primary blockers: cross-session entity over-bridging (generic nouns treated as entities), BM25 gap for specific named products, temporal link weight uniformity, preference routing blind spot
- S29 scope: 11 targeted fixes (R-1, R-2, G-1..G-4, C-1, T-1, T-2, G-5, G-6) split into Wave 2A (no re-retain) and Wave 2B (v15 re-retain). Target: ≥32/35 PASS.

---

## Exit Gate Sprint S28

| Gate | Condition | Status |
|------|-----------|--------|
| W1-artifact | 7/7 artifact checks PASS | ✅ |
| W1-G1 | Session ordering in generation prompt | ✅ |
| W1-G2 | Generation prompt improvements (c023/c030/c032) | ✅ |
| W1-R1-CE | RRF rank boost in scoring | ✅ |
| W1-R3 | Causal pattern expansion | ✅ |
| W1-R4 | Singleton session penalty | ✅ |
| Diag-Part1 | cogmem-audit: 35 case reports generated | ✅ |
| Diag-Part2 | cogmem-verify: VERDICTS.md (24 PASS / 11 FAIL confirmed) | ✅ |
| Diag-Part3 | cogmem-diagnose: DIAGNOSIS.md (281 lines, root cause classified) | ✅ |
| W2-plan | Wave 2 re-scoped → moved to S29 | ✅ |
