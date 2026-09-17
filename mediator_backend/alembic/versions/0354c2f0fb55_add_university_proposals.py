"""add university proposals

Revision ID: 0354c2f0fb55
Revises: 3990217789ca
Create Date: 2026-09-13
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql


revision: str = "0354c2f0fb55"

down_revision: Union[str, Sequence[str], None] = (
    "3990217789ca"
)

branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # --------------------------------------------------------
    # Create PostgreSQL enum
    # --------------------------------------------------------

    proposal_status_enum = postgresql.ENUM(
        "DRAFT",
        "SUBMITTED",
        "UNDER_EVALUATION",
        "SHORTLISTED",
        "REJECTED",
        "WITHDRAWN",
        name="universityproposalstatus",
    )

    proposal_status_enum.create(
        op.get_bind(),
        checkfirst=True,
    )

    proposal_status_column_enum = postgresql.ENUM(
        "DRAFT",
        "SUBMITTED",
        "UNDER_EVALUATION",
        "SHORTLISTED",
        "REJECTED",
        "WITHDRAWN",
        name="universityproposalstatus",
        create_type=False,
    )

    # --------------------------------------------------------
    # Create university proposals table
    # --------------------------------------------------------

    op.create_table(
        "university_proposals",
        sa.Column(
            "id",
            sa.Integer(),
            autoincrement=True,
            nullable=False,
        ),
        sa.Column(
            "rfp_id",
            sa.Integer(),
            nullable=False,
        ),
        sa.Column(
            "invitation_id",
            sa.Integer(),
            nullable=False,
        ),
        sa.Column(
            "university_id",
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
            sa.String(length=255),
            nullable=False,
        ),
        sa.Column(
            "solution",
            sa.Text(),
            nullable=False,
        ),
        sa.Column(
            "technical_approach",
            sa.Text(),
            nullable=False,
        ),
        sa.Column(
            "research_methodology",
            sa.Text(),
            nullable=True,
        ),
        sa.Column(
            "required_resources",
            sa.Text(),
            nullable=True,
        ),
        sa.Column(
            "estimated_cost",
            sa.Float(),
            nullable=True,
        ),
        sa.Column(
            "expected_timeline_days",
            sa.Integer(),
            nullable=True,
        ),
        sa.Column(
            "faculty_team",
            sa.Text(),
            nullable=True,
        ),
        sa.Column(
            "expected_outcomes",
            sa.Text(),
            nullable=True,
        ),
        sa.Column(
            "technology_requirements",
            sa.Text(),
            nullable=True,
        ),
        sa.Column(
            "status",
            proposal_status_column_enum,
            nullable=False,
        ),
        sa.Column(
            "submitted_at",
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
            ["rfp_id"],
            ["rfps.id"],
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["invitation_id"],
            ["rfp_invitations.id"],
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["university_id"],
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
            "invitation_id",
            name="uq_university_proposal_invitation",
        ),
    )

    # --------------------------------------------------------
    # Indexes
    # --------------------------------------------------------

    op.create_index(
        "ix_university_proposals_rfp_id",
        "university_proposals",
        ["rfp_id"],
        unique=False,
    )

    op.create_index(
        "ix_university_proposals_invitation_id",
        "university_proposals",
        ["invitation_id"],
        unique=True,
    )

    op.create_index(
        "ix_university_proposals_university_id",
        "university_proposals",
        ["university_id"],
        unique=False,
    )

    op.create_index(
        "ix_university_proposals_submitted_by",
        "university_proposals",
        ["submitted_by"],
        unique=False,
    )

    op.create_index(
        "ix_university_proposals_status",
        "university_proposals",
        ["status"],
        unique=False,
    )


def downgrade() -> None:
    # --------------------------------------------------------
    # Drop indexes
    # --------------------------------------------------------

    op.drop_index(
        "ix_university_proposals_status",
        table_name="university_proposals",
    )

    op.drop_index(
        "ix_university_proposals_submitted_by",
        table_name="university_proposals",
    )

    op.drop_index(
        "ix_university_proposals_university_id",
        table_name="university_proposals",
    )

    op.drop_index(
        "ix_university_proposals_invitation_id",
        table_name="university_proposals",
    )

    op.drop_index(
        "ix_university_proposals_rfp_id",
        table_name="university_proposals",
    )

    # --------------------------------------------------------
    # Drop table
    # --------------------------------------------------------

    op.drop_table(
        "university_proposals",
    )

    # --------------------------------------------------------
    # Drop enum
    # --------------------------------------------------------

    proposal_status_enum = postgresql.ENUM(
        "DRAFT",
        "SUBMITTED",
        "UNDER_EVALUATION",
        "SHORTLISTED",
        "REJECTED",
        "WITHDRAWN",
        name="universityproposalstatus",
    )

    proposal_status_enum.drop(
        op.get_bind(),
        checkfirst=True,
    )