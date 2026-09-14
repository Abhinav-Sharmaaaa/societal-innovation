"""add project risks

Revision ID: 8bafdd800eae
Revises: 5310b52e2906
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql


revision: str = "8bafdd800eae"

down_revision: Union[str, Sequence[str], None] = "5310b52e2906"

branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ---------------------------------------------------------
    # Risk level enum
    # ---------------------------------------------------------
    project_risk_level_enum = postgresql.ENUM(
        "LOW",
        "MEDIUM",
        "HIGH",
        "CRITICAL",
        name="projectrisklevel",
    )

    project_risk_level_enum.create(
        op.get_bind(),
        checkfirst=True,
    )

    project_risk_level_column_enum = postgresql.ENUM(
        "LOW",
        "MEDIUM",
        "HIGH",
        "CRITICAL",
        name="projectrisklevel",
        create_type=False,
    )

    # ---------------------------------------------------------
    # Risk status enum
    # ---------------------------------------------------------
    project_risk_status_enum = postgresql.ENUM(
        "OPEN",
        "ACKNOWLEDGED",
        "MITIGATED",
        "CLOSED",
        name="projectriskstatus",
    )

    project_risk_status_enum.create(
        op.get_bind(),
        checkfirst=True,
    )

    project_risk_status_column_enum = postgresql.ENUM(
        "OPEN",
        "ACKNOWLEDGED",
        "MITIGATED",
        "CLOSED",
        name="projectriskstatus",
        create_type=False,
    )

    # ---------------------------------------------------------
    # Create project risks table
    # ---------------------------------------------------------
    op.create_table(
        "project_risks",

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
            "risk_level",
            project_risk_level_column_enum,
            nullable=False,
        ),

        sa.Column(
            "risk_score",
            sa.Float(),
            nullable=False,
        ),

        sa.Column(
            "title",
            sa.Text(),
            nullable=False,
        ),

        sa.Column(
            "description",
            sa.Text(),
            nullable=False,
        ),

        sa.Column(
            "detected_factors",
            sa.Text(),
            nullable=True,
        ),

        sa.Column(
            "recommended_action",
            sa.Text(),
            nullable=True,
        ),

        sa.Column(
            "status",
            project_risk_status_column_enum,
            nullable=False,
        ),

        sa.Column(
            "detected_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),

        sa.Column(
            "acknowledged_at",
            sa.DateTime(timezone=True),
            nullable=True,
        ),

        sa.Column(
            "resolved_at",
            sa.DateTime(timezone=True),
            nullable=True,
        ),

        sa.Column(
            "resolution_remarks",
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

        sa.PrimaryKeyConstraint("id"),
    )

    # ---------------------------------------------------------
    # Indexes
    # ---------------------------------------------------------

    op.create_index(
        "ix_project_risks_id",
        "project_risks",
        ["id"],
        unique=False,
    )

    op.create_index(
        "ix_project_risks_project_id",
        "project_risks",
        ["project_id"],
        unique=False,
    )


def downgrade() -> None:
    # ---------------------------------------------------------
    # Drop indexes
    # ---------------------------------------------------------

    op.drop_index(
        "ix_project_risks_project_id",
        table_name="project_risks",
    )

    op.drop_index(
        "ix_project_risks_id",
        table_name="project_risks",
    )

    # ---------------------------------------------------------
    # Drop table
    # ---------------------------------------------------------

    op.drop_table("project_risks")

    # ---------------------------------------------------------
    # Drop enums
    # ---------------------------------------------------------

    project_risk_status_enum = postgresql.ENUM(
        "OPEN",
        "ACKNOWLEDGED",
        "MITIGATED",
        "CLOSED",
        name="projectriskstatus",
    )

    project_risk_status_enum.drop(
        op.get_bind(),
        checkfirst=True,
    )

    project_risk_level_enum = postgresql.ENUM(
        "LOW",
        "MEDIUM",
        "HIGH",
        "CRITICAL",
        name="projectrisklevel",
    )

    project_risk_level_enum.drop(
        op.get_bind(),
        checkfirst=True,
    )