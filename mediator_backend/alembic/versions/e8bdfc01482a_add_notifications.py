"""add notifications

Revision ID: e8bdfc01482a
Revises: 8bafdd800eae
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql


revision: str = "e8bdfc01482a"

down_revision: Union[str, Sequence[str], None] = "8bafdd800eae"

branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ---------------------------------------------------------
    # Notification type enum
    # ---------------------------------------------------------
    notification_type_enum = postgresql.ENUM(
        "RISK_ALERT",
        "DEADLINE_ALERT",
        "PROJECT_UPDATE",
        "MILESTONE_UPDATE",
        "FUNDING_ALERT",
        name="notificationtype",
    )

    notification_type_enum.create(
        op.get_bind(),
        checkfirst=True,
    )

    notification_type_column_enum = postgresql.ENUM(
        "RISK_ALERT",
        "DEADLINE_ALERT",
        "PROJECT_UPDATE",
        "MILESTONE_UPDATE",
        "FUNDING_ALERT",
        name="notificationtype",
        create_type=False,
    )

    # ---------------------------------------------------------
    # Notification priority enum
    # ---------------------------------------------------------
    notification_priority_enum = postgresql.ENUM(
        "LOW",
        "MEDIUM",
        "HIGH",
        "CRITICAL",
        name="notificationpriority",
    )

    notification_priority_enum.create(
        op.get_bind(),
        checkfirst=True,
    )

    notification_priority_column_enum = postgresql.ENUM(
        "LOW",
        "MEDIUM",
        "HIGH",
        "CRITICAL",
        name="notificationpriority",
        create_type=False,
    )

    # ---------------------------------------------------------
    # Create notifications table
    # ---------------------------------------------------------
    op.create_table(
        "notifications",

        sa.Column(
            "id",
            sa.Integer(),
            autoincrement=True,
            nullable=False,
        ),

        sa.Column(
            "user_id",
            sa.Integer(),
            nullable=False,
        ),

        sa.Column(
            "project_id",
            sa.Integer(),
            nullable=True,
        ),

        sa.Column(
            "notification_type",
            notification_type_column_enum,
            nullable=False,
        ),

        sa.Column(
            "priority",
            notification_priority_column_enum,
            nullable=False,
        ),

        sa.Column(
            "title",
            sa.Text(),
            nullable=False,
        ),

        sa.Column(
            "message",
            sa.Text(),
            nullable=False,
        ),

        sa.Column(
            "is_read",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("false"),
        ),

        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),

        sa.Column(
            "read_at",
            sa.DateTime(timezone=True),
            nullable=True,
        ),

        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            ondelete="CASCADE",
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
        "ix_notifications_id",
        "notifications",
        ["id"],
        unique=False,
    )

    op.create_index(
        "ix_notifications_user_id",
        "notifications",
        ["user_id"],
        unique=False,
    )

    op.create_index(
        "ix_notifications_project_id",
        "notifications",
        ["project_id"],
        unique=False,
    )

    op.create_index(
        "ix_notifications_created_at",
        "notifications",
        ["created_at"],
        unique=False,
    )


def downgrade() -> None:
    # ---------------------------------------------------------
    # Drop indexes
    # ---------------------------------------------------------
    op.drop_index(
        "ix_notifications_created_at",
        table_name="notifications",
    )

    op.drop_index(
        "ix_notifications_project_id",
        table_name="notifications",
    )

    op.drop_index(
        "ix_notifications_user_id",
        table_name="notifications",
    )

    op.drop_index(
        "ix_notifications_id",
        table_name="notifications",
    )

    # ---------------------------------------------------------
    # Drop table
    # ---------------------------------------------------------
    op.drop_table("notifications")

    # ---------------------------------------------------------
    # Drop enums
    # ---------------------------------------------------------
    notification_priority_enum = postgresql.ENUM(
        "LOW",
        "MEDIUM",
        "HIGH",
        "CRITICAL",
        name="notificationpriority",
    )

    notification_priority_enum.drop(
        op.get_bind(),
        checkfirst=True,
    )

    notification_type_enum = postgresql.ENUM(
        "RISK_ALERT",
        "DEADLINE_ALERT",
        "PROJECT_UPDATE",
        "MILESTONE_UPDATE",
        "FUNDING_ALERT",
        name="notificationtype",
    )

    notification_type_enum.drop(
        op.get_bind(),
        checkfirst=True,
    )