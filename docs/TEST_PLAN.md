# S24 Ablation Test Plan — LongMemEval-S Distilled Small

**Date:** 2026-04-25  
**Fixture:** `data/longmemeval_s_distilled_small.json`  
**Goal:** Run E1–E7 ablation profiles on 12 LongMemEval-S questions, measure judge accuracy, recall@k, and session recall@k per category.

---

## 1. Fixture Summary

| | Value |
|---|---|
| File | `data/longmemeval_s_distilled_small.json` |
| Questions | 12 (each = 1 QA item with its own haystack) |
| Category split | multi-session × 5, knowledge-update × 4, temporal-reasoning × 3 |
| Sessions per question | 39–53 (avg ~47) |
| Chars per question | ~470k–500k |
| Chunks per question (chunk_size=3000) | ~158–167 |
| Gold sessions per question | 1–4 |

Each item is evaluated independently: its haystack is retained into a fresh bank, then recalled.

---

## 2. Ablation Profiles

| Profile | Description | enabled_networks | adaptive_router | sum_activation |
|---|---|---|---|---|
| E1 | Baseline (3 networks) | world, experience, opinion | ✗ | ✗ |
| E2 | + Habit | world, experience, opinion, habit | ✗ | ✗ |
| E3 | + Intention | world, experience, opinion, intention | ✗ | ✗ |
| E4 | + Action-Effect | world, experience, opinion, action_effect | ✗ | ✗ |
| E5 | All 6 networks, no routing/SUM | all 6 | ✗ | ✗ |
| E6 | All 6 networks + SUM activation | all 6 | ✗ | ✓ |
| E7 | Full CogMem (all 6 + routing + SUM) | all 6 | ✓ | ✓ |

---

## 3. Retain Grouping (Critical)

E5, E6, E7 all retain the **same 6 networks** — they can share a bank. Only the recall parameters differ (adaptive_router, sum_activation). This saves 2 × 12 = 24 retain batches.

| Retain Group | Profiles | Bank naming scheme |
|---|---|---|
| Group-1 | E1 only | `COGMEM_S24_e1_c{N:03d}` |
| Group-2 | E2 only | `COGMEM_S24_e2_c{N:03d}` |
| Group-3 | E3 only | `COGMEM_S24_e3_c{N:03d}` |
| Group-4 | E4 only | `COGMEM_S24_e4_c{N:03d}` |
| Group-567 | E5 + E6 + E7 | `COGMEM_S24_e567_c{N:03d}` |

**Total retain batches: 5 × 12 = 60**  
**Total recall+judge calls: 7 × 12 = 84**

---

## 4. Time Estimate

| Step | Per question | Total (×12) |
|---|---|---|
| Retain (1 group, ~160 chunks @ ~5s/chunk) | ~13 min | — |
| Retain × 5 groups per question | ~65 min | ~13 hours |
| Recall (7 profiles, negligible) | ~1 min | ~12 min |
| Judge LLM (7 calls × ~90s, minimax-m2.7) | ~10 min | ~2 hours |
| **Total per question** | **~76 min** | |
| **Total all 12 questions** | | **~15 hours** |

Depends heavily on NGROK latency and Ministral-3B throughput. Use `--conv-index` to process one question at a time with checkpointing.

---

## 5. Pre-flight Checklist

Before any run:

- [ ] Docker Desktop running
- [ ] Start services: `docker compose --env-file .env -f docker/docker-compose/external-pg/docker-compose.yaml up -d`
- [ ] Verify API health: `curl http://localhost:8888/health`
- [ ] Load env vars into PowerShell session (see Section 6)
- [ ] Verify NGROK URL is active: check `COGMEM_API_LLM_BASE_URL` in `.env`
- [ ] Verify minimax API key valid: `echo $env:COGMEM_API_EVAL_LLM_API_KEY`
- [ ] Docker image rebuilt after `entity_processing.py` FK fix: `docker compose ... up --build -d`

---

## 6. Environment Setup (PowerShell)

Run once per terminal session:

```powershell
# Load all .env vars into current process
Get-Content .env | ForEach-Object {
    if ($_ -match '^([^#=\s][^=]*)=(.*)$') {
        $k = $Matches[1].Trim()
        $v = $Matches[2].Trim().Trim('"')
        [System.Environment]::SetEnvironmentVariable($k, $v, 'Process')
    }
}

# Verify key vars
echo "LLM: $env:COGMEM_API_LLM_BASE_URL"
echo "Eval LLM: $env:COGMEM_API_EVAL_LLM_BASE_URL"
echo "Judge model: $env:COGMEM_API_EVAL_LLM_MODEL"
```

---

## 7. Execution Order per Conversation (conv-index N)

Process questions in order N=0..11. For each N:

### Step 1: Rebuild Docker (once, before first run)

```powershell
docker compose --env-file .env -f docker/docker-compose/external-pg/docker-compose.yaml up --build -d
```

### Step 2: E5 — Retain + Recall (Group-567 bank)

```powershell
$N = 0  # change per iteration
$bankE567 = "COGMEM_S24_e567_c$($N.ToString('000'))"

uv run python scripts/eval_cogmem.py `
  --pipeline full `
  --profile E5 `
  --fixture longmemeval `
  --conv-index $N `
  --bank-id $bankE567 `
  --checkpoint-dir logs/eval/s24/checkpoints `
  --output-dir logs/eval/s24
```

### Step 3: E6 — Skip-Retain, Reuse Group-567 Bank

```powershell
uv run python scripts/eval_cogmem.py `
  --pipeline full `
  --profile E6 `
  --fixture longmemeval `
  --conv-index $N `
  --bank-id $bankE567 `
  --skip-retain `
  --checkpoint-dir logs/eval/s24/checkpoints `
  --output-dir logs/eval/s24
```

### Step 4: E7 — Skip-Retain, Reuse Group-567 Bank

```powershell
uv run python scripts/eval_cogmem.py `
  --pipeline full `
  --profile E7 `
  --fixture longmemeval `
  --conv-index $N `
  --bank-id $bankE567 `
  --skip-retain `
  --checkpoint-dir logs/eval/s24/checkpoints `
  --output-dir logs/eval/s24
```

### Step 5: E1 — Own Bank

```powershell
uv run python scripts/eval_cogmem.py `
  --pipeline full `
  --profile E1 `
  --fixture longmemeval `
  --conv-index $N `
  --bank-id "COGMEM_S24_e1_c$($N.ToString('000'))" `
  --checkpoint-dir logs/eval/s24/checkpoints `
  --output-dir logs/eval/s24
```

### Step 6–8: E2, E3, E4 — Own Banks

Same pattern, replace `--profile E2/E3/E4` and `--bank-id COGMEM_S24_e2/e3/e4_c{N:03d}`.

### Step 9: After all 12 conversations — Aggregate (auto)

When `--conv-index` is omitted after all 12 checkpoints exist, the script auto-aggregates. Or trigger manually:

```powershell
# Run without --conv-index to trigger aggregation
uv run python scripts/eval_cogmem.py --pipeline full --profile E7 --fixture longmemeval --checkpoint-dir logs/eval/s24/checkpoints --output-dir logs/eval/s24
```

---

## 8. Checkpoint & Resume

Each conversation saves to `logs/eval/s24/checkpoints/{PROFILE}_full_c{N:03d}.json`.

If a run fails mid-way, re-run the same command — the checkpoint guard skips completed convs automatically:

```
[full] conv=3/11 SKIPPED (checkpoint exists)
```

To restart a specific conv (e.g. re-do E7 conv 5):

```powershell
Remove-Item logs/eval/s24/checkpoints/E7_full_c005.json
# then re-run E7 conv-index 5
```

---

## 9. Metrics to Collect per Profile

From the aggregated result JSON:

| Metric | Description |
|---|---|
| `judge_accuracy` | % questions answered correctly (per judge LLM) |
| `judge_score_mean` | Mean judge score 0–1 |
| `recall_keyword_accuracy` | Keyword coverage in recalled facts |
| `recall_at_5_mean` | Keyword recall@5 |
| `session_recall_at_5_mean` | Session-level recall@5 (gold doc_id in top-5) |
| `session_recall_at_10_mean` | Session-level recall@10 |
| `judge_accuracy_per_category` | Breakdown by multi-session / knowledge-update / temporal |

---

## 10. What to Compare Across Profiles

| Hypothesis | Expected |
|---|---|
| E5 vs E1 (+ 3 networks) | Higher judge_accuracy when extra networks add relevant facts |
| E6 vs E5 (+ SUM activation) | Higher session_recall@k (SUM helps propagate activation across sessions) |
| E7 vs E6 (+ adaptive router) | Higher judge_accuracy on temporal/multi-hop queries |
| E2 vs E1 | Habit network contribution isolated |
| E3 vs E1 | Intention network contribution isolated |
| E4 vs E1 | Action-effect network contribution isolated |

---

## 11. Known Risks & Mitigations

| Risk | Mitigation |
|---|---|
| NGROK URL expires | Update `COGMEM_API_LLM_BASE_URL` in `.env` and reload env vars |
| Ministral-3B returns empty facts (heuristic fallback) | Logged as WARNING — check Docker logs between convs |
| minimax-m2.7 API rate limit | Add `--api-timeout 3600` if needed; judge calls are sequential |
| FK violation in retain (entity upsert) | Fixed in `entity_processing.py`; requires Docker image rebuild |
| Bank collision (same name) | Use unique naming scheme `COGMEM_S24_{profile}_c{N:03d}` per convention above |
| Checkpoint already exists for wrong run | Delete specific checkpoint and re-run |
