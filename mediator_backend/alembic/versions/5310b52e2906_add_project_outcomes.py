"""add project outcomes

Revision ID: 5310b52e2906
Revises: 72d551840f67
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql


revision: str = "5310b52e2906"

down_revision: Union[str, Sequence[str], None] = "72d551840f67"

branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ---------------------------------------------------------
    # Create outcome metric type enum
    # ---------------------------------------------------------
    outcome_metric_type_enum = postgresql.ENUM(
        "COUNT",
        "PERCENTAGE",
        "CURRENCY",
        "SCORE",
        "TEXT",
        name="projectoutcomemetrictype",
    )

    outcome_metric_type_enum.create(
        op.get_bind(),
        checkfirst=True,
    )

    outcome_metric_type_column_enum = postgresql.ENUM(
        "COUNT",
        "PERCENTAGE",
        "CURRENCY",
        "SCORE",
        "TEXT",
        name="projectoutcomemetrictype",
        create_type=False,
    )

    # ---------------------------------------------------------
    # Create outcome status enum
    # ---------------------------------------------------------
    outcome_status_enum = postgresql.ENUM(
        "DRAFT",
        "SUBMITTED",
        "UNDER_REVIEW",
        "VERIFIED",
        "REJECTED",
        name="projectoutcomestatus",
    )

    outcome_status_enum.create(
        op.get_bind(),
        checkfirst=True,
    )

    outcome_status_column_enum = postgresql.ENUM(
        "DRAFT",
        "SUBMITTED",
        "UNDER_REVIEW",
        "VERIFIED",
        "REJECTED",
        name="projectoutcomestatus",
        create_type=False,
    )

    # ---------------------------------------------------------
    # Create project outcomes table
    # ---------------------------------------------------------
    op.create_table(
        "project_outcomes",

        sa.Column(
            "id",
            sa.Integer(),
            autoincrement=True,
            nullable=False,
        ),

        sa.Column(
            "project_id",
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
            "description",
            sa.Text(),
            nullable=False,
        ),

        sa.Column(
            "beneficiary_count",
            sa.Integer(),
            nullable=True,
        ),

        sa.Column(
            "metric_name",
            sa.String(length=255),
            nullable=True,
        ),

        sa.Column(
            "metric_type",
            outcome_metric_type_column_enum,
            nullable=True,
        ),

        sa.Column(
            "baseline_value",
            sa.Float(),
            nullable=True,
        ),

        sa.Column(
            "target_value",
            sa.Float(),
            nullable=True,
        ),

        sa.Column(
            "achieved_value",
            sa.Float(),
            nullable=True,
        ),

        sa.Column(
            "impact_score",
            sa.Float(),
            nullable=True,
        ),

        sa.Column(
            "status",
            outcome_status_column_enum,
            nullable=False,
        ),

        sa.Column(
            "submitted_at",
            sa.DateTime(timezone=True),
            nullable=True,
        ),

        sa.Column(
            "verified_at",
            sa.DateTime(timezone=True),
            nullable=True,
        ),

        sa.Column(
            "verification_remarks",
            sa.Text(),
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
            ["project_id"],
            ["projects.id"],
            ondelete="CASCADE",
        ),

        sa.ForeignKeyConstraint(
            ["submitted_by"],
            ["users.id"],
            ondelete="RESTRICT",
        ),

        sa.PrimaryKeyConstraint("id"),
    )

    # ---------------------------------------------------------
    # Indexes
    # ---------------------------------------------------------

    op.create_index(
        "ix_project_outcomes_id",
        "project_outcomes",
        ["id"],
        unique=False,
    )

    op.create_index(
        "ix_project_outcomes_project_id",
        "project_outcomes",
        ["project_id"],
        unique=False,
    )

    op.create_index(
        "ix_project_outcomes_submitted_by",
        "project_outcomes",
        ["submitted_by"],
        unique=False,
    )


def downgrade() -> None:
    # ---------------------------------------------------------
    # Drop indexes
    # ---------------------------------------------------------

    op.drop_index(
        "ix_project_outcomes_submitted_by",
        table_name="project_outcomes",
    )

    op.drop_index(
        "ix_project_outcomes_project_id",
        table_name="project_outcomes",
    )

    op.drop_index(
        "ix_project_outcomes_id",
        table_name="project_outcomes",
    )

    # ---------------------------------------------------------
    # Drop table
    # ---------------------------------------------------------

    op.drop_table("project_outcomes")

    # ---------------------------------------------------------
    # Drop enums
    # ---------------------------------------------------------

    outcome_status_enum = postgresql.ENUM(
        "DRAFT",
        "SUBMITTED",
        "UNDER_REVIEW",
        "VERIFIED",
        "REJECTED",
        name="projectoutcomestatus",
    )

    outcome_status_enum.drop(
        op.get_bind(),
        checkfirst=True,
    )

    outcome_metric_type_enum = postgresql.ENUM(
        "COUNT",
        "PERCENTAGE",
        "CURRENCY",
        "SCORE",
        "TEXT",
        name="projectoutcomemetrictype",
    )

    outcome_metric_type_enum.drop(
        op.get_bind(),
        checkfirst=True,
    )