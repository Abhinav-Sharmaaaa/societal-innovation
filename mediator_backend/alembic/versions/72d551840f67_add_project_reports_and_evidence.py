"""add project reports and evidence

Revision ID: 72d551840f67
Revises: 2b22f288ca15
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql


revision: str = "72d551840f67"

down_revision: Union[str, Sequence[str], None] = "2b22f288ca15"

branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ---------------------------------------------------------
    # Project report type enum
    # ---------------------------------------------------------
    project_report_type_enum = postgresql.ENUM(
        "PROGRESS",
        "MILESTONE",
        "FINANCIAL",
        "PILOT",
        "FINAL",
        name="projectreporttype",
    )

    project_report_type_enum.create(
        op.get_bind(),
        checkfirst=True,
    )

    project_report_type_column_enum = postgresql.ENUM(
        "PROGRESS",
        "MILESTONE",
        "FINANCIAL",
        "PILOT",
        "FINAL",
        name="projectreporttype",
        create_type=False,
    )

    # ---------------------------------------------------------
    # Project report status enum
    # ---------------------------------------------------------
    project_report_status_enum = postgresql.ENUM(
        "DRAFT",
        "SUBMITTED",
        "UNDER_REVIEW",
        "APPROVED",
        "REJECTED",
        name="projectreportstatus",
    )

    project_report_status_enum.create(
        op.get_bind(),
        checkfirst=True,
    )

    project_report_status_column_enum = postgresql.ENUM(
        "DRAFT",
        "SUBMITTED",
        "UNDER_REVIEW",
        "APPROVED",
        "REJECTED",
        name="projectreportstatus",
        create_type=False,
    )

    # ---------------------------------------------------------
    # Project evidence type enum
    # ---------------------------------------------------------
    project_evidence_type_enum = postgresql.ENUM(
        "DOCUMENT",
        "IMAGE",
        "VIDEO",
        "DATASET",
        "LINK",
        name="projectevidencetype",
    )

    project_evidence_type_enum.create(
        op.get_bind(),
        checkfirst=True,
    )

    project_evidence_type_column_enum = postgresql.ENUM(
        "DOCUMENT",
        "IMAGE",
        "VIDEO",
        "DATASET",
        "LINK",
        name="projectevidencetype",
        create_type=False,
    )

    # ---------------------------------------------------------
    # Create project reports
    # ---------------------------------------------------------
    op.create_table(
        "project_reports",

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
            nullable=True,
        ),

        sa.Column(
            "submitted_by",
            sa.Integer(),
            nullable=False,
        ),

        sa.Column(
            "report_type",
            project_report_type_column_enum,
            nullable=False,
        ),

        sa.Column(
            "title",
            sa.Text(),
            nullable=False,
        ),

        sa.Column(
            "summary",
            sa.Text(),
            nullable=False,
        ),

        sa.Column(
            "findings",
            sa.Text(),
            nullable=True,
        ),

        sa.Column(
            "challenges",
            sa.Text(),
            nullable=True,
        ),

        sa.Column(
            "next_steps",
            sa.Text(),
            nullable=True,
        ),

        sa.Column(
            "status",
            project_report_status_column_enum,
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
            "review_remarks",
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
            ["milestone_id"],
            ["project_milestones.id"],
            ondelete="SET NULL",
        ),

        sa.ForeignKeyConstraint(
            ["submitted_by"],
            ["users.id"],
            ondelete="RESTRICT",
        ),

        sa.PrimaryKeyConstraint("id"),
    )

    # ---------------------------------------------------------
    # Project report indexes
    # ---------------------------------------------------------
    op.create_index(
        "ix_project_reports_id",
        "project_reports",
        ["id"],
        unique=False,
    )

    op.create_index(
        "ix_project_reports_project_id",
        "project_reports",
        ["project_id"],
        unique=False,
    )

    op.create_index(
        "ix_project_reports_milestone_id",
        "project_reports",
        ["milestone_id"],
        unique=False,
    )

    op.create_index(
        "ix_project_reports_submitted_by",
        "project_reports",
        ["submitted_by"],
        unique=False,
    )

    # ---------------------------------------------------------
    # Create project evidence
    # ---------------------------------------------------------
    op.create_table(
        "project_evidence",

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
            "report_id",
            sa.Integer(),
            nullable=True,
        ),

        sa.Column(
            "uploaded_by",
            sa.Integer(),
            nullable=False,
        ),

        sa.Column(
            "evidence_type",
            project_evidence_type_column_enum,
            nullable=False,
        ),

        sa.Column(
            "title",
            sa.String(length=255),
            nullable=False,
        ),

        sa.Column(
            "file_url",
            sa.Text(),
            nullable=True,
        ),

        sa.Column(
            "external_url",
            sa.Text(),
            nullable=True,
        ),

        sa.Column(
            "description",
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
            ["report_id"],
            ["project_reports.id"],
            ondelete="CASCADE",
        ),

        sa.ForeignKeyConstraint(
            ["uploaded_by"],
            ["users.id"],
            ondelete="RESTRICT",
        ),

        sa.PrimaryKeyConstraint("id"),
    )

    # ---------------------------------------------------------
    # Project evidence indexes
    # ---------------------------------------------------------
    op.create_index(
        "ix_project_evidence_id",
        "project_evidence",
        ["id"],
        unique=False,
    )

    op.create_index(
        "ix_project_evidence_project_id",
        "project_evidence",
        ["project_id"],
        unique=False,
    )

    op.create_index(
        "ix_project_evidence_report_id",
        "project_evidence",
        ["report_id"],
        unique=False,
    )

    op.create_index(
        "ix_project_evidence_uploaded_by",
        "project_evidence",
        ["uploaded_by"],
        unique=False,
    )


def downgrade() -> None:
    # ---------------------------------------------------------
    # Drop evidence indexes
    # ---------------------------------------------------------
    op.drop_index(
        "ix_project_evidence_uploaded_by",
        table_name="project_evidence",
    )

    op.drop_index(
        "ix_project_evidence_report_id",
        table_name="project_evidence",
    )

    op.drop_index(
        "ix_project_evidence_project_id",
        table_name="project_evidence",
    )

    op.drop_index(
        "ix_project_evidence_id",
        table_name="project_evidence",
    )

    # ---------------------------------------------------------
    # Drop reports indexes
    # ---------------------------------------------------------
    op.drop_index(
        "ix_project_reports_submitted_by",
        table_name="project_reports",
    )

    op.drop_index(
        "ix_project_reports_milestone_id",
        table_name="project_reports",
    )

    op.drop_index(
        "ix_project_reports_project_id",
        table_name="project_reports",
    )

    op.drop_index(
        "ix_project_reports_id",
        table_name="project_reports",
    )

    # ---------------------------------------------------------
    # Drop tables
    # ---------------------------------------------------------
    op.drop_table("project_evidence")
    op.drop_table("project_reports")

    # ---------------------------------------------------------
    # Drop enums
    # ---------------------------------------------------------
    project_evidence_type_enum = postgresql.ENUM(
        "DOCUMENT",
        "IMAGE",
        "VIDEO",
        "DATASET",
        "LINK",
        name="projectevidencetype",
    )

    project_evidence_type_enum.drop(
        op.get_bind(),
        checkfirst=True,
    )

    project_report_status_enum = postgresql.ENUM(
        "DRAFT",
        "SUBMITTED",
        "UNDER_REVIEW",
        "APPROVED",
        "REJECTED",
        name="projectreportstatus",
    )

    project_report_status_enum.drop(
        op.get_bind(),
        checkfirst=True,
    )

    project_report_type_enum = postgresql.ENUM(
        "PROGRESS",
        "MILESTONE",
        "FINANCIAL",
        "PILOT",
        "FINAL",
        name="projectreporttype",
    )

    project_report_type_enum.drop(
        op.get_bind(),
        checkfirst=True,
    )