"""Entity processing for retain pipeline."""

from __future__ import annotations

import uuid

from cogmem_api.engine.memory_engine import fq_table

from . import link_utils
from .types import EntityLink, ProcessedFact

# Generic pronouns / placeholders that appear in virtually every fact.
# Including them in entity links creates a near-fully-connected hub that
# dilutes BFS spreading-activation signal.
_ENTITY_BLOCKLIST: frozenset[str] = frozenset({
    "user", "the user", "i", "me", "my", "we", "our",
    # Generic event/concept nouns (S29 T-2) — shared vocabulary across
    # sessions that creates false cross-session bridges in BFS.
    "wedding", "project", "team", "class", "meeting", "birthday",
    "dinner", "trip", "cake", "model kit",
})

# All-lowercase single words in this set are never proper nouns.
# Entities matching this pattern without possessive/modifier get blocked.
_GENERIC_NOUN_SET: frozenset[str] = frozenset({
    "wedding", "project", "team", "class", "meeting", "birthday",
    "dinner", "trip", "cake", "kit", "event", "party", "concert",
    "session", "course", "lesson", "workshop", "seminar",
    "app", "tool", "game", "movie", "book", "website",
})


def _normalize_entity_name(entity: str) -> str:
    return entity.strip().lower()


def _is_allowed_entity(entity_name: str) -> bool:
    """Check if an entity name should be kept (not blocked).

    Blocks entities that:
    1. Are in the explicit blocklist (exact match after normalization).
    2. Are all-lowercase, lack a possessive modifier (no \"'s\"), and match
       a known generic noun — these are not proper nouns.
    """
    normalized = _normalize_entity_name(entity_name)
    if normalized in _ENTITY_BLOCKLIST:
        return False
    # Heuristic: all-lowercase entities without possessive modifier that
    # match a generic noun are unlikely to be true named entities.
    if not any(c.isupper() for c in entity_name) and "'s" not in entity_name:
        words = normalized.split()
        if any(w in _GENERIC_NOUN_SET for w in words):
            return False
    return True


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
            if entity and entity.strip() and _is_allowed_entity(entity):
                merged_entities.add(entity.strip())

        if user_entities_per_content:
            for payload in user_entities_per_content.get(fact.content_index, []):
                text = str(payload.get("text", "")).strip()
                if text:
                    merged_entities.add(text)

        unit_to_entities[unit_id] = merged_entities

    unit_entity_pairs: list[tuple[str, str]] = []
    entity_index: dict[str, list[str]] = {}
    entity_name_map: dict[str, str] = {}

    for unit_id, entities in unit_to_entities.items():
        for entity_name in entities:
            entity_id = _resolve_entity_id(bank_id, entity_name)
            unit_entity_pairs.append((unit_id, entity_id))
            entity_index.setdefault(entity_id, []).append(unit_id)
            entity_name_map[entity_id] = entity_name.strip()

    if hasattr(conn, "insert_unit_entities"):
        await conn.insert_unit_entities(unit_entity_pairs)
    elif entity_name_map:
        await conn.executemany(
            f"INSERT INTO {fq_table('entities')} (id, canonical_name, bank_id, metadata) "
            f"VALUES ($1::uuid, $2, $3, '{{}}'::jsonb) ON CONFLICT (id) DO NOTHING",
            [(eid, name, bank_id) for eid, name in entity_name_map.items()],
        )
        if unit_entity_pairs:
            await conn.executemany(
                f"INSERT INTO {fq_table('unit_entities')} (unit_id, entity_id) "
                f"VALUES ($1::uuid, $2::uuid) ON CONFLICT DO NOTHING",
                unit_entity_pairs,
            )

    links: list[EntityLink] = []
    for entity_id, linked_units in entity_index.items():
        for i, source_id in enumerate(linked_units):
            for target_id in linked_units[i + 1 :]:
                links.append(EntityLink(from_unit_id=source_id, to_unit_id=target_id, entity_id=entity_id))
                links.append(EntityLink(from_unit_id=target_id, to_unit_id=source_id, entity_id=entity_id))

    return links


async def build_cross_bank_entity_links(
    conn,
    bank_id: str,
    new_unit_ids: list[str],
    new_facts: list[ProcessedFact],
) -> list[EntityLink]:
    """Cross-session: for each non-blocked entity in new facts, find existing units
    in the bank that share that entity and create bidirectional entity links."""
    if not new_unit_ids or not new_facts:
        return []

    links: list[EntityLink] = []
    seen_pairs: set[tuple[str, str]] = set()

    for new_uid, fact in zip(new_unit_ids, new_facts):
        for entity_name in fact.entities:
            if not entity_name or not entity_name.strip() or not _is_allowed_entity(entity_name):
                continue

            entity_id = _resolve_entity_id(bank_id, entity_name)

            if hasattr(conn, "get_entity_unit_ids"):
                existing_uids = await conn.get_entity_unit_ids(entity_id, new_unit_ids)
            else:
                rows = await conn.fetch(
                    f"""
                    SELECT DISTINCT unit_id::text AS uid
                    FROM {fq_table("unit_entities")}
                    WHERE entity_id = $1::uuid
                      AND unit_id::text != ALL($2::text[])
                    """,
                    entity_id,
                    new_unit_ids,
                )
                existing_uids = [str(row["uid"]) for row in rows]

            for existing_uid in existing_uids:
                pair = (new_uid, existing_uid)
                reverse = (existing_uid, new_uid)
                if pair not in seen_pairs:
                    seen_pairs.add(pair)
                    seen_pairs.add(reverse)
                    links.append(EntityLink(from_unit_id=new_uid, to_unit_id=existing_uid, entity_id=entity_id))
                    links.append(EntityLink(from_unit_id=existing_uid, to_unit_id=new_uid, entity_id=entity_id))

    return links


async def insert_entity_links_batch(conn, entity_links: list[EntityLink]) -> None:
    """Persist entity links into memory_links table."""
    link_records: list[link_utils.LinkRecord] = [
        (link.from_unit_id, link.to_unit_id, link.link_type, None, link.entity_id, link.weight) for link in entity_links
    ]
    await link_utils.insert_links(conn, link_records)
