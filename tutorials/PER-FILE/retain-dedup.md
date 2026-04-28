# `dedup.py` — Cross-Pass Deduplication

## Purpose

`dedup.py::dedup_facts()` resolves fact sets from Pass 1 and Pass 2 after two-pass extraction. When both passes return facts about the same event, this function decides which version to keep.

## The Dedup Problem

**Pass 1** (all roles): "User joined DI in April 2024" (experience)
**Pass 2** (user-only): "User joined DI as ML Engineer in April 2024" (experience)

Both describe the same event with different specificity. Pass 2's version is usually more detailed (persona-focused prompt), but Pass 1 might capture facts Pass 2 missed.

## Algorithm

```python
def dedup_facts(facts_p1, facts_p2):
    # 1. Index Pass 2 by (content_index, chunk_index, fact_text)
    # 2. Iterate Pass 1:
    #    - If match found in Pass 2:
    #        - personal type (opinion/habit/intention/experience) → keep Pass 2
    #        - world/action_effect → keep Pass 1 (more comprehensive)
    #    - No match → keep Pass 1
    # 3. Add all unmatched Pass 2 facts
```

## Why Personal Types Prefer Pass 2

`opinion`, `habit`, `intention`, `experience` are types where the **user is the subject**. Pass 2 specifically targets user-role turns — its version of these facts is more reliable.

`world` and `action_effect` are not subject-specific. Pass 1's version is more comprehensive. Pass 2 doesn't even try to extract these types (see `PASS2_ALLOWED_FACT_TYPES` in `pass2.py`).

## Verify Commands

```bash
rg "dedup_facts" cogmem_api/engine/retain/fact_extraction.py
rg "PASS2_ALLOWED_FACT_TYPES" cogmem_api/
```
