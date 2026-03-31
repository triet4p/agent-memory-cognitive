"""Main orchestrator for the CogMem retain pipeline baseline (T2.1)."""

from __future__ import annotations

from collections.abc import Awaitable, Callable
from contextlib import asynccontextmanager
from datetime import UTC, datetime
from typing import Any

import asyncpg

from cogmem_api.engine.db_utils import acquire_with_retry, retry_with_backoff
from cogmem_api.engine.response_models import TokenUsage
from . import chunk_storage, embedding_processing, entity_processing, fact_extraction, fact_storage, link_creation
from .types import ProcessedFact, RetainContent, RetainContentDict, coerce_fact_type


def utcnow() -> datetime:
    """Timezone-aware UTC now helper."""
    return datetime.now(UTC)


def parse_datetime_flexible(value: Any) -> datetime:
    """Parse datetime or ISO string into timezone-aware datetime."""
    if isinstance(value, datetime):
        return value if value.tzinfo else value.replace(tzinfo=UTC)
    if isinstance(value, str):
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
        return parsed if parsed.tzinfo else parsed.replace(tzinfo=UTC)
    raise TypeError(f"Expected datetime or str, got {type(value).__name__}")


@asynccontextmanager
async def _maybe_transaction(conn):
    """Use connection transaction context when available."""
    transaction = getattr(conn, "transaction", None)
    if callable(transaction):
        ctx = transaction()
        async with ctx:
            yield
    else:
        yield


def _map_results_to_contents(contents: list[RetainContent], extracted_fact_count_by_content: dict[int, int], unit_ids: list[str]) -> list[list[str]]:
    """Map created unit IDs back to the original content index ordering."""
    results: list[list[str]] = []
    cursor = 0
    for content_index in range(len(contents)):
        count = extracted_fact_count_by_content.get(content_index, 0)
        results.append(unit_ids[cursor : cursor + count])
        cursor += count
    return results


async def retain_batch(
    pool,
    embeddings_model,
    llm_config,
    entity_resolver,
    format_date_fn,
    bank_id: str,
    contents_dicts: list[RetainContentDict],
    config,
    document_id: str | None = None,
    is_first_batch: bool = True,
    fact_type_override: str | None = None,
    confidence_score: float | None = None,
    document_tags: list[str] | None = None,
    operation_id: str | None = None,
    schema: str | None = None,
    outbox_callback: Callable[["asyncpg.Connection"], Awaitable[None]] | None = None,
) -> tuple[list[list[str]], TokenUsage]:
    """Process a retain batch end-to-end and return unit IDs per content item."""
    if not contents_dicts:
        return [], TokenUsage()

    contents: list[RetainContent] = []
    for payload in contents_dicts:
        normalized = dict(payload)
        if "event_date" not in normalized:
            normalized["event_date"] = utcnow()
        elif normalized.get("event_date") is not None:
            normalized["event_date"] = parse_datetime_flexible(normalized["event_date"])
        contents.append(RetainContent.from_dict(normalized))

    extracted_facts, chunks, usage = await fact_extraction.extract_facts_from_contents(
        contents=contents,
        llm_config=llm_config,
        agent_name=bank_id,
        config=config,
        pool=pool,
        operation_id=operation_id,
        schema=schema,
    )

    if fact_type_override:
        forced = coerce_fact_type(fact_type_override)
        for fact in extracted_facts:
            fact.fact_type = forced

    if not extracted_facts:
        return ([[] for _ in contents], usage)

    augmented_texts = embedding_processing.augment_texts_with_dates(extracted_facts, format_date_fn)
    embeddings = await embedding_processing.generate_embeddings_batch(embeddings_model, augmented_texts)

    processed_facts = [
        ProcessedFact.from_extracted_fact(extracted_fact=fact, embedding=embedding)
        for fact, embedding in zip(extracted_facts, embeddings)
    ]

    # Apply per-fact document IDs and optional shared document ID.
    for fact in processed_facts:
        source_doc = contents_dicts[fact.content_index].get("document_id")
        fact.document_id = source_doc or document_id

    created_unit_ids: list[str] = []

    async def _db_write_work() -> None:
        nonlocal created_unit_ids

        async with acquire_with_retry(pool) as conn:
            async with _maybe_transaction(conn):
                await fact_storage.ensure_bank_exists(conn, bank_id)

                if chunks and document_id:
                    chunk_id_map = await chunk_storage.store_chunks_batch(conn, bank_id, document_id, chunks)
                    for extracted_fact, processed_fact in zip(extracted_facts, processed_facts):
                        processed_fact.chunk_id = chunk_id_map.get(extracted_fact.chunk_index)

                created_unit_ids = await fact_storage.insert_facts_batch(
                    conn=conn,
                    bank_id=bank_id,
                    facts=processed_facts,
                    document_id=document_id,
                )

                user_entities_per_content = {
                    index: content.entities for index, content in enumerate(contents) if content.entities
                }
                entity_links = await entity_processing.process_entities_batch(
                    entity_resolver=entity_resolver,
                    conn=conn,
                    bank_id=bank_id,
                    unit_ids=created_unit_ids,
                    facts=processed_facts,
                    user_entities_per_content=user_entities_per_content,
                )

                embeddings_for_links = [fact.embedding for fact in processed_facts]
                await link_creation.create_temporal_links_batch(conn, bank_id, created_unit_ids)
                await link_creation.create_semantic_links_batch(conn, bank_id, created_unit_ids, embeddings_for_links)
                await entity_processing.insert_entity_links_batch(conn, entity_links)
                await link_creation.create_habit_sr_links_batch(conn, created_unit_ids, processed_facts)
                await link_creation.create_action_effect_links_batch(conn, created_unit_ids, processed_facts)
                await link_creation.create_transition_links_batch(conn, created_unit_ids, processed_facts)
                await link_creation.create_causal_links_batch(conn, created_unit_ids, processed_facts)

                if outbox_callback:
                    await outbox_callback(conn)

    await retry_with_backoff(_db_write_work)

    count_by_content: dict[int, int] = {}
    for fact in extracted_facts:
        count_by_content[fact.content_index] = count_by_content.get(fact.content_index, 0) + 1

    return _map_results_to_contents(contents, count_by_content, created_unit_ids), usage
