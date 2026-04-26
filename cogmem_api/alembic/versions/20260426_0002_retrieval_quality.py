"""Retrieval quality schema: search_vector, tags, partial HNSW, links indexes.

Revision ID: 20260426_0002
Revises: 20260330_0001
Create Date: 2026-04-26
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "20260426_0002"
down_revision = "20260330_0001"
branch_labels = None
depends_on = None


FACT_TYPES = ["world", "experience", "opinion", "habit", "intention", "action_effect"]


def upgrade() -> None:
    # Step 1: search_vector stored generated column + GIN index
    # to_tsvector includes both text and raw_snippet for better BM25 recall
    op.execute("""
        ALTER TABLE memory_units
        ADD COLUMN search_vector tsvector
        GENERATED ALWAYS AS (
            to_tsvector('english',
                coalesce(text, '') || ' ' || coalesce(raw_snippet, ''))
        ) STORED
    """)
    op.execute(
        "CREATE INDEX idx_memory_units_search_vector "
        "ON memory_units USING gin(search_vector)"
    )

    # Step 2: tags text[] column + partial GIN index
    op.add_column("memory_units", sa.Column("tags", sa.ARRAY(sa.Text()), nullable=True))
    op.execute(
        "CREATE INDEX idx_memory_units_tags "
        "ON memory_units USING gin(tags) "
        "WHERE tags IS NOT NULL"
    )

    # Step 3: 6 partial HNSW indexes per fact_type
    for ft in FACT_TYPES:
        op.execute(
            f"CREATE INDEX idx_mu_emb_{ft} "
            f"ON memory_units USING hnsw (embedding vector_cosine_ops) "
            f"WHERE fact_type = '{ft}'"
        )

    # Step 4: memory_links covering/composite indexes
    # Covering index for entity expansion: index-only scan, no heap fetch
    op.execute(
        "CREATE INDEX idx_memory_links_entity_covering "
        "ON memory_links (from_unit_id) "
        "INCLUDE (to_unit_id, entity_id) "
        "WHERE link_type = 'entity'"
    )
    # Composite index for incoming semantic links (both directions in LinkExpansion)
    op.execute(
        "CREATE INDEX idx_memory_links_to_type_weight "
        "ON memory_links (to_unit_id, link_type, weight DESC)"
    )


def downgrade() -> None:
    op.drop_index("idx_memory_links_to_type_weight", table_name="memory_links")
    op.drop_index("idx_memory_links_entity_covering", table_name="memory_links")
    for ft in FACT_TYPES:
        op.drop_index(f"idx_mu_emb_{ft}", table_name="memory_units")
    op.drop_index("idx_memory_units_tags", table_name="memory_units")
    op.drop_column("memory_units", "tags")
    op.drop_index("idx_memory_units_search_vector", table_name="memory_units")
    op.execute("ALTER TABLE memory_units DROP COLUMN search_vector")
