"""add rfps

Revision ID: ed66d4fb8ad1
Revises: d97e0758e0ff
Create Date: 2026-09-13
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql


revision: str = "ed66d4fb8ad1"

down_revision: Union[str, Sequence[str], None] = (
    "d97e0758e0ff"
)

branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # --------------------------------------------------------
    # Create PostgreSQL enum
    # --------------------------------------------------------

    rfp_status_enum = postgresql.ENUM(
        "DRAFT",
        "PUBLISHED",
        "CLOSED",
        "CANCELLED",
        name="rfpstatus",
    )

    rfp_status_enum.create(
        op.get_bind(),
        checkfirst=True,
    )

    rfp_status_column_enum = postgresql.ENUM(
        "DRAFT",
        "PUBLISHED",
        "CLOSED",
        "CANCELLED",
        name="rfpstatus",
        create_type=False,
    )

    # --------------------------------------------------------
    # Create RFP table
    # --------------------------------------------------------

    op.create_table(
        "rfps",
        sa.Column(
            "id",
            sa.Integer(),
            autoincrement=True,
            nullable=False,
        ),
        sa.Column(
            "innovation_opportunity_id",
            sa.Integer(),
            nullable=False,
        ),
        sa.Column(
            "created_by",
            sa.Integer(),
            nullable=False,
        ),
        sa.Column(
            "title",
            sa.String(length=255),
            nullable=False,
        ),
        sa.Column(
            "description",
            sa.Text(),
            nullable=False,
        ),
        sa.Column(
            "objectives",
            sa.Text(),
            nullable=True,
        ),
        sa.Column(
            "technical_requirements",
            sa.Text(),
            nullable=True,
        ),
        sa.Column(
            "expected_outcomes",
            sa.Text(),
            nullable=True,
        ),
        sa.Column(
            "estimated_budget",
            sa.Float(),
            nullable=True,
        ),
        sa.Column(
            "expected_duration_days",
            sa.Integer(),
            nullable=True,
        ),
        sa.Column(
            "proposal_deadline",
            sa.DateTime(timezone=True),
            nullable=True,
        ),
        sa.Column(
            "status",
            rfp_status_column_enum,
            nullable=False,
        ),
        sa.Column(
            "is_active",
            sa.Boolean(),
            nullable=False,
        ),
        sa.Column(
            "published_at",
            sa.DateTime(timezone=True),
            nullable=True,
        ),
        sa.Column(
            "closed_at",
            sa.DateTime(timezone=True),
            nullable=True,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.ForeignKeyConstraint(
            ["innovation_opportunity_id"],
            ["innovation_opportunities.id"],
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["created_by"],
            ["users.id"],
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "innovation_opportunity_id",
            name="uq_rfps_innovation_opportunity",
        ),
    )

    # --------------------------------------------------------
    # Indexes
    # --------------------------------------------------------

    op.create_index(
        "ix_rfps_innovation_opportunity_id",
        "rfps",
        ["innovation_opportunity_id"],
        unique=True,
    )

    op.create_index(
        "ix_rfps_created_by",
        "rfps",
        ["created_by"],
        unique=False,
    )

    op.create_index(
        "ix_rfps_status",
        "rfps",
        ["status"],
        unique=False,
    )


def downgrade() -> None:
    # --------------------------------------------------------
    # Drop indexes
    # --------------------------------------------------------

    op.drop_index(
        "ix_rfps_status",
        table_name="rfps",
    )

    op.drop_index(
        "ix_rfps_created_by",
        table_name="rfps",
    )

    op.drop_index(
        "ix_rfps_innovation_opportunity_id",
        table_name="rfps",
    )

    # --------------------------------------------------------
    # Drop table
    # --------------------------------------------------------

    op.drop_table("rfps")

    # --------------------------------------------------------
    # Drop enum
    # --------------------------------------------------------

    rfp_status_enum = postgresql.ENUM(
        "DRAFT",
        "PUBLISHED",
        "CLOSED",
        "CANCELLED",
        name="rfpstatus",
    )

    rfp_status_enum.drop(
        op.get_bind(),
        checkfirst=True,
    )