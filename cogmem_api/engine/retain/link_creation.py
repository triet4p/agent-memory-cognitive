"""Link creation orchestration for retain pipeline."""

from __future__ import annotations

from . import link_utils
from .types import ProcessedFact, TRANSITION_EDGE_RULES, clamp_relation_strength


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
            relation_type = str(relation.relation_type or "caused_by").strip().lower()
            if relation_type != "caused_by":
                continue

            target_index = relation.target_fact_index
            if target_index < 0 or target_index >= len(unit_ids):
                continue

            # caused_by intent points to an earlier supporting fact
            if target_index >= source_index:
                continue

            source_id = unit_ids[source_index]
            target_id = unit_ids[target_index]
            if source_id == target_id:
                continue

            links.append((source_id, target_id, "causal", None, None, clamp_relation_strength(relation.strength)))

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


async def create_transition_links_batch(conn, unit_ids: list[str], facts: list[ProcessedFact]) -> int:
    """Create typed transition edges for intention lifecycle handling."""
    if not unit_ids or not facts or len(unit_ids) != len(facts):
        return 0

    links: list[link_utils.LinkRecord] = []

    for source_index, fact in enumerate(facts):
        source_id = unit_ids[source_index]
        source_fact_type = fact.fact_type

        for relation in fact.transition_relations:
            transition_type = relation.transition_type.strip().lower()

            # Abandoned is a status-only lifecycle update (no edge target by design).
            if transition_type == "abandoned":
                continue

            expected_rule = TRANSITION_EDGE_RULES.get(transition_type)
            if expected_rule is None:
                continue

            target_index = relation.target_fact_index
            if target_index is None or target_index < 0 or target_index >= len(unit_ids):
                continue

            target_id = unit_ids[target_index]
            if source_id == target_id:
                continue

            target_fact_type = facts[target_index].fact_type
            expected_source, expected_target = expected_rule
            if source_fact_type != expected_source or target_fact_type != expected_target:
                continue

            links.append(
                (
                    source_id,
                    target_id,
                    "transition",
                    transition_type,
                    None,
                    clamp_relation_strength(relation.strength),
                )
            )

    return await link_utils.insert_links(conn, links)


async def create_action_effect_links_batch(conn, unit_ids: list[str], facts: list[ProcessedFact]) -> int:
    """Create A-O causal links from action_effect nodes."""
    if not unit_ids or not facts or len(unit_ids) != len(facts):
        return 0

    links: list[link_utils.LinkRecord] = []

    for source_index, fact in enumerate(facts):
        if fact.fact_type != "action_effect":
            continue

        source_id = unit_ids[source_index]

        # Primary path: explicit target relations declared by extraction.
        if fact.action_effect_relations:
            for relation in fact.action_effect_relations:
                relation_type = str(relation.relation_type or "a_o_causal").strip().lower()
                if relation_type != "a_o_causal":
                    continue

                target_index = relation.target_fact_index
                if target_index < 0 or target_index >= len(unit_ids):
                    continue

                target_id = unit_ids[target_index]
                if source_id == target_id:
                    continue

                links.append((source_id, target_id, "a_o_causal", None, None, clamp_relation_strength(relation.strength)))
            continue

        # Fallback path: infer target by shared entities with non-action_effect facts.
        source_entities = {entity.strip().lower() for entity in fact.entities if entity.strip()}
        if not source_entities:
            continue

        for target_index, target_fact in enumerate(facts):
            if target_index == source_index or target_fact.fact_type == "action_effect":
                continue

            target_entities = {entity.strip().lower() for entity in target_fact.entities if entity.strip()}
            overlap = source_entities.intersection(target_entities)
            if not overlap:
                continue

            overlap_ratio = len(overlap) / max(1, len(source_entities))
            weight = max(0.5, min(1.0, 0.65 + 0.35 * overlap_ratio))
            links.append((source_id, unit_ids[target_index], "a_o_causal", None, None, weight))

    return await link_utils.insert_links(conn, links)
