## PLAN - CogMem Migration (Index)

## 1) Mục tiêu

Bản PLAN này là **index** + **trạng thái thực tế** của toàn dự án. Chi tiết từng sprint được lưu trong `docs/sprint-plans/`.

Mục tiêu điều phối:
1. Không mất dấu lịch sử triển khai trước đây.
2. Không phân mảnh phase/sprint như bản cũ.
3. Có entry gate/exit gate rõ cho từng sprint còn lại.

---

## 2) Trạng thái hiện tại

**Coverage matrix** ([docs/migration_idea_coverage_matrix.md](migration_idea_coverage_matrix.md)):
- C1: FULL ✅
- C2: FULL ✅
- C3: FULL ✅
- C4: FULL ✅
- C5: MISSING (deferred)

**Quyết định phạm vi đang khóa:**
- Delete scope đã hoàn tất ✅
- C1-C4 coverage FULL ✅
- Tutorial (S16-S19) hoàn tất ✅
- C5 để track sau, không chặn eval trong vòng này.

**Trạng thái eval:**
- S20-S24.8 (tasks 743-777): Tất cả hoàn tất ✅
- S25 (2-pass extraction + prompt centralization): Pending 🔄
- S26 (recall quality + channel trace + generation prompt): Pending 🔄
- S27 (relationship completeness): Pending 🔄
- S28 Wave 1 (recall + generation fixes, no re-retain): ✅ Done — R1-CE, R3, R4, G1, G2
- S28-Diag (audit + diagnose): Systematic diagnostic trước Wave-2 | — | ✅ Done | [s28-recall-generation-quality.md](sprint-plans/s28-recall-generation-quality.md)
- S29 (Wave 2A: R-1/R-2/G-1..G-4/C-1 routing+generation fixes, no re-retain): Pending 🔄
- S29 (Wave 2B: T-1/T-2/G-5/G-6 retain+graph fixes, v15 re-retain): Pending 🔄
- S-final (E1-E7 ablation dry run): Pending 🔄
- S31 (graph-only ablation E7G–E11G): ✅ Done — verdicts verified (benchmark-fit problem identified: LongMemEval lacks prospective/causal/habitual categories)
- S32 (benchmark-construction foundation + 6-case pilot): ✅ Done — `cogmem_bench/` package + 3 skills → 1 (author only) + multi-call generation + frozen pilot verified
- S33 (intention necessity — retain-level cách B + Minimax strict extractor): ✅ Done — 2/16 cases discriminate after full confound chain removed (router bias → flat; recall-time leakage → retain-level paired banks; extractor leakage → Minimax + strict-typing). Intention necessary in sparse-context edge cases (~12.5%); redundant in rich-context conversations (observational state facts leak hợp lệ qua experience).
- S34 (action_effect necessity — agentic AI workload): ✅ Done — 5/12 cases discriminate (http_429, docker_pull, playwright_wait, git_lockfile, azure_token) after full confound chain (paired banks + agentic_transcript Pass1 hint + strict typing + leak detector). McNemar p≈0.22 (not significant, n=12). Action_effect necessary in cases where causal rule resists `world` re-typing; redundant where Minimax compresses rule to "X is resolved by Y" objective-knowledge form. Conditional on conversational density (parallel với S33 intention finding).

**Next immediate action:** Phase F cognitive-node ablation complete (S31→S34). Possible follow-ups: (a) strengthen S34 strict-typing addendum to block `"X is resolved by Y"` `world` pattern and re-gate 5 leaked ablated banks (estimated 7-8/12 → significance); (b) habit network ablation (S35, if pursued); (c) write up cross-sprint narrative tying S33+S34 findings (typed networks conditionally necessary, workload+extractor-dependent).

---

## 3) Sprint Index

### ✅ Completed — Historical (Sprint 0-7 + Backfill)

| Sprint | Mô tả | Tasks | File chi tiết |
|--------|-------|-------|---------------|
| S0-S7 + B1-B5 | Schema, retain, retrieval, reflect, runtime, Docker, hindsight readiness | 001-703 | [s0-s7-history.md](sprint-plans/s0-s7-history.md) |

### ✅ Phase A — Delete hindsight_api

| Sprint | Mô tả | Tasks | File chi tiết |
|--------|-------|-------|---------------|
| S11 | Delete `hindsight_api/` only | 704 | [s11-delete.md](sprint-plans/s11-delete.md) |

### ✅ Phase B — Coverage Closure C1-C4

| Sprint | Mô tả | Tasks | File chi tiết |
|--------|-------|-------|---------------|
| S12-S15 | Close C1, C3, C4 to FULL + pre-tutorial gate | 705-708 | [s12-s15-coverage.md](sprint-plans/s12-s15-coverage.md) |

### ✅ Phase C — Tutorial

| Sprint | Mô tả | Tasks | File chi tiết |
|--------|-------|-------|---------------|
| S16-S18 + S19 + Audits | Tutorial top-down (architecture, module, function) + per-file + audits | 716-742 | [s16-s18-tutorial.md](sprint-plans/s16-s18-tutorial.md) |

### ✅ Phase E — Eval Readiness (Early: S20-S24.8)

| Sprint | Mô tả | Tasks | File chi tiết |
|--------|-------|-------|---------------|
| S20-S23 | Contribution gaps, benchmark adapters, eval metrics, session recall@k | 743-753 | [s20-s23-eval-readiness.md](sprint-plans/s20-s23-eval-readiness.md) |
| S24-hotfix | Pipeline bug fixes (FK, bool, URL, timeout, chunking, dateparser) | 756-757 | [s24-hotfixes.md](sprint-plans/s24-hotfixes.md) |
| S24 | Retrieval quality hardening (schema/index/ef_search/tags) | 758-760 | [s24-retrieval-quality.md](sprint-plans/s24-retrieval-quality.md) |
| S24.5 | Eval pipeline correctness (two-tier recall, gen/judge endpoints) | 764-767 | [s24.5-eval-pipeline.md](sprint-plans/s24.5-eval-pipeline.md) |
| S24.6 | Eval quality fixes (snippet dedup, cross-encoder, dual model) | 768-771 | [s24.6-eval-quality.md](sprint-plans/s24.6-eval-quality.md) |
| S24.7 | Retain quality fixes (chunk snippet + richer extraction) | 772-774 | [s24.7-retain-quality.md](sprint-plans/s24.7-retain-quality.md) |
| S24.8 | chunk_id pipeline fix + judge rubric + entity diagnostics | 775-777 | [s24.8-chunk-id-fixes.md](sprint-plans/s24.8-chunk-id-fixes.md) |

### 🔄 Phase E — Eval Readiness (Active/Pending: S25+)

| Sprint | Mô tả | Tasks | Trạng thái | File chi tiết |
|--------|-------|-------|------------|---------------|
| S25 | 2-pass speaker-aware extraction + prompt centralization | 778-785 | ✅ Done | [s25-two-pass-extraction.md](sprint-plans/s25-two-pass-extraction.md) |
| S26 | Recall quality: query routing fix, 4-channel trace, generation prompt | 786-788 | ✅ Done | [s26-recall-quality.md](sprint-plans/s26-recall-quality.md) |
| S27 | Relationship completeness: entity blocklist + cross-session links + Pass 3 | 789-793 | ✅ Done | [s27-relationship-completeness.md](sprint-plans/s27-relationship-completeness.md) |
| S28 Wave 1 | R1-CE (RRF boost), R3 (causal routing), R4 (singleton penalty), G1 (session order), G2 (prompt) | — | ✅ Done | [s28-recall-generation-quality.md](sprint-plans/s28-recall-generation-quality.md) |
| S28-Diag Part 1 | cogmem-audit: audit 35 cases → per-case reports | — | ✅ Done | [s28-recall-generation-quality.md](sprint-plans/s28-recall-generation-quality.md) |
| S28-Diag Part 2 | cogmem-verify: verify which cases are truly PASS/FAIL vs expected | — | ✅ Done | [s28-recall-generation-quality.md](sprint-plans/s28-recall-generation-quality.md) |
| S28-Diag Part 3 | cogmem-diagnose: classify failure types + PASS/FAIL comparison → Wave-2 priority | — | ✅ Done | [s28-recall-generation-quality.md](sprint-plans/s28-recall-generation-quality.md) |
| S29 Wave 2A | R-1/R-2 (routing), G-1..G-4 (generation), C-1 (CE floor) — no re-retain, v14 banks | — | ✅ Done | [s29-recall-retain-routing-generation-quality.md](sprint-plans/s29-recall-retain-routing-generation-quality.md) |
| S29 Wave 2B | T-1 (retain prompt), T-2 (entity blocklist), G-5 (semantic cap), G-6 (temporal weights) — code done, awaiting v15 re-retain | — | ✅ Code Done / 🔄 Re-retain Pending | [s29-recall-retain-routing-generation-quality.md](sprint-plans/s29-recall-retain-routing-generation-quality.md) |
| S-final | Full ablation dry run gate (E1-E7) | 761-763 | 🔄 Pending | [s-final-ablation.md](sprint-plans/s-final-ablation.md) |

### 🔬 Phase F — Cognitive-Node Ablation Study

| Sprint | Mô tả | Tasks | Trạng thái | File chi tiết |
|--------|-------|-------|------------|---------------|
| S31 | Graph-only ablation E7G–E11G (isolate node-type graph contribution) | — | ✅ Done | [s31-graph-only-ablation.md](sprint-plans/s31-graph-only-ablation.md) |
| S32 | Benchmark-construction foundation + 6-case pilot (cogmem_bench package, multi-call generation, 1 agent skill + manual scripts) | S32-T1..T5 | ✅ Done | [s32-bench-construction.md](sprint-plans/s32-bench-construction.md) |
| S33 | Intention necessity — retain-level ablation (cách B) + Minimax strict extractor + flat router + manual verdict | S33-T1..T4 | ✅ Done (2/16 discriminate; intention necessary in sparse-context, redundant in rich-context) | [s33-bench-discrimination.md](sprint-plans/s33-bench-discrimination.md) |
| S34 | Action_effect necessity — agentic AI workload (tool-use traces) + cách B + McNemar | S34-T1..T5 | ✅ Done (5/12 discriminate; conditional on extractor + density) | [s34-bench-action-effect-agentic.md](sprint-plans/s34-bench-action-effect-agentic.md) |

---

## 4) Canonical Execution Order

### ✅ Completed
```
Sprint 0 → S7 + Backfill B1-B5 (tasks 001-703)
→ S11 (task 704)
→ S12-S15 (tasks 705-708)
→ S16-S19 + Audits (tasks 716-742)
→ S20-S23 (tasks 743-753)
→ S24-hotfix (tasks 756-757)
→ S24 (tasks 758-760)
→ S24.5 (tasks 764-767)
→ S24.6 (tasks 768-771)
→ S24.7 (tasks 772-774)
→ S24.8 (tasks 775-777)
→ S25 (tasks 778-785)
→ S26 (tasks 786-788)
→ S27 (tasks 789-793)
→ S28 Wave 1 ✅
→ S28-Diag Parts 1-3 ✅ (audit + verify + diagnose — 24/35 PASS confirmed, 11 FAIL classified)
→ S28 Wave 2: MOVED TO S29 (re-scoped into 11 targeted fixes, Wave 2A + Wave 2B)
```

### 🔄 Remaining (in order)
```
→ S29 Wave 2A: R-1/R-2 (routing) + G-1..G-4 (generation) + C-1 (CE floor) on v14 banks ✅
→ S29 Wave 2B: T-1/T-2 (retain+entity) + G-5/G-6 (link creation) → v15 re-retain 🔄 Pending
→ S-final (tasks 761-763): Full Ablation Dry Run Gate
```

### 🔬 Phase F — Cognitive-Node Ablation Study (parallel track)
```
→ S31: Graph-only ablation E7G–E11G ✅ (benchmark-fit problem found)
→ S32: cogmem_bench foundation + pilot ✅
→ S33: intention necessity (cách B retain-level + Minimax strict extractor + flat router) ✅ — 2/16 discriminate (intention necessary in sparse-context)
→ S34: action_effect necessity in agentic workload (tool-use traces) ✅ — 5/12 discriminate (conditional on density + extractor)
```

### Hard dependency rules
1. S25 entry gate: S24.8 PASS ✅ → S25 PASS ✅
2. S26 dependency: S25 PASS ✅ → S26 PASS ✅
3. S27 dependency: S26 PASS ✅ → S27 PASS ✅
4. S28 Wave 2: S27 PASS ✅ + v15 banks ready
5. S-final dependency: S28 Wave 2 PASS
6. C5 deferred: không chặn eval trong vòng này

---

## 5) Verification Standard (mọi sprint)

1. **Drift Check**: đối chiếu [docs/CogMem-Idea.md](CogMem-Idea.md) và coverage matrix.
2. **Behavioral Testing**: mỗi sprint có artifact test chạy độc lập.
3. **Isolation Check**: không có import runtime trái phạm vi trong cogmem_api.
4. **Sprint Gate**: sprint sau chỉ bắt đầu khi sprint trước PASS exit gate.

---

## 6) Relevant Files

1. [docs/migration_idea_coverage_matrix.md](migration_idea_coverage_matrix.md)
2. [reports/hindsight_removal_readiness.md](../reports/hindsight_removal_readiness.md)
3. [docs/hindsight_removal_playbook.md](hindsight_removal_playbook.md)
4. [docs/CogMem-Idea.md](CogMem-Idea.md)
5. [docs/REPORT.md](REPORT.md)
6. pyproject.toml
7. [cogmem_api/engine/search/retrieval.py](../cogmem_api/engine/search/retrieval.py)
8. [cogmem_api/engine/memory_engine.py](../cogmem_api/engine/memory_engine.py)
