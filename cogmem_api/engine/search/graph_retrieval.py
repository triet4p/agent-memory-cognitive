"""
Graph retrieval strategies for memory recall.

This module provides an abstraction for graph-based memory retrieval,
allowing different algorithms (BFS spreading activation, PPR, etc.) to be
swapped without changing the rest of the recall pipeline.
"""

import logging
from collections import defaultdict
from abc import ABC, abstractmethod

from cogmem_api.engine.db_utils import acquire_with_retry
from cogmem_api.engine.memory_engine import fq_table
from .tags import TagGroup, TagsMatch, filter_results_by_tag_groups, filter_results_by_tags
from .types import MPFPTimings, RetrievalResult

logger = logging.getLogger(__name__)


class GraphRetriever(ABC):
    """
    Abstract base class for graph-based memory retrieval.

    Implementations traverse the memory graph (entity links, temporal links,
    causal links) to find relevant facts that might not be found by
    semantic or keyword search alone.
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """Return identifier for this retrieval strategy (e.g., 'bfs', 'mpfp')."""
        pass

    @abstractmethod
    async def retrieve(
        self,
        pool,
        query_embedding_str: str,
        bank_id: str,
        fact_type: str,
        budget: int,
        query_text: str | None = None,
        semantic_seeds: list[RetrievalResult] | None = None,
        temporal_seeds: list[RetrievalResult] | None = None,
        adjacency=None,  # TypedAdjacency, optional pre-loaded graph
        tags: list[str] | None = None,  # Visibility scope tags for filtering
        tags_match: TagsMatch = "any",  # How to match tags: 'any' (OR) or 'all' (AND)
        tag_groups: list[TagGroup] | None = None,  # Compound boolean tag filter groups
    ) -> tuple[list[RetrievalResult], MPFPTimings | None]:
        """
        Retrieve relevant facts via graph traversal.

        Args:
            pool: Database connection pool
            query_embedding_str: Query embedding as string (for finding entry points)
            bank_id: Memory bank identifier
            fact_type: Fact type to filter (CogMem fact networks)
            budget: Maximum number of nodes to explore/return
            query_text: Original query text (optional, for some strategies)
            semantic_seeds: Pre-computed semantic entry points (from semantic retrieval)
            temporal_seeds: Pre-computed temporal entry points (from temporal retrieval)
            adjacency: Pre-loaded typed adjacency graph (optional, for MPFP)
            tags: Optional list of tags for visibility filtering (OR matching)

        Returns:
            Tuple of (List of RetrievalResult with activation scores, optional timing info)
        """
        pass


class BFSGraphRetriever(GraphRetriever):
    """
    Graph retrieval using BFS-style spreading activation.

    Starting from semantic entry points, spreads activation through
    the memory graph (entity, temporal, causal links) using breadth-first
    traversal with decaying activation.

    This is the original Hindsight graph retrieval algorithm.
    """

    def __init__(
        self,
        entry_point_limit: int = 5,
        entry_point_threshold: float = 0.5,
        activation_decay: float = 0.8,
        min_activation: float = 0.1,
        batch_size: int = 20,
        refractory_steps: int = 1,
        firing_quota: int = 2,
        activation_saturation: float = 2.0,
    ):
        """
        Initialize BFS graph retriever.

        Args:
            entry_point_limit: Maximum number of entry points to start from
            entry_point_threshold: Minimum semantic similarity for entry points
            activation_decay: Decay factor per hop (activation *= decay)
            min_activation: Minimum activation to continue spreading
            batch_size: Number of nodes to process per batch (for neighbor fetching)
            refractory_steps: Minimum steps before a node can fire again
            firing_quota: Maximum number of times a node can fire
            activation_saturation: Upper bound (A_max) for node activation
        """
        self.entry_point_limit = entry_point_limit
        self.entry_point_threshold = entry_point_threshold
        self.activation_decay = activation_decay
        self.min_activation = min_activation
        self.batch_size = batch_size
        self.refractory_steps = max(0, refractory_steps)
        self.firing_quota = max(1, firing_quota)
        self.activation_saturation = max(min_activation, activation_saturation)

    @property
    def name(self) -> str:
        return "bfs"

    async def retrieve(
        self,
        pool,
        query_embedding_str: str,
        bank_id: str,
        fact_type: str,
        budget: int,
        query_text: str | None = None,
        semantic_seeds: list[RetrievalResult] | None = None,
        temporal_seeds: list[RetrievalResult] | None = None,
        adjacency=None,  # Not used by BFS
        tags: list[str] | None = None,
        tags_match: TagsMatch = "any",
        tag_groups: list[TagGroup] | None = None,
    ) -> tuple[list[RetrievalResult], MPFPTimings | None]:
        """
        Retrieve facts using BFS spreading activation.

        Algorithm:
        1. Find entry points (top semantic matches above threshold)
        2. BFS traversal: visit neighbors, propagate decaying activation
        3. Boost causal links (`link_type='causal'`)
        4. Return visited nodes up to budget

        Note: BFS finds its own entry points via embedding search.
        The semantic_seeds, temporal_seeds, and adjacency parameters are accepted
        for interface compatibility but not used.
        """
        async with acquire_with_retry(pool) as conn:
            results = await self._retrieve_with_conn(
                conn,
                query_embedding_str,
                bank_id,
                fact_type,
                budget,
                tags=tags,
                tags_match=tags_match,
                tag_groups=tag_groups,
            )
            return results, None

    async def _retrieve_with_conn(
        self,
        conn,
        query_embedding_str: str,
        bank_id: str,
        fact_type: str,
        budget: int,
        tags: list[str] | None = None,
        tags_match: TagsMatch = "any",
        tag_groups: list[TagGroup] | None = None,
    ) -> list[RetrievalResult]:
        """Internal implementation with connection."""
        from .tags import build_tag_groups_where_clause, build_tags_where_clause_simple

        tags_clause = build_tags_where_clause_simple(tags, 6, match=tags_match)
        tag_groups_param_start = 6 + (1 if tags else 0)
        groups_clause, groups_params, _ = build_tag_groups_where_clause(tag_groups, tag_groups_param_start)
        params = [query_embedding_str, bank_id, fact_type, self.entry_point_threshold, self.entry_point_limit]
        if tags:
            params.append(tags)
        params.extend(groups_params)

        # Step 1: Find entry points
        entry_points = await conn.fetch(
            f"""
            SELECT id, text, context, event_date, occurred_start, occurred_end,
                   mentioned_at, fact_type, document_id, chunk_id, tags,
                   1 - (embedding <=> $1::vector) AS similarity
            FROM {fq_table("memory_units")}
            WHERE bank_id = $2
              AND embedding IS NOT NULL
              AND fact_type = $3
              AND (1 - (embedding <=> $1::vector)) >= $4
              {tags_clause}
              {groups_clause}
            ORDER BY embedding <=> $1::vector
            LIMIT $5
            """,
            *params,
        )

        if not entry_points:
            logger.debug(
                f"[BFS] No entry points found for fact_type={fact_type} (tags={tags}, tags_match={tags_match})"
            )
            return []

        logger.debug(
            f"[BFS] Found {len(entry_points)} entry points for fact_type={fact_type} "
            f"(tags={tags}, tags_match={tags_match})"
        )

        # Step 2: SUM spreading activation with cycle guards.
        # - Refractory: node cannot fire in consecutive steps.
        # - Firing quota: each node has a bounded number of firings.
        # - Saturation: node activation is clipped to A_max.
        results_by_id: dict[str, RetrievalResult] = {}
        node_payload: dict[str, RetrievalResult] = {}
        frontier_activation: dict[str, float] = defaultdict(float)
        firing_count: dict[str, int] = defaultdict(int)
        last_fired_step: dict[str, int] = {}

        for row in entry_points:
            seed = RetrievalResult.from_db_row(dict(row))
            node_payload[seed.id] = seed
            frontier_activation[seed.id] = min(
                self.activation_saturation,
                frontier_activation[seed.id] + max(float(row["similarity"]), 0.0),
            )

        step = 0
        budget_remaining = budget

        while frontier_activation and budget_remaining > 0:
            step += 1

            fireable: list[tuple[str, float]] = []
            for node_id, raw_activation in frontier_activation.items():
                activation = min(self.activation_saturation, raw_activation)
                if activation <= self.min_activation:
                    continue
                if firing_count[node_id] >= self.firing_quota:
                    continue

                previous_step = last_fired_step.get(node_id)
                if previous_step is not None and (step - previous_step) <= self.refractory_steps:
                    continue

                fireable.append((node_id, activation))

            if not fireable:
                break

            fireable.sort(key=lambda item: item[1], reverse=True)
            selected = fireable[: self.batch_size]
            batch_nodes = [node_id for node_id, _ in selected]
            batch_activations = {node_id: activation for node_id, activation in selected}

            for node_id, activation in selected:
                firing_count[node_id] += 1
                last_fired_step[node_id] = step
                frontier_activation.pop(node_id, None)

                node = node_payload.get(node_id)
                if node is None:
                    continue

                if node_id not in results_by_id:
                    node.activation = activation
                    results_by_id[node_id] = node
                    budget_remaining -= 1
                else:
                    prior = results_by_id[node_id].activation or 0.0
                    results_by_id[node_id].activation = min(self.activation_saturation, prior + activation)

            # Batch fetch neighbors
            if batch_nodes and budget_remaining > 0:
                max_neighbors = len(batch_nodes) * 20
                neighbors = await conn.fetch(
                    f"""
                    SELECT mu.id, mu.text, mu.context, mu.occurred_start, mu.occurred_end,
                           mu.mentioned_at, mu.fact_type,
                           mu.document_id, mu.chunk_id, mu.tags,
                           ml.weight, ml.link_type, ml.from_unit_id
                    FROM {fq_table("memory_links")} ml
                    JOIN {fq_table("memory_units")} mu ON ml.to_unit_id = mu.id
                    WHERE ml.from_unit_id = ANY($1::uuid[])
                      AND ml.weight >= $2
                      AND mu.fact_type = $3
                    ORDER BY ml.weight DESC
                    LIMIT $4
                    """,
                    batch_nodes,
                    self.min_activation,
                    fact_type,
                    max_neighbors,
                )

                for n in neighbors:
                    neighbor_id = str(n["id"])
                    parent_id = str(n["from_unit_id"])
                    parent_activation = batch_activations.get(parent_id, 0.5)

                    # Boost causal links
                    link_type = n["link_type"]
                    base_weight = n["weight"]

                    if link_type == "causal":
                        causal_boost = 2.0
                    else:
                        causal_boost = 1.0

                    effective_weight = base_weight * causal_boost
                    propagated = parent_activation * effective_weight * self.activation_decay

                    if propagated <= self.min_activation:
                        continue

                    node_payload.setdefault(neighbor_id, RetrievalResult.from_db_row(dict(n)))
                    frontier_activation[neighbor_id] = min(
                        self.activation_saturation,
                        frontier_activation.get(neighbor_id, 0.0) + propagated,
                    )

        results = sorted(results_by_id.values(), key=lambda r: r.activation or 0.0, reverse=True)

        # Apply tags filtering (BFS may traverse into memories that don't match tags criteria)
        if tags:
            results = filter_results_by_tags(results, tags, match=tags_match)

        # Apply compound tag group filtering (post-traversal)
        if tag_groups:
            results = filter_results_by_tag_groups(results, tag_groups)

        return results
