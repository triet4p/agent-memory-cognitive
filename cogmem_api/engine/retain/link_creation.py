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


async def create_habit_sr_links_batch(conn, unit_ids: list[str], facts: list[ProcessedFact]) -> int:
    """Create S-R links from habit nodes to facts that share at least one entity."""
    if not unit_ids or not facts or len(unit_ids) != len(facts):
        return 0

    links: list[link_utils.LinkRecord] = []

    habit_indices = [idx for idx, fact in enumerate(facts) if fact.fact_type == "habit"]
    non_habit_indices = [idx for idx, fact in enumerate(facts) if fact.fact_type != "habit"]

    for habit_index in habit_indices:
        habit_entities = {entity.strip().lower() for entity in facts[habit_index].entities if entity.strip()}
        if not habit_entities:
            continue

        for target_index in non_habit_indices:
            target_entities = {entity.strip().lower() for entity in facts[target_index].entities if entity.strip()}
            if not target_entities:
                continue

            overlap = habit_entities.intersection(target_entities)
            if not overlap:
                continue

            # Stronger overlap means stronger behavioral reinforcement signal.
            overlap_ratio = len(overlap) / max(1, len(habit_entities))
            weight = max(0.5, min(1.0, 0.6 + 0.4 * overlap_ratio))

            links.append((unit_ids[habit_index], unit_ids[target_index], "s_r_link", None, None, weight))

    return await link_utils.insert_links(conn, links)
