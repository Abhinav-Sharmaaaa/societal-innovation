"""add challenge reviews

Revision ID: c4e7b8129d31
Revises: b6c2a91f4e73
Create Date: 2026-09-13 01:40:00.000000
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql


revision: str = "c4e7b8129d31"

down_revision: Union[str, Sequence[str], None] = (
    "b6c2a91f4e73"
)

branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # --------------------------------------------------------
    # Create PostgreSQL enum explicitly.
    #
    # checkfirst=True means:
    # - create it if missing
    # - reuse it if already present
    # --------------------------------------------------------

    review_decision_enum = postgresql.ENUM(
        "ACCEPT_RECOMMENDATION",
        "OVERRIDE_AUTHORITY",
        name="reviewdecision",
    )

    review_decision_enum.create(
        op.get_bind(),
        checkfirst=True,
    )

    # --------------------------------------------------------
    # Reuse the already-created enum when creating the table.
    # --------------------------------------------------------

    review_decision_column_enum = postgresql.ENUM(
        "ACCEPT_RECOMMENDATION",
        "OVERRIDE_AUTHORITY",
        name="reviewdecision",
        create_type=False,
    )

    # --------------------------------------------------------
    # Create review table
    # --------------------------------------------------------

    op.create_table(
        "challenge_reviews",
        sa.Column(
            "id",
            sa.Integer(),
            autoincrement=True,
            nullable=False,
        ),
        sa.Column(
            "challenge_id",
            sa.Integer(),
            nullable=False,
        ),
        sa.Column(
            "reviewer_id",
            sa.Integer(),
            nullable=False,
        ),
        sa.Column(
            "decision",
            review_decision_column_enum,
            nullable=False,
        ),
        sa.Column(
            "recommended_authority_id",
            sa.Integer(),
            nullable=True,
        ),
        sa.Column(
            "selected_authority_id",
            sa.Integer(),
            nullable=False,
        ),
        sa.Column(
            "reason",
            sa.Text(),
            nullable=True,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["challenge_id"],
            ["challenges.id"],
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["reviewer_id"],
            ["users.id"],
            ondelete="SET NULL",
        ),
        sa.ForeignKeyConstraint(
            ["recommended_authority_id"],
            ["organizations.id"],
            ondelete="SET NULL",
        ),
        sa.ForeignKeyConstraint(
            ["selected_authority_id"],
            ["organizations.id"],
            ondelete="SET NULL",
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    # --------------------------------------------------------
    # Indexes
    # --------------------------------------------------------

    op.create_index(
        "ix_challenge_reviews_challenge_id",
        "challenge_reviews",
        ["challenge_id"],
        unique=False,
    )

    op.create_index(
        "ix_challenge_reviews_reviewer_id",
        "challenge_reviews",
        ["reviewer_id"],
        unique=False,
    )

    op.create_index(
        "ix_challenge_reviews_decision",
        "challenge_reviews",
        ["decision"],
        unique=False,
    )


def downgrade() -> None:
    # --------------------------------------------------------
    # Drop indexes
    # --------------------------------------------------------

    op.drop_index(
        "ix_challenge_reviews_decision",
        table_name="challenge_reviews",
    )

    op.drop_index(
        "ix_challenge_reviews_reviewer_id",
        table_name="challenge_reviews",
    )

    op.drop_index(
        "ix_challenge_reviews_challenge_id",
        table_name="challenge_reviews",
    )

    # --------------------------------------------------------
    # Drop table
    # --------------------------------------------------------

    op.drop_table(
        "challenge_reviews",
    )

    # --------------------------------------------------------
    # Drop enum if it exists.
    # --------------------------------------------------------

    review_decision_enum = postgresql.ENUM(
        "ACCEPT_RECOMMENDATION",
        "OVERRIDE_AUTHORITY",
        name="reviewdecision",
    )

    review_decision_enum.drop(
        op.get_bind(),
        checkfirst=True,
    )