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
- S28-Diag (systematic diagnostic toàn bộ 35 cases trước Wave-2): 🔄 In progress — `cogmem-audit` skill built
- S28 Wave 2 (R2+R2b+T1+G3+G4, v15 banks): Pending 🔄
- S-final (E1-E7 ablation dry run): Pending 🔄

**Next immediate action:** Run `cogmem-audit` trên toàn bộ 35 cases (c000–c034) → root cause map + statistical comparison PASS vs FAIL → sau đó Wave-2 (R2+R2b+T1+G3+G4 cùng lúc, cần re-retain v15).

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
| S28-Diag | Systematic diagnostic: cogmem-audit skill, 35 cases → root cause map + PASS vs FAIL comparison trước Wave-2 | — | 🔄 In progress | [s28-recall-generation-quality.md](sprint-plans/s28-recall-generation-quality.md) |
| S28 Wave 2 | R2+R2b+T1 (recall/retain fixes) + G3+G4 (generation fixes) + v15 re-retain | — | 🔄 Pending | [s28-recall-generation-quality.md](sprint-plans/s28-recall-generation-quality.md) |
| S-final | Full ablation dry run gate (E1-E7) | 761-763 | 🔄 Pending | [s-final-ablation.md](sprint-plans/s-final-ablation.md) |

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
```

### 🔄 Remaining (in order)
```
S28-Diag: Run cogmem-audit on 11 FAIL cases → root cause map
→ S28 Wave 2: R2+R2b+T1 (recall/retain) + G3+G4 (generation) + v15 re-retain
→ S-final (tasks 761-763): Full Ablation Dry Run Gate
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
