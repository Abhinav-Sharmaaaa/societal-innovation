"""add reputation system

Revision ID: 735717c758fc
Revises: e8bdfc01482a
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql


revision: str = "735717c758fc"

down_revision: Union[str, Sequence[str], None] = "e8bdfc01482a"

branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ---------------------------------------------------------
    # Reputation entity type enum
    # ---------------------------------------------------------
    reputation_entity_type_enum = postgresql.ENUM(
        "CITIZEN",
        "UNIVERSITY",
        "INDUSTRY",
        name="reputationentitytype",
    )

    reputation_entity_type_enum.create(
        op.get_bind(),
        checkfirst=True,
    )

    reputation_entity_type_column_enum = postgresql.ENUM(
        "CITIZEN",
        "UNIVERSITY",
        "INDUSTRY",
        name="reputationentitytype",
        create_type=False,
    )

    # ---------------------------------------------------------
    # Reputation event type enum
    # ---------------------------------------------------------
    reputation_event_type_enum = postgresql.ENUM(
        "CHALLENGE_SUBMITTED",
        "CHALLENGE_VALIDATED",
        "UNIVERSITY_PROPOSAL",
        "PROJECT_CONTRIBUTION",
        "MILESTONE_COMPLETED",
        "DELIVERABLE_APPROVED",
        "FUNDING_CONTRIBUTION",
        "PROJECT_COMPLETED",
        "POSITIVE_PROJECT_OUTCOME",
        name="reputationeventtype",
    )

    reputation_event_type_enum.create(
        op.get_bind(),
        checkfirst=True,
    )

    reputation_event_type_column_enum = postgresql.ENUM(
        "CHALLENGE_SUBMITTED",
        "CHALLENGE_VALIDATED",
        "UNIVERSITY_PROPOSAL",
        "PROJECT_CONTRIBUTION",
        "MILESTONE_COMPLETED",
        "DELIVERABLE_APPROVED",
        "FUNDING_CONTRIBUTION",
        "PROJECT_COMPLETED",
        "POSITIVE_PROJECT_OUTCOME",
        name="reputationeventtype",
        create_type=False,
    )

    # ---------------------------------------------------------
    # Reputation score entity type enum
    # ---------------------------------------------------------
    reputation_score_entity_type_enum = postgresql.ENUM(
        "CITIZEN",
        "UNIVERSITY",
        "INDUSTRY",
        name="reputationscoreentitytype",
    )

    reputation_score_entity_type_enum.create(
        op.get_bind(),
        checkfirst=True,
    )

    reputation_score_entity_type_column_enum = postgresql.ENUM(
        "CITIZEN",
        "UNIVERSITY",
        "INDUSTRY",
        name="reputationscoreentitytype",
        create_type=False,
    )

    # ---------------------------------------------------------
    # Create reputation events
    # ---------------------------------------------------------
    op.create_table(
        "reputation_events",

        sa.Column(
            "id",
            sa.Integer(),
            autoincrement=True,
            nullable=False,
        ),

        sa.Column(
            "entity_type",
            reputation_entity_type_column_enum,
            nullable=False,
        ),

        sa.Column(
            "user_id",
            sa.Integer(),
            nullable=True,
        ),

        sa.Column(
            "organization_id",
            sa.Integer(),
            nullable=True,
        ),

        sa.Column(
            "event_type",
            reputation_event_type_column_enum,
            nullable=False,
        ),

        sa.Column(
            "points",
            sa.Integer(),
            nullable=False,
        ),

        sa.Column(
            "description",
            sa.Text(),
            nullable=True,
        ),

        sa.Column(
            "project_id",
            sa.Integer(),
            nullable=True,
        ),

        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),

        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            ondelete="CASCADE",
        ),

        sa.ForeignKeyConstraint(
            ["organization_id"],
            ["organizations.id"],
            ondelete="CASCADE",
        ),

        sa.ForeignKeyConstraint(
            ["project_id"],
            ["projects.id"],
            ondelete="SET NULL",
        ),

        sa.PrimaryKeyConstraint("id"),
    )

    # ---------------------------------------------------------
    # Reputation event indexes
    # ---------------------------------------------------------
    op.create_index(
        "ix_reputation_events_id",
        "reputation_events",
        ["id"],
        unique=False,
    )

    op.create_index(
        "ix_reputation_events_entity_type",
        "reputation_events",
        ["entity_type"],
        unique=False,
    )

    op.create_index(
        "ix_reputation_events_user_id",
        "reputation_events",
        ["user_id"],
        unique=False,
    )

    op.create_index(
        "ix_reputation_events_organization_id",
        "reputation_events",
        ["organization_id"],
        unique=False,
    )

    op.create_index(
        "ix_reputation_events_event_type",
        "reputation_events",
        ["event_type"],
        unique=False,
    )

    op.create_index(
        "ix_reputation_events_project_id",
        "reputation_events",
        ["project_id"],
        unique=False,
    )

    # ---------------------------------------------------------
    # Create reputation scores
    # ---------------------------------------------------------
    op.create_table(
        "reputation_scores",

        sa.Column(
            "id",
            sa.Integer(),
            autoincrement=True,
            nullable=False,
        ),

        sa.Column(
            "entity_type",
            reputation_score_entity_type_column_enum,
            nullable=False,
        ),

        sa.Column(
            "user_id",
            sa.Integer(),
            nullable=True,
        ),

        sa.Column(
            "organization_id",
            sa.Integer(),
            nullable=True,
        ),

        sa.Column(
            "total_points",
            sa.Integer(),
            nullable=False,
            server_default=sa.text("0"),
        ),

        sa.Column(
            "contribution_count",
            sa.Integer(),
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
            ["user_id"],
            ["users.id"],
            ondelete="CASCADE",
        ),

        sa.ForeignKeyConstraint(
            ["organization_id"],
            ["organizations.id"],
            ondelete="CASCADE",
        ),

        sa.PrimaryKeyConstraint("id"),

        sa.UniqueConstraint(
            "entity_type",
            "user_id",
            "organization_id",
            name="uq_reputation_score_entity",
        ),
    )

    # ---------------------------------------------------------
    # Reputation score indexes
    # ---------------------------------------------------------
    op.create_index(
        "ix_reputation_scores_id",
        "reputation_scores",
        ["id"],
        unique=False,
    )


def downgrade() -> None:
    # ---------------------------------------------------------
    # Drop reputation score indexes/table
    # ---------------------------------------------------------
    op.drop_index(
        "ix_reputation_scores_id",
        table_name="reputation_scores",
    )

    op.drop_table("reputation_scores")

    # ---------------------------------------------------------
    # Drop reputation event indexes/table
    # ---------------------------------------------------------
    op.drop_index(
        "ix_reputation_events_project_id",
        table_name="reputation_events",
    )

    op.drop_index(
        "ix_reputation_events_event_type",
        table_name="reputation_events",
    )

    op.drop_index(
        "ix_reputation_events_organization_id",
        table_name="reputation_events",
    )

    op.drop_index(
        "ix_reputation_events_user_id",
        table_name="reputation_events",
    )

    op.drop_index(
        "ix_reputation_events_entity_type",
        table_name="reputation_events",
    )

    op.drop_index(
        "ix_reputation_events_id",
        table_name="reputation_events",
    )

    op.drop_table("reputation_events")

    # ---------------------------------------------------------
    # Drop enums
    # ---------------------------------------------------------
    reputation_score_entity_type_enum = postgresql.ENUM(
        "CITIZEN",
        "UNIVERSITY",
        "INDUSTRY",
        name="reputationscoreentitytype",
    )

    reputation_score_entity_type_enum.drop(
        op.get_bind(),
        checkfirst=True,
    )

    reputation_event_type_enum = postgresql.ENUM(
        "CHALLENGE_SUBMITTED",
        "CHALLENGE_VALIDATED",
        "UNIVERSITY_PROPOSAL",
        "PROJECT_CONTRIBUTION",
        "MILESTONE_COMPLETED",
        "DELIVERABLE_APPROVED",
        "FUNDING_CONTRIBUTION",
        "PROJECT_COMPLETED",
        "POSITIVE_PROJECT_OUTCOME",
        name="reputationeventtype",
    )

    reputation_event_type_enum.drop(
        op.get_bind(),
        checkfirst=True,
    )

    reputation_entity_type_enum = postgresql.ENUM(
        "CITIZEN",
        "UNIVERSITY",
        "INDUSTRY",
        name="reputationentitytype",
    )

    reputation_entity_type_enum.drop(
        op.get_bind(),
        checkfirst=True,
    )