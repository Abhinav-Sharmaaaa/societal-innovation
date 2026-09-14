"""add project execution

Revision ID: 65ac13114f66
Revises: 3b70bab58548
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql


revision: str = "65ac13114f66"

down_revision: Union[str, Sequence[str], None] = "3b70bab58548"

branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ---------------------------------------------------------
    # Create project status enum
    # ---------------------------------------------------------
    project_status_enum = postgresql.ENUM(
        "PLANNING",
        "ACTIVE",
        "ON_HOLD",
        "COMPLETED",
        "CANCELLED",
        name="projectstatus",
    )

    project_status_enum.create(
        op.get_bind(),
        checkfirst=True,
    )

    project_status_column_enum = postgresql.ENUM(
        "PLANNING",
        "ACTIVE",
        "ON_HOLD",
        "COMPLETED",
        "CANCELLED",
        name="projectstatus",
        create_type=False,
    )

    # ---------------------------------------------------------
    # Create project health enum
    # ---------------------------------------------------------
    project_health_enum = postgresql.ENUM(
        "ON_TRACK",
        "AT_RISK",
        "DELAYED",
        "CRITICAL",
        name="projecthealth",
    )

    project_health_enum.create(
        op.get_bind(),
        checkfirst=True,
    )

    project_health_column_enum = postgresql.ENUM(
        "ON_TRACK",
        "AT_RISK",
        "DELAYED",
        "CRITICAL",
        name="projecthealth",
        create_type=False,
    )

    # ---------------------------------------------------------
    # Create projects table
    # ---------------------------------------------------------
    op.create_table(
        "projects",

        sa.Column(
            "id",
            sa.Integer(),
            autoincrement=True,
            nullable=False,
        ),

        sa.Column(
            "collaboration_id",
            sa.Integer(),
            nullable=False,
        ),

        sa.Column(
            "challenge_id",
            sa.Integer(),
            nullable=False,
        ),

        sa.Column(
            "university_id",
            sa.Integer(),
            nullable=False,
        ),

        sa.Column(
            "industry_id",
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
            nullable=True,
        ),

        sa.Column(
            "objectives",
            sa.Text(),
            nullable=True,
        ),

        sa.Column(
            "expected_outcomes",
            sa.Text(),
            nullable=True,
        ),

        sa.Column(
            "total_budget",
            sa.Float(),
            nullable=True,
        ),

        sa.Column(
            "start_date",
            sa.DateTime(timezone=True),
            nullable=True,
        ),

        sa.Column(
            "target_completion_date",
            sa.DateTime(timezone=True),
            nullable=True,
        ),

        sa.Column(
            "actual_completion_date",
            sa.DateTime(timezone=True),
            nullable=True,
        ),

        sa.Column(
            "status",
            project_status_column_enum,
            nullable=False,
        ),

        sa.Column(
            "health",
            project_health_column_enum,
            nullable=False,
        ),

        sa.Column(
            "progress_percentage",
            sa.Float(),
            nullable=False,
            server_default=sa.text("0"),
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
            ["collaboration_id"],
            ["industry_collaboration_proposals.id"],
            ondelete="RESTRICT",
        ),

        sa.ForeignKeyConstraint(
            ["challenge_id"],
            ["challenges.id"],
            ondelete="RESTRICT",
        ),

        sa.ForeignKeyConstraint(
            ["university_id"],
            ["organizations.id"],
            ondelete="RESTRICT",
        ),

        sa.ForeignKeyConstraint(
            ["industry_id"],
            ["organizations.id"],
            ondelete="RESTRICT",
        ),

        sa.ForeignKeyConstraint(
            ["created_by"],
            ["users.id"],
            ondelete="RESTRICT",
        ),

        sa.PrimaryKeyConstraint("id"),

        sa.UniqueConstraint(
            "collaboration_id",
            name="uq_project_collaboration",
        ),
    )

    # ---------------------------------------------------------
    # Indexes
    # ---------------------------------------------------------

    op.create_index(
        "ix_projects_id",
        "projects",
        ["id"],
        unique=False,
    )

    op.create_index(
        "ix_projects_collaboration_id",
        "projects",
        ["collaboration_id"],
        unique=False,
    )

    op.create_index(
        "ix_projects_challenge_id",
        "projects",
        ["challenge_id"],
        unique=False,
    )

    op.create_index(
        "ix_projects_university_id",
        "projects",
        ["university_id"],
        unique=False,
    )

    op.create_index(
        "ix_projects_industry_id",
        "projects",
        ["industry_id"],
        unique=False,
    )

    op.create_index(
        "ix_projects_created_by",
        "projects",
        ["created_by"],
        unique=False,
    )


def downgrade() -> None:
    # ---------------------------------------------------------
    # Drop indexes
    # ---------------------------------------------------------

    op.drop_index(
        "ix_projects_created_by",
        table_name="projects",
    )

    op.drop_index(
        "ix_projects_industry_id",
        table_name="projects",
    )

    op.drop_index(
        "ix_projects_university_id",
        table_name="projects",
    )

    op.drop_index(
        "ix_projects_challenge_id",
        table_name="projects",
    )

    op.drop_index(
        "ix_projects_collaboration_id",
        table_name="projects",
    )

    op.drop_index(
        "ix_projects_id",
        table_name="projects",
    )

    # ---------------------------------------------------------
    # Drop table
    # ---------------------------------------------------------

    op.drop_table("projects")

    # ---------------------------------------------------------
    # Drop enums
    # ---------------------------------------------------------

    project_health_enum = postgresql.ENUM(
        "ON_TRACK",
        "AT_RISK",
        "DELAYED",
        "CRITICAL",
        name="projecthealth",
    )

    project_health_enum.drop(
        op.get_bind(),
        checkfirst=True,
    )

    project_status_enum = postgresql.ENUM(
        "PLANNING",
        "ACTIVE",
        "ON_HOLD",
        "COMPLETED",
        "CANCELLED",
        name="projectstatus",
    )

    project_status_enum.drop(
        op.get_bind(),
        checkfirst=True,
    )