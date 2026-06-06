# Retain Pipeline Deep Dive

## Entry Point: `retain_batch()`

Located at `cogmem_api/engine/retain/orchestrator.py::retain_batch`.

This is the only public entry point for the entire retain pipeline. It receives raw content dicts and orchestrates six sub-modules in a single DB transaction:

```
retain_batch(pool, embeddings_model, llm_config, entity_resolver, format_date_fn,
             bank_id, contents_dicts, config, document_id, ...)
  │
  ├─→ fact_extraction.extract_facts_from_contents()
  │     (LLM-driven OR seeded fallback OR heuristic fallback)
  │
  ├─→ embedding_processing.augment_texts_with_dates()
  │     (+ generate_embeddings_batch())
  │
  ├─→ Map to ProcessedFact (with document_id + embedding)
  │
  └─→ _db_write_work() [transaction block]
        ├─→ fact_storage.ensure_bank_exists()
        ├─→ chunk_storage.store_chunks_batch()        (if document_id present)
        ├─→ fact_storage.insert_facts_batch()
        ├─→ entity_processing.process_entities_batch()
        │
        ├─ Phase A — in-session links
        │   ├─→ link_creation.create_temporal_links_batch()
        │   ├─→ link_creation.create_semantic_links_batch()
        │   ├─→ entity_processing.insert_entity_links_batch()
        │   ├─→ link_creation.create_habit_sr_links_batch()
        │   ├─→ link_creation.create_action_effect_links_batch()
        │   ├─→ link_creation.create_transition_links_batch()
        │   └─→ link_creation.create_causal_links_batch()
        │
        └─ Phase B — cross-session / cross-bank links
            ├─→ link_creation.create_cross_bank_semantic_links_batch()
            ├─→ entity_processing.build_cross_bank_entity_links() + insert_entity_links_batch()
            └─→ link_creation.create_cross_bank_structural_links_batch()
```

The whole `_db_write_work()` body runs inside one transaction wrapped by `retry_with_backoff()`. Two optional retain controls are applied *before* the write phase:
- `enabled_fact_types` — an allowlist that drops extracted facts whose type isn't permitted (S33 ablation).
- `agentic_transcript` — flag that switches Pass 1 to a prompt that parses agent `[tool]/[output]` tags (S34).

## Step 1 — Fact Extraction (`fact_extraction.py`)

### Two-Pass Architecture

When `content.messages` is present and `retain_two_pass_enabled=True`:

**Pass 1** (all roles, all content):
- Chunks the full conversation into ~10K char blocks via `chunk_for_pass1()`
- Sends each chunk to LLM with `build_pass1_prompt()` — extraction modes (concise/verbose/verbatim/custom) affect this prompt
- `_normalize_llm_facts()` converts JSON → `ExtractedFact`, applies temporal sanitization and heuristic type overrides

**Pass 2** (user-only, persona signals):
- Filters to user-role turns only, chunks at ~3K chars via `chunk_for_pass2()`
- Runs `build_pass2_prompt()` — persona-focused, targets `opinion`, `habit`, `intention`, `experience` types only
- `_normalize_llm_facts()` with `mode="concise"` and `extract_causal_links=False`
- Final result: `dedup_facts(facts_p1, facts_p2)` — Pass 2 preference for personal types

**Pass 3** (cross-chunk relations):
- After `dedup_facts(facts_p1, facts_p2)` merges the two passes, `_run_pass3()` sends the merged fact list to the LLM with `build_pass3_prompt()` ([prompts/retain/pass3.py](../../cogmem_api/prompts/retain/pass3.py))
- It mutates facts in place, appending `causal_relations`, `transition_relations`, and `action_effect_relations` discovered *across* chunks (relations a per-chunk pass can't see)
- Default on (`retain_pass3_enabled`), bounded to runs where the session has 2–30 facts

**Why multiple passes?** Assistant turns in mixed conversations dilute persona signals — a user saying "I love Python" gets lost among assistant tokens. Pass 2 isolates user turns with a prompt tuned for self-referential statements; Pass 3 then recovers relationships that only emerge once all facts are on the table.

### Temporal Sanitization (`_sanitize_temporal_fact()`)

SLMs hallucinate dates. When a conversation has no explicit time context, they fill `occurred_start` with today's date. This function detects that pattern and clears hallucinated temporal fields.

The key signal: if `fact_type == "world"`, always strip temporal fields (world facts are time-independent by definition). For other types, check if the date matches today and the text lacks real time context (`"today"`, `"now"`, `"current"`, etc.).

### Heuristic Type Overrides

The LLM frequently misclassifies. Three overrides fire after parsing:

1. **`world` → `habit`**: If `fact_text` contains `"always"`, `"usually"`, `"often"`, `"routine"`, etc., override to `habit`.
2. **`world` → `intention`**: If LLM returned `world` but `intention_status` is set, override to `intention`. World facts cannot have planning/fulfilled status.
3. **`experience` → `intention`**: If `what` text matches future-planning patterns (`"plans to"`, `"intends to"`, `"is going to"`), override to `intention`.

Additionally, `_infer_fulfilled_from_context()` checks whether a planning/intention fact should be reclassified as fulfilled based on completion signals in the chunk.

### Fallback Hierarchy

```
extract_facts_from_contents()
  ├─ if content.facts present → _extract_seeded_facts() [programmatic, no LLM]
  ├─ else if llm_config → _extract_facts_with_llm()
  │     ├─ PASS 1 + PASS 2 (if two_pass_enabled)
  │     └─ SINGLE-PASS (legacy, if no messages)
  └─ else → _extract_fallback_facts() [regex split, last resort]
```

## Step 2 — Entity Resolution (`entity_processing.py`)

After facts are stored, entities are resolved against the existing entity graph:

```
process_entities_batch(entity_resolver, conn, bank_id, unit_ids, facts, user_entities_per_content)
  ├─ For each fact: extract entity names from fact.entities or from text
  ├─ Normalize: lowercase, strip, deduplicate
  ├─ Resolve: look up existing unit_entities for this bank_id
  └─ Return list of (unit_id, entity_id) EntityLink pairs
```

Entity overlap is used as a proxy for `s_r_link` creation in `link_creation.py`. This is a simplification: spec intended behavioral reinforcement (habit formation from repeated patterns), but entity-overlap is a reasonable NL-dialogue proxy.

## Step 3 — Link Creation (`link_creation.py`)

Seven in-session (Phase A) edge types are created after fact storage:

1. **Temporal links** — ordered by `occurred_start` within each bank. Connects consecutive experience/intention nodes (weight decays with the time gap).
2. **Semantic links** — in-batch cosine similarity ≥ **0.6** threshold on embedding space. Bidirectional.
3. **Entity links** — created by `entity_processing.insert_entity_links_batch()` from resolved entity overlap.
4. **Causal links** — `causal_relations` extracted from fact payload. Directed.
5. **S-R links** — `create_habit_sr_links_batch()`. A habit fact links to the experience it triggered (weight scales with entity overlap).
6. **A-O causal links** — from `action_effect_relations`. Precondition→Action→Outcome triple.
7. **Transition links** — typed lifecycle edges: `fulfilled_by`, `triggered`, `enabled_by`, `revised_to`, `contradicted_by` (rules in `types.py::TRANSITION_EDGE_RULES`).

**Phase B — cross-bank links** then bridge the new units to facts in *other* banks:
- `create_cross_bank_semantic_links_batch()` — cosine ≥ `COGMEM_API_RETAIN_CROSS_BANK_SEMANTIC_THRESHOLD` (default 0.75), top-K = 4
- `build_cross_bank_entity_links()` — shared entities across banks
- `create_cross_bank_structural_links_batch()` — structural bridges

Key design: all link creation uses **bulk INSERT** with `executemany` for performance. Each link type has its own batch function to allow independent error handling.

## Lossless Layer: `raw_snippet`

Every `ExtractedFact` carries a `raw_snippet` — the original text chunk from which the fact was extracted. This is stored in `ProcessedFact.metadata["raw_snippet"]`.

The problem it solves: LLM extraction is lossy compression. "I got a 40% raise when moving to DI" becomes "User moved to DI with higher salary." The specific 40% detail is lost.

During retrieval (S23+), `raw_snippet` is injected into the generation context so that reflect synthesis can access verbatim details.

## Transaction Behavior

All DB writes happen inside a single transaction. If any step fails (FK violation, unique constraint, connection loss), the entire batch rolls back. No partial state.

The `_maybe_transaction()` helper handles both bare connections and explicit transaction contexts, making it usable with `acquire_with_retry()` which may return a connection in autocommit mode.

## Verify Commands

```bash
# Run retain baseline test
uv run python tests/artifacts/test_task201_retain_baseline.py

# Check two-pass is wired correctly
rg "two_pass_enabled|build_pass1_prompt|build_pass2_prompt" cogmem_api/engine/retain/fact_extraction.py

# Check raw_snippet is stored
rg "raw_snippet" cogmem_api/engine/retain/
# Should find: assignment in _normalize_llm_facts, usage in ProcessedFact construction
```
