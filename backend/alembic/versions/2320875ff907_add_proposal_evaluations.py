"""add proposal evaluations

Revision ID: 2320875ff907
Revises: 0354c2f0fb55
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql


revision: str = "2320875ff907"

down_revision: Union[str, Sequence[str], None] = "0354c2f0fb55"

branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    proposal_evaluation_decision_enum = postgresql.ENUM(
        "UNDER_REVIEW",
        "SHORTLISTED",
        "REJECTED",
        name="proposalevaluationdecision",
    )

    proposal_evaluation_decision_enum.create(
        op.get_bind(),
        checkfirst=True,
    )

    proposal_evaluation_decision_column_enum = postgresql.ENUM(
        "UNDER_REVIEW",
        "SHORTLISTED",
        "REJECTED",
        name="proposalevaluationdecision",
        create_type=False,
    )

    op.create_table(
        "proposal_evaluations",
        sa.Column(
            "id",
            sa.Integer(),
            autoincrement=True,
            nullable=False,
        ),

        sa.Column(
            "proposal_id",
            sa.Integer(),
            nullable=False,
        ),

        sa.Column(
            "evaluated_by",
            sa.Integer(),
            nullable=False,
        ),

        sa.Column(
            "technical_feasibility_score",
            sa.Float(),
            nullable=False,
        ),

        sa.Column(
            "innovation_score",
            sa.Float(),
            nullable=False,
        ),

        sa.Column(
            "cost_effectiveness_score",
            sa.Float(),
            nullable=False,
        ),

        sa.Column(
            "impact_score",
            sa.Float(),
            nullable=False,
        ),

        sa.Column(
            "timeline_score",
            sa.Float(),
            nullable=False,
        ),

        sa.Column(
            "scalability_score",
            sa.Float(),
            nullable=False,
        ),

        sa.Column(
            "research_capability_score",
            sa.Float(),
            nullable=False,
        ),

        sa.Column(
            "overall_score",
            sa.Float(),
            nullable=False,
        ),

        sa.Column(
            "remarks",
            sa.Text(),
            nullable=True,
        ),

        sa.Column(
            "decision",
            proposal_evaluation_decision_column_enum,
            nullable=False,
        ),

        sa.Column(
            "evaluated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
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
            ["proposal_id"],
            ["university_proposals.id"],
            ondelete="CASCADE",
        ),

        sa.ForeignKeyConstraint(
            ["evaluated_by"],
            ["users.id"],
            ondelete="RESTRICT",
        ),

        sa.PrimaryKeyConstraint("id"),

        sa.UniqueConstraint(
            "proposal_id",
            name="uq_proposal_evaluation_proposal",
        ),
    )

    op.create_index(
        "ix_proposal_evaluations_proposal_id",
        "proposal_evaluations",
        ["proposal_id"],
        unique=False,
    )

    op.create_index(
        "ix_proposal_evaluations_evaluated_by",
        "proposal_evaluations",
        ["evaluated_by"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(
        "ix_proposal_evaluations_evaluated_by",
        table_name="proposal_evaluations",
    )

    op.drop_index(
        "ix_proposal_evaluations_proposal_id",
        table_name="proposal_evaluations",
    )

    op.drop_table("proposal_evaluations")

    proposal_evaluation_decision_enum = postgresql.ENUM(
        "UNDER_REVIEW",
        "SHORTLISTED",
        "REJECTED",
        name="proposalevaluationdecision",
    )

    proposal_evaluation_decision_enum.drop(
        op.get_bind(),
        checkfirst=True,
    )