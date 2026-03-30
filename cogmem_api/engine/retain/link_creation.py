"""Link creation orchestration for retain pipeline."""

from __future__ import annotations

from . import link_utils
from .types import ProcessedFact


async def create_temporal_links_batch(conn, bank_id: str, unit_ids: list[str]) -> int:
    """Create temporal links for units close in time."""
    unit_dates = await link_utils.fetch_event_dates(conn, unit_ids)
    links = link_utils.build_temporal_links(unit_dates)
    return await link_utils.insert_links(conn, links)


async def create_semantic_links_batch(conn, bank_id: str, unit_ids: list[str], embeddings: list[list[float]]) -> int:
    """Create semantic links using in-batch cosine similarity."""
    links = link_utils.build_semantic_links(unit_ids, embeddings, threshold=0.6)
    return await link_utils.insert_links(conn, links)


async def create_causal_links_batch(conn, unit_ids: list[str], facts: list[ProcessedFact]) -> int:
    """Create causal links based on extracted causal relations."""
    links: list[link_utils.LinkRecord] = []

    for source_index, fact in enumerate(facts):
        for relation in fact.causal_relations:
            target_index = relation.target_fact_index
            if target_index < 0 or target_index >= len(unit_ids):
                continue

            source_id = unit_ids[source_index]
            target_id = unit_ids[target_index]
            if source_id == target_id:
                continue

            links.append((source_id, target_id, "causal", None, None, float(relation.strength)))

    return await link_utils.insert_links(conn, links)
