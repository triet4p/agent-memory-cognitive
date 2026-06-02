# CogMem Verify Output Templates

Read this file before writing any output.

---

## Single Case

```
c{NNN}: {PASS|FAIL}
  Gold:  {gold_answer}
  Model: "{extracted final answer — one sentence, after </think> if present}"
  Reason: {one sentence — what specifically matched or mismatched}
```

**Example (c000):**
```
c000: FAIL
  Gold:  2
  Model: "you have led or are currently leading at least five distinct projects"
  Reason: Model counted 5 (marketing research, high-priority project, data mining, product
           launch, The Merge events) instead of 2 — noise session 2e4430d8_2 injected
           irrelevant project mentions that the model counted as distinct led projects.
```

**Example (c001):**
```
c001: FAIL
  Gold:  5 kits
  Model: "you have worked on or purchased approximately 6 model kits"
  Reason: Model counted 6 instead of 5 — likely counted F-15 Eagle 1/72 and 1/48 as two
           separate kits.
```

---

## Batch — write to `experiments/v14/diagnostic_s28/VERDICTS.md`

```markdown
# CogMem Verdicts

Generated: {date}
Cases: {N} total — {pass_count} PASS, {fail_count} FAIL, {missing_count} Missing answer

## Verdict Table

| Case | Gold Answer | Verdict | Model Answer (summary) | Mismatch Reason |
|------|-------------|---------|------------------------|-----------------|
| c000 | 2 | FAIL | "at least five distinct projects" | Counted 5; noise session added 3 extra project mentions |
| c001 | 5 kits | FAIL | "approximately 6 model kits" | Counted F-15 Eagle 1/72 and 1/48 as two separate kits |
| c007 | 3 | FAIL | "4 weddings attended" | Sister's wedding noise session counted as a real event |
| c014 | 120 stars | FAIL | "125 stars to reach Gold" | Gave threshold value, not the updated current value |
| c029 | Luna (cat) | FAIL | "no information available" | Recall missed the Luna fact entirely |
| c031 | power bank | FAIL | "I don't have specific information" | Complete recall miss on "battery life" / "power bank" |
| ... | ... | ... | ... | ... |

## Summary

| Verdict | Count | Cases |
|---------|-------|-------|
| PASS    | N     | c???, ... |
| FAIL    | N     | c???, ... |
| Missing | N     | c???, ... |

## FAIL Categories (for cogmem-diagnose input)

Group FAIL cases by the apparent error type visible from the model answer alone:

### Wrong count (model answered a different number)
Cases: {list} — gold vs model number per case

### Wrong entity / name
Cases: {list} — what model said vs gold entity

### "No information" / refused to answer
Cases: {list} — these are almost always recall failures

### Correct topic, wrong value (updated vs old value)
Cases: {list} — model gave a superseded value

### Other mismatch
Cases: {list} — description per case
```
