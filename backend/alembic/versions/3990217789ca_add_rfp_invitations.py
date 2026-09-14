"""add rfp invitations

Revision ID: 3990217789ca
Revises: ed66d4fb8ad1
Create Date: 2026-09-13
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql


revision: str = "3990217789ca"

down_revision: Union[str, Sequence[str], None] = (
    "ed66d4fb8ad1"
)

branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # --------------------------------------------------------
    # Create RFP invitation status enum
    # --------------------------------------------------------

    invitation_status_enum = postgresql.ENUM(
        "INVITED",
        "VIEWED",
        "INTERESTED",
        "DECLINED",
        "PROPOSAL_SUBMITTED",
        "EXPIRED",
        name="rfpinvitationstatus",
    )

    invitation_status_enum.create(
        op.get_bind(),
        checkfirst=True,
    )

    invitation_status_column_enum = postgresql.ENUM(
        "INVITED",
        "VIEWED",
        "INTERESTED",
        "DECLINED",
        "PROPOSAL_SUBMITTED",
        "EXPIRED",
        name="rfpinvitationstatus",
        create_type=False,
    )

    # --------------------------------------------------------
    # Create RFP invitations table
    # --------------------------------------------------------

    op.create_table(
        "rfp_invitations",
        sa.Column(
            "id",
            sa.Integer(),
            autoincrement=True,
            nullable=False,
        ),
        sa.Column(
            "rfp_id",
            sa.Integer(),
            nullable=False,
        ),
        sa.Column(
            "university_id",
            sa.Integer(),
            nullable=False,
        ),
        sa.Column(
            "invited_by",
            sa.Integer(),
            nullable=False,
        ),
        sa.Column(
            "recommendation_rank",
            sa.Integer(),
            nullable=True,
        ),
        sa.Column(
            "match_score",
            sa.Float(),
            nullable=True,
        ),
        sa.Column(
            "status",
            invitation_status_column_enum,
            nullable=False,
        ),
        sa.Column(
            "response_reason",
            sa.Text(),
            nullable=True,
        ),
        sa.Column(
            "invited_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.Column(
            "viewed_at",
            sa.DateTime(timezone=True),
            nullable=True,
        ),
        sa.Column(
            "responded_at",
            sa.DateTime(timezone=True),
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
            ["rfp_id"],
            ["rfps.id"],
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["university_id"],
            ["organizations.id"],
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["invited_by"],
            ["users.id"],
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "rfp_id",
            "university_id",
            name="uq_rfp_invitation_university",
        ),
    )

    # --------------------------------------------------------
    # Indexes
    # --------------------------------------------------------

    op.create_index(
        "ix_rfp_invitations_rfp_id",
        "rfp_invitations",
        ["rfp_id"],
        unique=False,
    )

    op.create_index(
        "ix_rfp_invitations_university_id",
        "rfp_invitations",
        ["university_id"],
        unique=False,
    )

    op.create_index(
        "ix_rfp_invitations_invited_by",
        "rfp_invitations",
        ["invited_by"],
        unique=False,
    )

    op.create_index(
        "ix_rfp_invitations_status",
        "rfp_invitations",
        ["status"],
        unique=False,
    )


def downgrade() -> None:
    # --------------------------------------------------------
    # Drop indexes
    # --------------------------------------------------------

    op.drop_index(
        "ix_rfp_invitations_status",
        table_name="rfp_invitations",
    )

    op.drop_index(
        "ix_rfp_invitations_invited_by",
        table_name="rfp_invitations",
    )

    op.drop_index(
        "ix_rfp_invitations_university_id",
        table_name="rfp_invitations",
    )

    op.drop_index(
        "ix_rfp_invitations_rfp_id",
        table_name="rfp_invitations",
    )

    # --------------------------------------------------------
    # Drop table
    # --------------------------------------------------------

    op.drop_table("rfp_invitations")

    # --------------------------------------------------------
    # Drop enum
    # --------------------------------------------------------

    invitation_status_enum = postgresql.ENUM(
        "INVITED",
        "VIEWED",
        "INTERESTED",
        "DECLINED",
        "PROPOSAL_SUBMITTED",
        "EXPIRED",
        name="rfpinvitationstatus",
    )

    invitation_status_enum.drop(
        op.get_bind(),
        checkfirst=True,
    )