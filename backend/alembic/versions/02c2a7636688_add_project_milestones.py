"""add project milestones

Revision ID: 02c2a7636688
Revises: 65ac13114f66
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql


revision: str = "02c2a7636688"

down_revision: Union[str, Sequence[str], None] = "65ac13114f66"

branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ---------------------------------------------------------
    # Create milestone status enum
    # ---------------------------------------------------------
    milestone_status_enum = postgresql.ENUM(
        "NOT_STARTED",
        "IN_PROGRESS",
        "COMPLETED",
        "DELAYED",
        "BLOCKED",
        name="projectmilestonestatus",
    )

    milestone_status_enum.create(
        op.get_bind(),
        checkfirst=True,
    )

    milestone_status_column_enum = postgresql.ENUM(
        "NOT_STARTED",
        "IN_PROGRESS",
        "COMPLETED",
        "DELAYED",
        "BLOCKED",
        name="projectmilestonestatus",
        create_type=False,
    )

    # ---------------------------------------------------------
    # Create milestone type enum
    # ---------------------------------------------------------
    milestone_type_enum = postgresql.ENUM(
        "PROBLEM_VALIDATION",
        "RESEARCH_PLANNING",
        "PROTOTYPE_DEVELOPMENT",
        "TESTING_VALIDATION",
        "PILOT_DEPLOYMENT",
        "FINAL_SOLUTION_DEPLOYMENT",
        name="projectmilestonetype",
    )

    milestone_type_enum.create(
        op.get_bind(),
        checkfirst=True,
    )

    milestone_type_column_enum = postgresql.ENUM(
        "PROBLEM_VALIDATION",
        "RESEARCH_PLANNING",
        "PROTOTYPE_DEVELOPMENT",
        "TESTING_VALIDATION",
        "PILOT_DEPLOYMENT",
        "FINAL_SOLUTION_DEPLOYMENT",
        name="projectmilestonetype",
        create_type=False,
    )

    # ---------------------------------------------------------
    # Create project milestones table
    # ---------------------------------------------------------
    op.create_table(
        "project_milestones",

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
            "milestone_type",
            milestone_type_column_enum,
            nullable=False,
        ),

        sa.Column(
            "sequence_number",
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
            nullable=True,
        ),

        sa.Column(
            "deliverables",
            sa.Text(),
            nullable=True,
        ),

        sa.Column(
            "start_date",
            sa.DateTime(timezone=True),
            nullable=True,
        ),

        sa.Column(
            "due_date",
            sa.DateTime(timezone=True),
            nullable=True,
        ),

        sa.Column(
            "completed_at",
            sa.DateTime(timezone=True),
            nullable=True,
        ),

        sa.Column(
            "status",
            milestone_status_column_enum,
            nullable=False,
        ),

        sa.Column(
            "progress_percentage",
            sa.Float(),
            nullable=False,
            server_default=sa.text("0"),
        ),

        sa.Column(
            "is_mandatory",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("true"),
        ),

        sa.Column(
            "completion_remarks",
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
        "ix_project_milestones_id",
        "project_milestones",
        ["id"],
        unique=False,
    )

    op.create_index(
        "ix_project_milestones_project_id",
        "project_milestones",
        ["project_id"],
        unique=False,
    )

    # Useful for project-level ordering and status queries
    op.create_index(
        "ix_project_milestones_project_sequence",
        "project_milestones",
        ["project_id", "sequence_number"],
        unique=False,
    )

    op.create_index(
        "ix_project_milestones_status",
        "project_milestones",
        ["status"],
        unique=False,
    )


def downgrade() -> None:
    # ---------------------------------------------------------
    # Drop indexes
    # ---------------------------------------------------------

    op.drop_index(
        "ix_project_milestones_status",
        table_name="project_milestones",
    )

    op.drop_index(
        "ix_project_milestones_project_sequence",
        table_name="project_milestones",
    )

    op.drop_index(
        "ix_project_milestones_project_id",
        table_name="project_milestones",
    )

    op.drop_index(
        "ix_project_milestones_id",
        table_name="project_milestones",
    )

    # ---------------------------------------------------------
    # Drop table
    # ---------------------------------------------------------

    op.drop_table(
        "project_milestones",
    )

    # ---------------------------------------------------------
    # Drop enums
    # ---------------------------------------------------------

    milestone_type_enum = postgresql.ENUM(
        "PROBLEM_VALIDATION",
        "RESEARCH_PLANNING",
        "PROTOTYPE_DEVELOPMENT",
        "TESTING_VALIDATION",
        "PILOT_DEPLOYMENT",
        "FINAL_SOLUTION_DEPLOYMENT",
        name="projectmilestonetype",
    )

    milestone_type_enum.drop(
        op.get_bind(),
        checkfirst=True,
    )

    milestone_status_enum = postgresql.ENUM(
        "NOT_STARTED",
        "IN_PROGRESS",
        "COMPLETED",
        "DELAYED",
        "BLOCKED",
        name="projectmilestonestatus",
    )

    milestone_status_enum.drop(
        op.get_bind(),
        checkfirst=True,
    )