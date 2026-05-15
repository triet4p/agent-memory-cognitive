# Sprint S29: Recall, Retain, Routing & Generation Quality

**Date:** 2026-05-15
**Author:** Synthesized from S28-Diag (35 audit reports + VERDICTS + DIAGNOSIS)
**Status:** 🔄 Active

**Phụ thuộc:** S28 Wave-1 ✅ + S28-Diag Parts 1-3 ✅

---

## Context

**Why this sprint:** S28 Wave-1 + S28-Diag (Parts 1-3) just completed. Truthful verification shows **24/35 PASS, 11/35 FAIL** on LongMemEval E7 (CP5 baseline preserved through Wave-1 — c014 moved PASS via G1, c019 newly discovered FAIL).

**Goal:** Push truthful PASS rate from 24/35 (68.6%) to **≥32/35 (91.4%)** — i.e., fix at least **8 of 11 FAIL cases** without regressing the 24 confirmed PASSes.

**Evidence base:** All 11 root causes are empirically classified in [DIAGNOSIS.md](../../experiments/v14/diagnostic_s28/DIAGNOSIS.md), [VERDICTS.md](../../experiments/v14/diagnostic_s28/VERDICTS.md), and 35 per-case reports. This sprint maps each root cause to a specific code-level fix with named files and expected case wins.

---

## FAIL Inventory (mechanism → cases)

| # | Mechanism | Cases | Stage |
|---|-----------|-------|-------|
| M1 | **Preference routing blind spot** (no preference pattern match → fallback `semantic`, uniform weights) | c030, c031, c032, c033 | Routing |
| M2 | **Retain-miss of user-specific named entities & numeric values** (Luna, Jen, power bank, Memrise, Celeste-10h) | c006, c007, c029, c031, c033 | Retain |
| M3 | **Cross-session semantic over-bridging** (200 semantic links per fact, 83% cross-session) | c000, c001, c007 | Graph/Retain |
| M4 | **Generic noun treated as named entity** ("project", "wedding", "team" → cross-persona links) | c000, c007 | Retain |
| M5 | **Multi-hop priority shadows temporal** ("how many days ago" → multi_hop instead of temporal) | c019 | Routing |
| M6 | **Generation: scale-variant double-count / persona-conflation / off-by-one / entity-aliasing** | c000, c001, c007, c019, c023, c032 | Generation |
| M7 | **CE suppression of multi-channel-strong fact** (sem≤5, bm25≤10, graph≤10, but CE<-10 → outside top-25) | c001 (Tiger I rank 27), c030 (Suica travel-cost) | Ranking |
| M8 | **Temporal link weight uniformity** (delta_s≈0 for same-session → all weights = 1.0) | c001, c000 (secondary) | Graph |

Each case is driven by 1-3 of these mechanisms; many fixes are compounding.

---

## Fix Roadmap — split by priority and expected case-delta

> **Wave 2A** = no re-retain needed (code-only, deploy on current v14 banks).
> **Wave 2B** = requires v15 re-retain (retain prompt + linker changes).
>
> Recommend running Wave 2A first, measure delta, then commit to Wave 2B.

---

### Priority P0 — Wave 2A — Routing & Generation (no re-retain)

**Expected wins:** c019 (full), c030 (full), c032 (full), c000 (partial), c001 (partial), c007 (partial), c023 (partial).
**Estimated cumulative delta:** +4 to +5 cases.

#### Fix R-1: Expand `_PREFERENCE_PATTERN` for conversational preference signals

- **File:** [cogmem_api/engine/query_analyzer.py](../../cogmem_api/engine/query_analyzer.py) (line ~40: `_PREFERENCE_PATTERN`)
- **Why:** 4 FAIL cases (c030, c031, c032, c033) phrase preference queries as conversation ("any tips?", "do you have helpful tips?", "I was wondering if you could remind me", "thinking of inviting…tips on what to bake?"). None match the current regex (`prefer|preference|favorite|like|dislike|love|hate|usually choose`). They fall through to `semantic` (uniform 1.0/1.0/1.0/1.0) instead of `preference` (1.0/**1.2**/**1.4**/**0.5**) — losing BM25 boost for named entities (Suica, TripIt, lemon poppyseed) and bleeding noise from temporal channel.
- **Change:** Add conversational signals: `any\s+tips|helpful\s+tips|what\s+(should|would|do)\s+you\s+recommend|remind\s+me\s+(of|about)|wondering\s+if|thinking\s+of\s+\w+ing|do\s+you\s+have`. Verify ALL 35 queries with a static-sweep test to confirm zero false-positive reclassification.
- **How it helps each case:**
  - **c030** (Suica + TripIt): BM25 boost (1.0 → 1.2) raises specific-entity names ("Suica", "TripIt") above generic Tokyo Tower/Park Hyatt noise; temporal demotion (1.0 → 0.5) reduces old-travel-fact bleed.
  - **c032** (lemon poppyseed at rank 1 but cookies chosen): temporal demotion removes "plans to bake cookies" noise that crowds ranks 2-5; preference-weighted re-rank stabilizes top-3.
  - **c031, c033**: routing now correct; but full fix still requires Retain change (M2) below.

#### Fix R-2: Reorder `classify_query_type` — temporal before multi_hop

- **File:** [cogmem_api/engine/query_analyzer.py](../../cogmem_api/engine/query_analyzer.py) (lines ~96-111: `classify_query_type`)
- **Why:** c019 query "How many days **ago** did I attend a baking class?" matches `_MULTI_HOP_PATTERN` ("how many") before `_TEMPORAL_HINT_PATTERN` ("ago"). Gets multi_hop weights (graph=2.6, temporal=0.8) instead of correct temporal (temporal=2.2). Recall didn't fail (facts at ranks 1, 3, 4) but the LLM then computed 20 days instead of 21 (off-by-one). Correct routing primes the model with temporal-grounded scoring.
- **Change:** Either reorder so temporal runs before multi_hop; OR add a compound check: if both patterns match AND temporal-anchor word ("ago", "since", "before") is present, prefer `temporal`. Verify static sweep on 35 queries — only c019 should reclassify.
- **How it helps:** c019 routing corrected; combined with G-3 (below) gives explicit day-count reasoning prompt → fix off-by-one.

#### Fix G-1: Generation — persona-separation hint

- **File:** [cogmem_api/prompts/eval/generate.py](../../cogmem_api/prompts/eval/generate.py)
- **Why:** c000 noise session `2e4430d8_2` ("senior SWE leadership", "high-priority project", "product launch") and c007 noise session `81b971b8_2` ("sister's wedding") share vocabulary with gold sessions. The model treats them as the user's own events — c000 counts 5 projects instead of 2; c007 counts 4 weddings instead of 3.
- **Change:** Add prompt instruction:

  > *"When counting events/items belonging to the user, examine subject/possessive cues. A memory mentioning another person's event (e.g., 'sister's wedding', 'team's high-priority project') without explicit user participation should NOT be counted as the user's own event. Only count events where the user is the explicit actor or participant."*

- **How it helps:** c000 strips out "senior SWE leadership" / "discussing project goals" entries → counts 2 (user-led marketing + user-led data mining). c007 strips out "sister's wedding" → counts 3. Compounds with M3 graph fix in Wave 2B.

#### Fix G-2: Generation — scale-variant collapsing

- **File:** same as G-1.
- **Why:** c001 model counts F-15 Eagle 1/72 and F-15 Eagle 1/48 as two separate kits (6 total) — gold answer is 5 (F-15 Eagle counted once even though two scale variants of the same product exist in bank).
- **Change:** Add instruction:

  > *"When counting distinct products, scale/version variants of the same named product (e.g., '1/72 F-15 Eagle' and '1/48 F-15 Eagle') refer to the same model line and should be counted as ONE item unless the question explicitly asks about variants."*

- **How it helps:** c001 collapses F-15 1/72 + F-15 1/48 to one → counts 5. Note: c001 also needs CE-floor fix (P3) for Tiger I to even reach top-25.

#### Fix G-3: Generation — explicit day-arithmetic guidance

- **File:** same as G-1.
- **Why:** c019 model computed 20 days instead of 21. The fact text is "yesterday" relative to a session date 22 days before the query date.
- **Change:** Add instruction for temporal `how many days ago` questions:

  > *"For 'how many days ago' questions: identify the session date, then compute `query_date - session_date` in days. If the source fact uses 'yesterday', the event date is session_date - 1. Show the arithmetic step-by-step. The answer is INCLUSIVE of both endpoints if requested."*

- **How it helps:** c019 off-by-one resolved.

#### Fix G-4: Generation — entity-aliasing for descriptive references

- **File:** same as G-1. (Strengthen the G2 instruction added in Wave 1 — currently ineffective.)
- **Why:** c023 model said "no direct record" despite fact at rank 2 ("realized it is worth triple what they paid") because gold uses "sunset painting" but fact uses "flea market find". G2 already added a soft hint that didn't trigger.
- **Change:** Strengthen to:

  > *"If a recalled memory describes an item by its acquisition context (e.g., 'flea market find', 'Etsy purchase') and the query references it by visual/topical description (e.g., 'painting of a sunset'), assume they refer to the same object UNLESS contradicted by another memory. Use the value/quantitative information from such memories to answer."*

- **How it helps:** c023 finds "worth triple what they paid" → correct answer.

---

### Priority P1 — Wave 2B — Retain & Graph (requires v15 re-retain)

**Expected wins:** c006 (full), c029 (full), c031 (full), c033 (full), c007 (partial — Jen entity), c000 (partial — entity blocklist), c001 (partial — semantic cap).
**Estimated cumulative delta:** +3 to +4 cases on top of Wave 2A.

#### Fix T-1: Retain prompt — extract user-specific named entities, purchases, numeric values

- **File:** [cogmem_api/prompts/retain/pass1.py](../../cogmem_api/prompts/retain/pass1.py) (extraction guidelines) and [pass2.py](../../cogmem_api/prompts/retain/pass2.py) if speaker-aware.
- **Why (4-5 cases):** Diagnostic confirmed by Phase-1 fact inventory that key user-specific details exist in `raw_snippet` but were never extracted as facts:
  - **c006** Celeste 10h: raw says "Celeste, which took me 10 hours to complete" — no fact created.
  - **c029** Cat Luna shedding, recent deep clean, sneezing — all in raw, none extracted.
  - **c031** Portable power bank: extracted only as part of generic "travel case with power bank compartment" world fact, not as user purchase.
  - **c033** Memrise app: assistant said "Memrise uses mnemonics" — no fact.
  - **c007** Friend Jen as wedding bride: fact `9648370e` exists but "Jen" was not extracted as an entity → channel-level miss (zero across sem/bm25/graph/temporal).
- **Change:** Add explicit extraction guidelines to the prompt:

  > *Always extract as separate facts:*
  > 1. *Named pets, people, products, apps, places mentioned by the user (e.g., "Luna", "Jen", "TripIt", "Memrise", "power bank") — store as `world` facts with the entity tagged.*
  > 2. *Explicit user purchases/acquisitions ("I bought X", "I picked up X") — store as `experience` facts.*
  > 3. *Explicit numeric values in user utterances about themselves (durations: "took me 10 hours", quantities, prices) — store as `experience` with numeric metadata.*
  > 4. *Recent user actions affecting their environment ("I deep cleaned the living room", "I attended X") — store as `experience` with `occurred_*`.*
  > 5. *Assistant recommendations of specific named tools/apps/products — store as `world` facts ("Assistant recommended X for purpose Y").*

- **How it helps each case:**
  - **c006**: Celeste 10h fact created → model computes 70+30+25+5+10=140 ✓.
  - **c029**: Luna+deep-clean+sneezing facts created → model answers personalized ("cat Luna's shedding + recent deep clean") ✓.
  - **c031**: User-purchased-power-bank fact created → semantic match for "battery life" question via cross-encoder context ✓.
  - **c033**: Memrise-mnemonics fact created → recall hit ✓.
  - **c007**: Jen entity links exist → fact 9648370e reachable via entity graph; combined with G-1 persona fix gets correct count.

#### Fix T-2: Entity blocklist — block generic nouns from becoming entity nodes

- **File:** [cogmem_api/engine/retain/entity_processing.py](../../cogmem_api/engine/retain/entity_processing.py) and config.
- **Why (3 cases):** Per c007 audit Phase-3 graph analysis: keyword search on "wedding" returned 23 entity links, INCLUDING cross-session bridges between gold session and noise session `81b971b8_2`. "wedding" is a shared CONCEPT, not a named entity. Same pattern likely for "project" in c000, "team" in c000, "model kit" in c001. These generic-noun entity links are what makes BFS amplify noise.
- **Change:**
  1. Extend the existing blocklist (S27 added one — verify what's there) with a curated list of generic event/concept nouns (`wedding`, `project`, `team`, `class`, `meeting`, `birthday`, `dinner`, `trip`, `cake`, `model kit`, etc.).
  2. Add a heuristic: an entity must be ProperCase OR contain a discriminating modifier (e.g., "Rachel's wedding" → keep; bare "wedding" → block).
  3. Re-link existing v14 facts before re-retain to validate impact before recommitting v15.
- **How it helps:**
  - **c000**: noise session 2e4430d8_2 no longer linked to gold session via "project" entity → BFS doesn't amplify noise. Combined with G-1 persona prompt → count 2 ✓.
  - **c007**: noise session 81b971b8_2 no longer linked via "wedding" entity → top-25 less polluted. Combined with G-1 → count 3 ✓.
  - **c001**: less cross-session linkage on "model kit" → Tiger I and Spitfire less diluted in BFS budget.

#### Fix G-5: Cross-session semantic link cap

- **File:** [cogmem_api/engine/retain/link_creation.py](../../cogmem_api/engine/retain/link_creation.py) (lines 197-245: `create_cross_bank_semantic_links_batch`).
- **Why (3 cases):** c001 Phase-3 shows Tiger I has **200 semantic links, 166 cross-session (83%), avg weight 0.76**. Threshold 0.6 + top_k=10 per fact creates a wall of cross-session edges that consume BFS per_source_limit=20 → Tiger I gets graph_rank=48 → rrf_rank=124 → CE drops it to rank 27 (outside top-25). c000 and c007 have analogous patterns.
- **Change:**
  1. **Raise cross-session semantic threshold from 0.6 → 0.75** (intra-session can stay 0.6).
  2. **Reduce cross-session top_k per fact from 10 → 4**.
  3. **Optional: amplify weight differentiation during BFS propagation** — square the semantic weight in [graph_retrieval.py](../../cogmem_api/engine/graph_retrieval.py) (lines 343-344) so 0.62 becomes 0.38 (vs entity 1.0² = 1.0). Currently 0.62 × 0.8 = 0.50 — only 35% weaker than entity.
- **How it helps:** Tiger I's cross-session bridges drop from 166 to <40, BFS reaches Tiger I in ≤20 steps → graph_rank ≤6 → rrf_rank ≤15 → survives CE cut, lands in top-15. c001 generation then sees Tiger I + applies G-2 collapse → counts 5 ✓.

#### Fix G-6: Temporal link weight differentiation (optional, secondary)

- **File:** [cogmem_api/engine/retain/link_creation.py](../../cogmem_api/engine/retain/link_creation.py) (line ~289)
- **Why:** Live API audit (DIAGNOSIS §Link Weight Quality) confirms every temporal link has weight=1.0 because `weight = max(0.3, 1.0 - delta_s/86400)` and same-session facts have delta_s ≈ 0. BFS treats all temporal neighbors identically.
- **Change:** Switch denominator from 1 day (86400s) to e.g. 1 hour (3600s) for intra-session, OR add a secondary recency term. Validate that intra-session weights span 0.5-1.0 instead of all 1.0.
- **How it helps:** Indirect — improves BFS noise discrimination broadly. Marginal individual-case win; main value is hardening passing cases against regression.

---

### Priority P2 — CE/Ranking robustness (Wave 2A, low risk)

**Expected wins:** c001 (Tiger I survives → +1), c030 (Suica travel-cost → consolidates partial), prevents PASS-case regression.
**Estimated delta:** +1.

#### Fix C-1: Multi-channel-strong CE floor

- **File:** [cogmem_api/engine/memory_engine.py](../../cogmem_api/engine/memory_engine.py) or [reranking.py](../../cogmem_api/engine/search/reranking.py)
- **Why:** Across all 35 cases, **4 AR facts had all channels rank ≤10 but CE < -10.0** and got dropped from top-25:
  - c030 fact `8974d7c7` (Suica travel-cost): sem=2, bm25=4, graph=2, but CE=-11.27 → rank 33.
  - c031 fact `260bdf66`: sem=10, bm25=82, graph=118, CE=-11.13.
  - c032 fact `fe4c78f1`: sem=6, bm25=8, graph=6, CE=-10.83 → rank 14 (in top-25 but dominated).
  - c001 fact `49689465` (Tiger I): sem=12, bm25=8, graph=48, CE=-9.83 → rank 27.

  Wave-1 R1-CE RRF boost helps but isn't enough at extreme CE values.

- **Change:** Add a "consensus floor" rule applied AFTER `apply_combined_scoring`:

  > *If a fact has semantic_rank ≤ 5 AND bm25_rank ≤ 10 AND graph_rank ≤ 10, force its final rank to ≤ 15 regardless of CE score.*

  Implementation: post-CE re-rank pass that promotes "consensus-strong" facts into a reserved top-15 slot.

- **How it helps:** c030 Suica travel-cost lands in top-15 → preference query gets all 3 AR facts → model enumerates Suica + TripIt ✓. c001 Tiger I lands in top-15 → with G-2 collapse → counts 5 ✓.

#### Fix C-2 (alternative to C-1): Raise RRF alpha

- **File:** [cogmem_api/engine/search/reranking.py](../../cogmem_api/engine/search/reranking.py) (`_RRF_ALPHA`)
- **Change:** Bump `_RRF_ALPHA` from 1.5 to 2.5 (or higher) for stronger rank boost. Cheaper than C-1 but coarser.
- **Tradeoff:** May over-boost RRF-strong but topically-tangential facts. C-1 is safer.

---

## Expected case-by-case delta (sum)

| Case | Wave 2A fixes that help | Wave 2B fixes that help | Expected verdict |
|------|------------------------|------------------------|------------------|
| c000 | G-1 (persona) | T-2 (entity blocklist), G-5 (semantic cap) | **PASS** |
| c001 | G-2 (scale collapse), C-1 (CE floor) | G-5 (semantic cap) | **PASS** |
| c006 | — | T-1 (extract Celeste 10h) | **PASS** |
| c007 | G-1 (persona) | T-1 (Jen entity), T-2 (wedding blocklist), G-5 | **PASS** |
| c019 | R-2 (temporal priority), G-3 (day arithmetic) | — | **PASS** |
| c023 | G-4 (entity aliasing) | — | **PASS (high prob)** |
| c029 | — | T-1 (Luna + deep clean) | **PASS** |
| c030 | R-1 (preference), C-1 (CE floor) | — | **PASS** |
| c031 | R-1 (preference) | T-1 (user purchased power bank) | **PASS** |
| c032 | R-1 (preference) | — | **PASS** |
| c033 | R-1 (preference) | T-1 (Memrise) | **PASS** |

**Projected:** **35/35 if all fixes land cleanly.** Realistic target after dual sources of risk (regression, partial wins): **32-34 PASS**.

---

## Risk register & regression guards

1. **Preference pattern overreach** — broaden too far and PASS cases get reclassified.
   - Mitigation: static-sweep validation on all 35 queries before deploy; only c030/c031/c032/c033 should change.
2. **Re-retain cost** — v15 builds 35 banks via Kaggle/NGROK LLM; expensive and slow.
   - Mitigation: validate Wave 2A first; only commit to Wave 2B re-retain after retain-prompt diff has been unit-tested on 3-5 sample sessions.
3. **Entity blocklist over-aggressive** — blocking "team" may remove legitimate user-team links.
   - Mitigation: keep blocklist conservative (~15-30 generic event nouns); rely on ProperCase + modifier heuristic for the rest.
4. **Semantic threshold raise hurts marginal PASS cases** (c002 Bell Zephyr at rank 18, c024 lavender gin fizz at rank 17).
   - Mitigation: top-15 projection in DIAGNOSIS shows these still survive at top-25; recheck after re-retain.
5. **G-1 persona prompt over-corrects** — model might drop legitimate user-attended-other-person's-event facts.
   - Mitigation: phrase as "without explicit user participation" — preserves "User attended cousin Rachel's wedding".

---

## Sequencing & exit gates

### Wave 2A (1-2 day implementation, hours of validation)
1. Implement R-1, R-2, G-1, G-2, G-3, G-4, C-1.
2. Run full 35-case eval on existing v14 banks.
3. Gate: ≥27 PASS (24 baseline + ≥3 case wins; no PASS-case regression).

### Wave 2B (re-retain + linker changes)
1. Implement T-1, T-2, G-5 (optionally G-6).
2. Unit-test retain prompt on 3 representative sessions (compare extracted-fact count + types).
3. Re-retain all 35 banks into v15.
4. Re-run eval.
5. Gate: ≥32 PASS truthful (verified via `cogmem-verify`).

### S-final
- Full ablation dry run (E1-E7) on v15 banks.

---

## Critical files to modify

- [cogmem_api/engine/query_analyzer.py](../../cogmem_api/engine/query_analyzer.py) — R-1, R-2
- [cogmem_api/prompts/eval/generate.py](../../cogmem_api/prompts/eval/generate.py) — G-1..G-4
- [cogmem_api/engine/memory_engine.py](../../cogmem_api/engine/memory_engine.py) — C-1
- [cogmem_api/engine/search/reranking.py](../../cogmem_api/engine/search/reranking.py) — C-1 alt / C-2
- [cogmem_api/prompts/retain/pass1.py](../../cogmem_api/prompts/retain/pass1.py) — T-1
- [cogmem_api/engine/retain/entity_processing.py](../../cogmem_api/engine/retain/entity_processing.py) — T-2
- [cogmem_api/engine/retain/link_creation.py](../../cogmem_api/engine/retain/link_creation.py) — G-5, G-6
- [cogmem_api/engine/graph_retrieval.py](../../cogmem_api/engine/graph_retrieval.py) — G-5 (BFS propagation amplification)

---

## Verification

Per-fix tests under `tests/artifacts/`:
- `test_task_s29_wave2a.py` — static checks (regex sweep on 35 queries, prompt-string presence, CE-floor unit test on mock candidates).
- `test_task_s29_wave2b.py` — retain-extract unit test (feed 3 sample dialogues, assert Luna/power-bank/Memrise/Celeste-10h/Jen facts appear), entity-blocklist test, link-creation cap test.

End-to-end:
- Run `experiments/v14/run_e7_full.py` (or equivalent) → produces new checkpoints.
- Run `cogmem-verify` on c000-c034 → write `VERDICTS_v15.md`.
- Compare to baseline VERDICTS.md; document deltas in `experiments/v15/diagnostic_s29/`.

---

## Exit Gate Sprint S29

| Gate | Condition | Status |
|------|-----------|--------|
| W2A-R1 | `_PREFERENCE_PATTERN` expanded; static sweep 35 queries — only c030/c031/c032/c033 reclassify | 🔄 Pending |
| W2A-R2 | temporal before multi_hop; c019 reclassifies | 🔄 Pending |
| W2A-G1 | persona-separation instruction in generate.py | 🔄 Pending |
| W2A-G2 | scale-variant collapse instruction in generate.py | 🔄 Pending |
| W2A-G3 | day-arithmetic instruction in generate.py | 🔄 Pending |
| W2A-G4 | entity-aliasing instruction strengthened in generate.py | 🔄 Pending |
| W2A-C1 | consensus floor post-CE re-rank implemented | 🔄 Pending |
| W2A-artifact | test_task_s29_wave2a.py: all static checks PASS | 🔄 Pending |
| W2A-eval | ≥27/35 PASS on v14 banks (no PASS-case regression) | 🔄 Pending |
| W2B-T1 | retain prompt updated; unit test on 3 sessions extracts Luna/power-bank/Memrise/Celeste-10h/Jen | 🔄 Pending |
| W2B-T2 | entity blocklist updated; generic nouns blocked | 🔄 Pending |
| W2B-G5 | cross-session semantic threshold 0.6→0.75, top_k 10→4 | 🔄 Pending |
| W2B-reretain | v15 banks re-retained | 🔄 Pending |
| W2B-artifact | test_task_s29_wave2b.py: all checks PASS | 🔄 Pending |
| W2B-eval | ≥32/35 PASS truthful via cogmem-verify on v15 banks | 🔄 Pending |
