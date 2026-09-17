"""add project deliverables

Revision ID: f40399eea8d7
Revises: eafc8ed0eb17
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql


revision: str = "f40399eea8d7"

down_revision: Union[str, Sequence[str], None] = "eafc8ed0eb17"

branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ---------------------------------------------------------
    # Create deliverable status enum
    # ---------------------------------------------------------
    deliverable_status_enum = postgresql.ENUM(
        "PENDING",
        "IN_PROGRESS",
        "SUBMITTED",
        "APPROVED",
        "REJECTED",
        "OVERDUE",
        name="projectdeliverablestatus",
    )

    deliverable_status_enum.create(
        op.get_bind(),
        checkfirst=True,
    )

    deliverable_status_column_enum = postgresql.ENUM(
        "PENDING",
        "IN_PROGRESS",
        "SUBMITTED",
        "APPROVED",
        "REJECTED",
        "OVERDUE",
        name="projectdeliverablestatus",
        create_type=False,
    )

    # ---------------------------------------------------------
    # Create project deliverables table
    # ---------------------------------------------------------
    op.create_table(
        "project_deliverables",

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
            "milestone_id",
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
            "due_date",
            sa.DateTime(timezone=True),
            nullable=True,
        ),

        sa.Column(
            "submitted_at",
            sa.DateTime(timezone=True),
            nullable=True,
        ),

        sa.Column(
            "approved_at",
            sa.DateTime(timezone=True),
            nullable=True,
        ),

        sa.Column(
            "status",
            deliverable_status_column_enum,
            nullable=False,
        ),

        sa.Column(
            "submission_reference",
            sa.Text(),
            nullable=True,
        ),

        sa.Column(
            "review_remarks",
            sa.Text(),
            nullable=True,
        ),

        sa.Column(
            "is_mandatory",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("true"),
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
            ["milestone_id"],
            ["project_milestones.id"],
            ondelete="CASCADE",
        ),

        sa.PrimaryKeyConstraint("id"),
    )

    # ---------------------------------------------------------
    # Indexes
    # ---------------------------------------------------------

    op.create_index(
        "ix_project_deliverables_id",
        "project_deliverables",
        ["id"],
        unique=False,
    )

    op.create_index(
        "ix_project_deliverables_project_id",
        "project_deliverables",
        ["project_id"],
        unique=False,
    )

    op.create_index(
        "ix_project_deliverables_milestone_id",
        "project_deliverables",
        ["milestone_id"],
        unique=False,
    )

    op.create_index(
        "ix_project_deliverables_status",
        "project_deliverables",
        ["status"],
        unique=False,
    )


def downgrade() -> None:
    # ---------------------------------------------------------
    # Drop indexes
    # ---------------------------------------------------------
    op.drop_index(
        "ix_project_deliverables_status",
        table_name="project_deliverables",
    )

    op.drop_index(
        "ix_project_deliverables_milestone_id",
        table_name="project_deliverables",
    )

    op.drop_index(
        "ix_project_deliverables_project_id",
        table_name="project_deliverables",
    )

    op.drop_index(
        "ix_project_deliverables_id",
        table_name="project_deliverables",
    )

    # ---------------------------------------------------------
    # Drop table
    # ---------------------------------------------------------
    op.drop_table("project_deliverables")

    # ---------------------------------------------------------
    # Drop enum
    # ---------------------------------------------------------
    deliverable_status_enum = postgresql.ENUM(
        "PENDING",
        "IN_PROGRESS",
        "SUBMITTED",
        "APPROVED",
        "REJECTED",
        "OVERDUE",
        name="projectdeliverablestatus",
    )

    deliverable_status_enum.drop(
        op.get_bind(),
        checkfirst=True,
    )