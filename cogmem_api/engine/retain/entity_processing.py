"""Entity processing for retain pipeline."""

from __future__ import annotations

import uuid

from . import link_utils
from .types import EntityLink, ProcessedFact


def _normalize_entity_name(entity: str) -> str:
    return entity.strip().lower()


def _resolve_entity_id(bank_id: str, entity_name: str) -> str:
    """Deterministic entity-id generation for baseline pipeline."""
    key = f"{bank_id}:{_normalize_entity_name(entity_name)}"
    return str(uuid.uuid5(uuid.NAMESPACE_DNS, key))


async def process_entities_batch(
    entity_resolver,
    conn,
    bank_id: str,
    unit_ids: list[str],
    facts: list[ProcessedFact],
    log_buffer: list[str] | None = None,
    user_entities_per_content: dict[int, list[dict]] | None = None,
    entity_labels: list | None = None,
) -> list[EntityLink]:
    """Resolve entities and build unit-to-unit entity links."""
    if not unit_ids or not facts:
        return []

    unit_to_entities: dict[str, set[str]] = {}
    for unit_id, fact in zip(unit_ids, facts):
        merged_entities: set[str] = set()

        for entity in fact.entities:
            if entity and entity.strip():
                merged_entities.add(entity.strip())

        if user_entities_per_content:
            for payload in user_entities_per_content.get(fact.content_index, []):
                text = str(payload.get("text", "")).strip()
                if text:
                    merged_entities.add(text)

        unit_to_entities[unit_id] = merged_entities

    unit_entity_pairs: list[tuple[str, str]] = []
    entity_index: dict[str, list[str]] = {}

    for unit_id, entities in unit_to_entities.items():
        for entity_name in entities:
            entity_id = _resolve_entity_id(bank_id, entity_name)
            unit_entity_pairs.append((unit_id, entity_id))
            entity_index.setdefault(entity_id, []).append(unit_id)

    if hasattr(conn, "insert_unit_entities"):
        await conn.insert_unit_entities(unit_entity_pairs)

    links: list[EntityLink] = []
    for entity_id, linked_units in entity_index.items():
        for i, source_id in enumerate(linked_units):
            for target_id in linked_units[i + 1 :]:
                links.append(EntityLink(from_unit_id=source_id, to_unit_id=target_id, entity_id=entity_id))
                links.append(EntityLink(from_unit_id=target_id, to_unit_id=source_id, entity_id=entity_id))

    return links


async def insert_entity_links_batch(conn, entity_links: list[EntityLink]) -> None:
    """Persist entity links into memory_links table."""
    link_records: list[link_utils.LinkRecord] = [
        (link.from_unit_id, link.to_unit_id, link.link_type, None, link.entity_id, link.weight) for link in entity_links
    ]
    await link_utils.insert_links(conn, link_records)
