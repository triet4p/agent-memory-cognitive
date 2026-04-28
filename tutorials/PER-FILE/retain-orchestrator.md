# `orchestrator.py` — Retain Transaction Orchestrator

## Purpose

`orchestrator.py::retain_batch()` is the **only public entry point** for the entire retain pipeline. It is called by `MemoryEngine.retain_batch_async()` and coordinates all 6 sub-modules within a single DB transaction.

**Design principle: all-or-nothing.** If any step fails, the entire batch rolls back. No partial state.

## `_db_write_work()` — The Transaction Block

```python
async with acquire_with_retry(pool) as conn:
    async with _maybe_transaction(conn):
        # All writes happen here
        await fact_storage.ensure_bank_exists(conn, bank_id)
        if chunks:
            await chunk_storage.store_chunks_batch(conn, bank_id, document_id, chunks)
        created_unit_ids = await fact_storage.insert_facts_batch(...)
        # entity resolution
        entity_links = await entity_processing.process_entities_batch(...)
        await entity_processing.insert_entity_links_batch(conn, entity_links)
        # 7 link creation calls
        await link_creation.create_temporal_links_batch(...)
        await link_creation.create_semantic_links_batch(...)
        await link_creation.create_habit_sr_links_batch(...)
        await link_creation.create_action_effect_links_batch(...)
        await link_creation.create_transition_links_batch(...)
        await link_creation.create_causal_links_batch(...)
        if outbox_callback:
            await outbox_callback(conn)
```

## `utcnow()` and `parse_datetime_flexible()`

`utcnow()` returns timezone-aware `datetime.now(UTC)`. PostgreSQL's `TIMESTAMPTZ` requires timezone-aware timestamps — mixing naive and aware datetimes causes comparison errors.

`parse_datetime_flexible()` handles: datetime objects (add UTC if naive), ISO strings with `Z` (replace with `+00:00`), ISO strings without timezone (add UTC).

## `retain_batch()` Signature — Dependency Injection

The function takes explicit dependencies rather than importing globals:

```python
async def retain_batch(
    pool,                  # asyncpg connection pool
    embeddings_model,      # LocalST or OpenAI embeddings provider
    llm_config,            # LLMConfig (can be None for seeded path)
    entity_resolver,       # entity resolution service
    format_date_fn,        # date formatting for embeddings
    bank_id, contents_dicts, config, document_id, ...
)
```

This makes the function **testable**: tests inject fake/mock versions of all dependencies without starting the full server.

## `_map_results_to_contents()`

After all facts are inserted, we get back a flat list of `unit_ids`. But one content item can produce multiple facts. This function slices the flat list using `extracted_fact_count_by_content` (a dict mapping `content_index → fact count`).

## Failure Handling

The entire `_db_write_work()` is wrapped in `retry_with_backoff()` from `db_utils.py`. It retries on transient DB errors (connection loss, deadlock) with exponential backoff. It does NOT retry on logic errors (FK violation, unique constraint).

## Verify Commands

```bash
rg "create_.*_links_batch" cogmem_api/engine/retain/orchestrator.py
rg "^from \.|import " cogmem_api/engine/retain/orchestrator.py
```
