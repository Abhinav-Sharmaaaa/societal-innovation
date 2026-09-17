"""add industry collaboration proposals

Revision ID: 3b70bab58548
Revises: 2320875ff907
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql


revision: str = "3b70bab58548"

down_revision: Union[str, Sequence[str], None] = "2320875ff907"

branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    industry_collaboration_status_enum = postgresql.ENUM(
        "DRAFT",
        "SUBMITTED",
        "UNDER_REVIEW",
        "MODIFICATION_REQUESTED",
        "ACCEPTED",
        "REJECTED",
        "WITHDRAWN",
        name="industrycollaborationstatus",
    )

    industry_collaboration_status_enum.create(
        op.get_bind(),
        checkfirst=True,
    )

    industry_collaboration_status_column_enum = postgresql.ENUM(
        "DRAFT",
        "SUBMITTED",
        "UNDER_REVIEW",
        "MODIFICATION_REQUESTED",
        "ACCEPTED",
        "REJECTED",
        "WITHDRAWN",
        name="industrycollaborationstatus",
        create_type=False,
    )

    op.create_table(
        "industry_collaboration_proposals",

        sa.Column(
            "id",
            sa.Integer(),
            autoincrement=True,
            nullable=False,
        ),

        sa.Column(
            "university_proposal_id",
            sa.Integer(),
            nullable=False,
        ),

        sa.Column(
            "industry_id",
            sa.Integer(),
            nullable=False,
        ),

        sa.Column(
            "submitted_by",
            sa.Integer(),
            nullable=False,
        ),

        sa.Column(
            "title",
            sa.Text(),
            nullable=False,
        ),

        sa.Column(
            "collaboration_description",
            sa.Text(),
            nullable=False,
        ),

        sa.Column(
            "funding_amount",
            sa.Float(),
            nullable=True,
        ),

        sa.Column(
            "technical_mentorship",
            sa.Text(),
            nullable=True,
        ),

        sa.Column(
            "industry_experts",
            sa.Text(),
            nullable=True,
        ),

        sa.Column(
            "infrastructure_resources",
            sa.Text(),
            nullable=True,
        ),

        sa.Column(
            "technology_support",
            sa.Text(),
            nullable=True,
        ),

        sa.Column(
            "internship_support",
            sa.Text(),
            nullable=True,
        ),

        sa.Column(
            "pilot_deployment_support",
            sa.Text(),
            nullable=True,
        ),

        sa.Column(
            "commercialization_support",
            sa.Text(),
            nullable=True,
        ),

        sa.Column(
            "proposed_duration_days",
            sa.Integer(),
            nullable=True,
        ),

        sa.Column(
            "additional_terms",
            sa.Text(),
            nullable=True,
        ),

        sa.Column(
            "status",
            industry_collaboration_status_column_enum,
            nullable=False,
        ),

        sa.Column(
            "submitted_at",
            sa.DateTime(timezone=True),
            nullable=True,
        ),

        sa.Column(
            "reviewed_at",
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
            ["university_proposal_id"],
            ["university_proposals.id"],
            ondelete="CASCADE",
        ),

        sa.ForeignKeyConstraint(
            ["industry_id"],
            ["organizations.id"],
            ondelete="RESTRICT",
        ),

        sa.ForeignKeyConstraint(
            ["submitted_by"],
            ["users.id"],
            ondelete="RESTRICT",
        ),

        sa.PrimaryKeyConstraint("id"),

        sa.UniqueConstraint(
            "university_proposal_id",
            "industry_id",
            name="uq_industry_collaboration_proposal",
        ),
    )

    op.create_index(
        "ix_industry_collaboration_proposals_university_proposal_id",
        "industry_collaboration_proposals",
        ["university_proposal_id"],
        unique=False,
    )

    op.create_index(
        "ix_industry_collaboration_proposals_industry_id",
        "industry_collaboration_proposals",
        ["industry_id"],
        unique=False,
    )

    op.create_index(
        "ix_industry_collaboration_proposals_submitted_by",
        "industry_collaboration_proposals",
        ["submitted_by"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(
        "ix_industry_collaboration_proposals_submitted_by",
        table_name="industry_collaboration_proposals",
    )

    op.drop_index(
        "ix_industry_collaboration_proposals_industry_id",
        table_name="industry_collaboration_proposals",
    )

    op.drop_index(
        "ix_industry_collaboration_proposals_university_proposal_id",
        table_name="industry_collaboration_proposals",
    )

    op.drop_table(
        "industry_collaboration_proposals",
    )

    industry_collaboration_status_enum = postgresql.ENUM(
        "DRAFT",
        "SUBMITTED",
        "UNDER_REVIEW",
        "MODIFICATION_REQUESTED",
        "ACCEPTED",
        "REJECTED",
        "WITHDRAWN",
        name="industrycollaborationstatus",
    )

    industry_collaboration_status_enum.drop(
        op.get_bind(),
        checkfirst=True,
    )