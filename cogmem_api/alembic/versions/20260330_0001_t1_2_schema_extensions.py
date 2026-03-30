"""T1.2 schema extensions for CogMem core networks and transition typing.

Revision ID: 20260330_0001
Revises: 
Create Date: 2026-03-30
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "20260330_0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("memory_units", sa.Column("raw_snippet", sa.Text(), nullable=True))
    op.add_column(
        "memory_units",
        sa.Column("network_type", sa.Text(), nullable=False, server_default="world"),
    )

    op.drop_constraint("memory_units_fact_type_check", "memory_units", type_="check")
    op.create_check_constraint(
        "memory_units_fact_type_check",
        "memory_units",
        "fact_type IN ('world', 'experience', 'opinion', 'observation', 'habit', 'intention', 'action_effect')",
    )

    op.create_check_constraint(
        "memory_units_network_type_check",
        "memory_units",
        "network_type IN ('world', 'experience', 'opinion', 'observation', 'habit', 'intention', 'action_effect')",
    )

    op.create_index("idx_memory_units_network_type", "memory_units", ["network_type"], unique=False)
    op.create_index("idx_memory_units_bank_network_type", "memory_units", ["bank_id", "network_type"], unique=False)
    op.create_index(
        "idx_memory_units_bank_network_date",
        "memory_units",
        ["bank_id", "network_type", "event_date"],
        unique=False,
        postgresql_ops={"event_date": "DESC"},
    )

    op.add_column("memory_links", sa.Column("transition_type", sa.Text(), nullable=True))

    op.drop_constraint("memory_links_link_type_check", "memory_links", type_="check")
    op.create_check_constraint(
        "memory_links_link_type_check",
        "memory_links",
        "link_type IN ('temporal', 'semantic', 'entity', 'causes', 'caused_by', 'enables', 'prevents', 'causal', 's_r_link', 'a_o_causal', 'transition')",
    )
    op.create_check_constraint(
        "memory_links_transition_type_values_check",
        "memory_links",
        "transition_type IS NULL OR transition_type IN ('fulfilled_by', 'abandoned', 'triggered', 'enabled_by', 'revised_to', 'contradicted_by')",
    )
    op.create_check_constraint(
        "memory_links_transition_type_usage_check",
        "memory_links",
        "(link_type = 'transition' AND transition_type IS NOT NULL) OR (link_type <> 'transition' AND transition_type IS NULL)",
    )
    op.create_index("idx_memory_links_transition_type", "memory_links", ["transition_type"], unique=False)


def downgrade() -> None:
    op.drop_index("idx_memory_links_transition_type", table_name="memory_links")
    op.drop_constraint("memory_links_transition_type_usage_check", "memory_links", type_="check")
    op.drop_constraint("memory_links_transition_type_values_check", "memory_links", type_="check")

    op.drop_constraint("memory_links_link_type_check", "memory_links", type_="check")
    op.create_check_constraint(
        "memory_links_link_type_check",
        "memory_links",
        "link_type IN ('temporal', 'semantic', 'entity', 'causes', 'caused_by', 'enables', 'prevents')",
    )

    op.drop_column("memory_links", "transition_type")

    op.drop_index("idx_memory_units_bank_network_date", table_name="memory_units")
    op.drop_index("idx_memory_units_bank_network_type", table_name="memory_units")
    op.drop_index("idx_memory_units_network_type", table_name="memory_units")

    op.drop_constraint("memory_units_network_type_check", "memory_units", type_="check")

    op.drop_constraint("memory_units_fact_type_check", "memory_units", type_="check")
    op.create_check_constraint(
        "memory_units_fact_type_check",
        "memory_units",
        "fact_type IN ('world', 'experience', 'opinion', 'observation')",
    )

    op.drop_column("memory_units", "network_type")
    op.drop_column("memory_units", "raw_snippet")
