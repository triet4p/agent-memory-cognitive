"""Link creation orchestration for retain pipeline."""

from __future__ import annotations

import os

from cogmem_api.engine.memory_engine import fq_table

from . import link_utils
from .types import ProcessedFact, TRANSITION_EDGE_RULES, clamp_relation_strength
from .entity_processing import _normalize_entity_name, _resolve_entity_id, _ENTITY_BLOCKLIST

_CROSS_BANK_SEMANTIC_THRESHOLD = float(os.environ.get("COGMEM_API_RETAIN_CROSS_BANK_SEMANTIC_THRESHOLD", "0.6"))
_CROSS_BANK_SEMANTIC_TOP_K = int(os.environ.get("COGMEM_API_RETAIN_CROSS_BANK_SEMANTIC_TOP_K", "10"))


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


# ---------------------------------------------------------------------------
# Phase B: Cross-session (inter-session) link creation
# ---------------------------------------------------------------------------


async def create_cross_bank_semantic_links_batch(
    conn,
    bank_id: str,
    unit_ids: list[str],
    embeddings: list[list[float]],
    threshold: float = _CROSS_BANK_SEMANTIC_THRESHOLD,
    top_k: int = _CROSS_BANK_SEMANTIC_TOP_K,
) -> int:
    """Phase B: for each new fact, find top-k semantically similar existing facts
    in the bank via pgvector ANN and create bidirectional semantic links."""
    if not unit_ids or not embeddings:
        return 0

    links: list[link_utils.LinkRecord] = []
    seen_pairs: set[tuple[str, str]] = set()

    for unit_id, embedding in zip(unit_ids, embeddings):
        if hasattr(conn, "get_ann_neighbors"):
            rows = await conn.get_ann_neighbors(bank_id, unit_id, embedding, threshold, top_k)
        else:
            rows = await conn.fetch(
                f"""
                SELECT id::text AS id, 1.0 - (embedding <=> $1::vector) AS similarity
                FROM {fq_table("memory_units")}
                WHERE bank_id = $2
                  AND id::text != ALL($3::text[])
                  AND 1.0 - (embedding <=> $1::vector) >= $4
                ORDER BY embedding <=> $1::vector
                LIMIT $5
                """,
                str(embedding),
                bank_id,
                unit_ids,
                threshold,
                top_k,
            )

        for row in rows:
            target_id = str(row["id"])
            sim = float(row["similarity"])
            pair = (unit_id, target_id)
            reverse = (target_id, unit_id)
            if pair not in seen_pairs:
                seen_pairs.add(pair)
                seen_pairs.add(reverse)
                links.append((unit_id, target_id, "semantic", None, None, sim))
                links.append((target_id, unit_id, "semantic", None, None, sim))

    return await link_utils.insert_links(conn, links)


async def create_cross_bank_structural_links_batch(
    conn,
    bank_id: str,
    unit_ids: list[str],
    facts: list[ProcessedFact],
) -> int:
    """Phase B: create cross-session temporal, s_r_link, a_o_causal, and transition
    links by querying existing bank facts via date windows and entity overlap."""
    if not unit_ids or not facts or len(unit_ids) != len(facts):
        return 0

    links: list[link_utils.LinkRecord] = []

    # --- Temporal: facts with absolute event_date, cross-session ---
    unit_dates = await link_utils.fetch_event_dates(conn, unit_ids)
    for unit_id, event_date in unit_dates.items():
        if hasattr(conn, "get_temporal_neighbors"):
            rows = await conn.get_temporal_neighbors(bank_id, unit_id, event_date, 86400)
        else:
            rows = await conn.fetch(
                f"""
                SELECT id::text AS id, event_date
                FROM {fq_table("memory_units")}
                WHERE bank_id = $1
                  AND id::text != ALL($2::text[])
                  AND event_date IS NOT NULL
                  AND ABS(EXTRACT(EPOCH FROM (event_date - $3))) <= $4
                """,
                bank_id,
                unit_ids,
                event_date,
                86400,
            )

        for row in rows:
            target_id = str(row["id"])
            target_date = row["event_date"]
            if target_date is None:
                continue
            delta_s = abs((event_date - target_date).total_seconds())
            weight = max(0.3, 1.0 - delta_s / 86400.0)
            links.append((unit_id, target_id, "temporal", None, None, weight))
            links.append((target_id, unit_id, "temporal", None, None, weight))

    # --- Entity-based cross-session: s_r_link, a_o_causal, transition (heuristic) ---
    for unit_id, fact in zip(unit_ids, facts):
        fact_type = fact.fact_type
        is_habit = fact_type == "habit"
        is_action_effect = fact_type == "action_effect"
        is_experience = fact_type == "experience"

        if not (is_habit or is_action_effect or is_experience):
            continue

        non_blocked_entity_ids = []
        for entity_name in fact.entities:
            normalized = _normalize_entity_name(entity_name)
            if normalized and normalized not in _ENTITY_BLOCKLIST:
                non_blocked_entity_ids.append(_resolve_entity_id(bank_id, entity_name))

        if not non_blocked_entity_ids:
            continue

        if is_habit:
            # s_r_link: habit → non-habit facts sharing entities cross-session
            if hasattr(conn, "get_entity_overlapping_facts"):
                rows = await conn.get_entity_overlapping_facts(bank_id, unit_ids, non_blocked_entity_ids, exclude_fact_types=["habit"])
            else:
                rows = await conn.fetch(
                    f"""
                    SELECT DISTINCT mu.id::text AS id
                    FROM {fq_table("unit_entities")} ue
                    JOIN {fq_table("memory_units")} mu ON mu.id = ue.unit_id
                    WHERE ue.entity_id = ANY($1::uuid[])
                      AND mu.bank_id = $2
                      AND mu.fact_type != 'habit'
                      AND mu.id::text != ALL($3::text[])
                    """,
                    non_blocked_entity_ids,
                    bank_id,
                    unit_ids,
                )
            for row in rows:
                target_id = str(row["id"])
                links.append((unit_id, target_id, "s_r_link", None, None, 0.65))

        elif is_action_effect:
            # a_o_causal fallback: action_effect → non-action_effect facts sharing entities
            if hasattr(conn, "get_entity_overlapping_facts"):
                rows = await conn.get_entity_overlapping_facts(bank_id, unit_ids, non_blocked_entity_ids, exclude_fact_types=["action_effect"])
            else:
                rows = await conn.fetch(
                    f"""
                    SELECT DISTINCT mu.id::text AS id
                    FROM {fq_table("unit_entities")} ue
                    JOIN {fq_table("memory_units")} mu ON mu.id = ue.unit_id
                    WHERE ue.entity_id = ANY($1::uuid[])
                      AND mu.bank_id = $2
                      AND mu.fact_type != 'action_effect'
                      AND mu.id::text != ALL($3::text[])
                    """,
                    non_blocked_entity_ids,
                    bank_id,
                    unit_ids,
                )
            for row in rows:
                target_id = str(row["id"])
                links.append((unit_id, target_id, "a_o_causal", None, None, 0.65))

        elif is_experience:
            # transition heuristic: experience → existing planning intentions sharing entities
            if hasattr(conn, "get_planning_intentions_by_entity"):
                rows = await conn.get_planning_intentions_by_entity(bank_id, unit_ids, non_blocked_entity_ids)
            else:
                rows = await conn.fetch(
                    f"""
                    SELECT DISTINCT mu.id::text AS id
                    FROM {fq_table("unit_entities")} ue
                    JOIN {fq_table("memory_units")} mu ON mu.id = ue.unit_id
                    WHERE ue.entity_id = ANY($1::uuid[])
                      AND mu.bank_id = $2
                      AND mu.fact_type = 'intention'
                      AND mu.metadata->>'intention_status' = 'planning'
                      AND mu.id::text != ALL($3::text[])
                    """,
                    non_blocked_entity_ids,
                    bank_id,
                    unit_ids,
                )
            for row in rows:
                intention_id = str(row["id"])
                # intention fulfilled_by experience: intention → experience
                links.append((intention_id, unit_id, "transition", "fulfilled_by", None, 0.7))

    return await link_utils.insert_links(conn, links)
