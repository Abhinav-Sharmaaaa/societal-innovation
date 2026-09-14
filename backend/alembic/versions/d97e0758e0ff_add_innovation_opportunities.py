"""add innovation opportunities

Revision ID: d97e0758e0ff
Revises: e8b3c4be637f
Create Date: 2026-09-13
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql


revision: str = "d97e0758e0ff"

down_revision: Union[str, Sequence[str], None] = (
    "e8b3c4be637f"
)

branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # --------------------------------------------------------
    # Create innovation opportunity status enum
    # --------------------------------------------------------

    opportunity_status_enum = postgresql.ENUM(
        "DRAFT",
        "APPROVED",
        "RFP_CREATED",
        "ACTIVE",
        "CLOSED",
        "CANCELLED",
        name="innovationopportunitystatus",
    )

    opportunity_status_enum.create(
        op.get_bind(),
        checkfirst=True,
    )

    opportunity_status_column_enum = postgresql.ENUM(
        "DRAFT",
        "APPROVED",
        "RFP_CREATED",
        "ACTIVE",
        "CLOSED",
        "CANCELLED",
        name="innovationopportunitystatus",
        create_type=False,
    )

    # --------------------------------------------------------
    # Create innovation opportunities table
    # --------------------------------------------------------

    op.create_table(
        "innovation_opportunities",
        sa.Column(
            "id",
            sa.Integer(),
            autoincrement=True,
            nullable=False,
        ),
        sa.Column(
            "challenge_id",
            sa.Integer(),
            nullable=False,
        ),
        sa.Column(
            "sponsoring_organization_id",
            sa.Integer(),
            nullable=False,
        ),
        sa.Column(
            "created_by",
            sa.Integer(),
            nullable=False,
        ),
        sa.Column(
            "approved_by",
            sa.Integer(),
            nullable=True,
        ),
        sa.Column(
            "title",
            sa.String(length=255),
            nullable=False,
        ),
        sa.Column(
            "problem_statement",
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
            opportunity_status_column_enum,
            nullable=False,
        ),
        sa.Column(
            "is_active",
            sa.Boolean(),
            nullable=False,
        ),
        sa.Column(
            "approved_at",
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
            ["challenge_id"],
            ["challenges.id"],
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["sponsoring_organization_id"],
            ["organizations.id"],
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["created_by"],
            ["users.id"],
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["approved_by"],
            ["users.id"],
            ondelete="SET NULL",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "challenge_id",
            name="uq_innovation_opportunity_challenge",
        ),
    )

    # --------------------------------------------------------
    # Indexes
    # --------------------------------------------------------

    op.create_index(
        "ix_innovation_opportunities_challenge_id",
        "innovation_opportunities",
        ["challenge_id"],
        unique=True,
    )

    op.create_index(
        "ix_innovation_opportunities_sponsoring_organization_id",
        "innovation_opportunities",
        ["sponsoring_organization_id"],
        unique=False,
    )

    op.create_index(
        "ix_innovation_opportunities_created_by",
        "innovation_opportunities",
        ["created_by"],
        unique=False,
    )

    op.create_index(
        "ix_innovation_opportunities_approved_by",
        "innovation_opportunities",
        ["approved_by"],
        unique=False,
    )

    op.create_index(
        "ix_innovation_opportunities_status",
        "innovation_opportunities",
        ["status"],
        unique=False,
    )


def downgrade() -> None:
    # --------------------------------------------------------
    # Drop indexes
    # --------------------------------------------------------

    op.drop_index(
        "ix_innovation_opportunities_status",
        table_name="innovation_opportunities",
    )

    op.drop_index(
        "ix_innovation_opportunities_approved_by",
        table_name="innovation_opportunities",
    )

    op.drop_index(
        "ix_innovation_opportunities_created_by",
        table_name="innovation_opportunities",
    )

    op.drop_index(
        "ix_innovation_opportunities_sponsoring_organization_id",
        table_name="innovation_opportunities",
    )

    op.drop_index(
        "ix_innovation_opportunities_challenge_id",
        table_name="innovation_opportunities",
    )

    # --------------------------------------------------------
    # Drop table
    # --------------------------------------------------------

    op.drop_table(
        "innovation_opportunities",
    )

    # --------------------------------------------------------
    # Drop enum
    # --------------------------------------------------------

    opportunity_status_enum = postgresql.ENUM(
        "DRAFT",
        "APPROVED",
        "RFP_CREATED",
        "ACTIVE",
        "CLOSED",
        "CANCELLED",
        name="innovationopportunitystatus",
    )

    opportunity_status_enum.drop(
        op.get_bind(),
        checkfirst=True,
    )