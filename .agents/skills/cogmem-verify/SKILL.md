---
name: cogmem-verify
description: >
  Verify whether a CogMem case truly passes or fails by comparing the pipeline's actual
  generated answer against the gold answer — without trusting judge.correct or judge.score.
  Use this skill whenever the user asks to verify, check, or confirm pass/fail status of
  one or more cases — e.g., "verify c000", "check which cases actually pass", "what does
  the model answer for c007", "run verification on all cases". Output feeds into
  cogmem-diagnose as the ground-truth verdict. Always run this BEFORE diagnosing failures.
---

# CogMem Verify Skill

Reads checkpoint files and makes an independent determination of whether each case passes
or fails — based solely on the semantic match between `generated_answer` and `gold_answer`.
Judge output is never used.

## ⚠ Execution Rules

**Never use `judge.correct`, `judge.score`, or `judge.reason`.**
These fields exist in the checkpoint but are unreliable. Ignore them completely.

**Use `generated_answer` from the checkpoint as the primary source.**
Do NOT call `scripts/generate_answer.py` unless `generated_answer` is absent, null, or
an empty string in the checkpoint. If the field has content — even a long think-block —
use it. The script exists only as a last resort for cases where the pipeline was not run.

**No shell scripting.** Never write PowerShell, bash, or curl to call the API.
If a live answer is needed, use only:
```
uv run python .claude/skills/cogmem-verify/scripts/generate_answer.py --bank-id ... --query "..."
```

**Batch vs single case:**
- **Single case** (e.g., "verify c007"): read one checkpoint, print verdict in chat.
- **Batch** (e.g., "verify all cases", "verify c000–c034"): process all specified cases
  sequentially — complete case N fully before opening the file for case N+1. Do NOT
  parallelize reads between cases. After all cases are verified, write the full
  `experiments/v14/diagnostic_s28/VERDICTS.md` in one pass.

**After all batch cases: write `experiments/v14/diagnostic_s28/VERDICTS.md`.**
Read `references/_VERDICT_TEMPLATE.md` for the exact format before writing.

---

## Data Source

For case `c{NNN}`:
```
experiments/v14/checkpoints_5/E7_full_c{NNN}.json
```

Relevant fields:

| Field | Location | Notes |
|-------|----------|-------|
| `bank_id` | top-level | e.g. `COGMEM_EXP_v14_e567_c001` |
| `query` | `questions[0].query` | The question asked |
| `gold_answer` | `questions[0].gold_answer` | Ground truth — int or string |
| `generated_answer` | `questions[0].generated_answer` | Full model output; may contain `<think>…</think>` |

---

## Extraction Steps

### Step 1: Extract the final answer from `generated_answer`

The field often contains `<think>…</think>` reasoning. The model's actual answer is
the text **after** `</think>`. If no think block is present, the entire field is the answer.

**Only the text after `</think>` counts for verdict.** Never use the think block to
determine PASS/FAIL — it contains the model's internal deliberation, not its stated answer.

However, if the think block reveals something diagnostically significant — e.g., the model
explicitly reasoned about the wrong entity, double-counted an item, or confused two sessions
— add a `Note:` line in the verdict so downstream diagnosis steps can use it:

```
Note (from think block): Model explicitly listed F-15 1/72 and F-15 1/48 as separate items
during reasoning, then carried that count into the final answer.
```

Only add a Note when the thinking reveals something non-obvious. Skip it when the thinking
is routine or mirrors what the final answer already makes clear.

### Step 2: Normalize `gold_answer`

- Integer (e.g., `2`) → expected count
- String (e.g., `"5 kits"`, `"Luna"`, `"120 stars"`) → extract core value

### Step 3: Compare semantically

**Count questions** (`gold_answer` is a number or "N items"):
- Extract the number from the model's conclusion.
- PASS only if the number matches exactly.
- "at least 5" when gold=5 → PASS. "at least 5" when gold=2 → FAIL.

**Named entity questions** (gold is a name, place, item):
- PASS if the model names the correct entity in its conclusion.
- Phrasing differences are fine ("five model kits" = "5 kits").
- FAIL if the model names a different entity, says "I don't know", or gives no answer.

**Factual value questions** (gold is a value, e.g., "120 stars"):
- PASS if the model's stated value matches exactly or is semantically equivalent.
- FAIL if the model gives a different number, or confuses a threshold with an actual value.

**"I don't know" / "no information available":**
- FAIL if `gold_answer` is a concrete value, name, or count — the model should have answered.
- PASS if `gold_answer` itself indicates no information exists (e.g., `"unknown"`, `"none"`,
  `"no record"`) — the model correctly recognized the absence of data.

---

## Output

Read `references/_VERDICT_TEMPLATE.md` for the exact format before writing.

- **Single case**: print verdict block in chat.
- **Batch**: write all verdicts to `experiments/v14/diagnostic_s28/VERDICTS.md`.
