"""add challenge location resolution metadata

Revision ID: 36154f2d98f8
Revises: eeb2ef8c4a89
Create Date: 2026-09-12 12:42:57.916399

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '36154f2d98f8'
down_revision: Union[str, Sequence[str], None] = 'eeb2ef8c4a89'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    location_source_enum = sa.Enum(
        "MANUAL",
        "GPS",
        "GPS_VERIFIED_MANUAL",
        "CONFLICT",
        name="challengelocationsource",
    )

    location_source_enum.create(op.get_bind(), checkfirst=True)

    op.add_column(
        "challenges",
        sa.Column(
            "location_source",
            location_source_enum,
            nullable=False,
            server_default="MANUAL",
        ),
    )

    op.add_column(
        "challenges",
        sa.Column(
            "location_verified",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("false"),
        ),
    )

    op.add_column(
        "challenges",
        sa.Column(
            "location_accuracy_meters",
            sa.Float(),
            nullable=True,
        ),
    )

    op.add_column(
        "challenges",
        sa.Column(
            "locality",
            sa.String(length=255),
            nullable=True,
        ),
    )

    op.add_column(
        "challenges",
        sa.Column(
            "location_resolution_reason",
            sa.Text(),
            nullable=True,
        ),
    )

    op.add_column(
        "challenges",
        sa.Column(
            "location_resolved_at",
            sa.DateTime(timezone=True),
            nullable=True,
        ),
    )

    organization_location_source_enum = None

    op.add_column(
        "organizations",
        sa.Column(
            "locality",
            sa.String(length=255),
            nullable=True,
        ),
    )

    op.alter_column(
        "challenges",
        "location_source",
        server_default=None,
    )

    op.alter_column(
        "challenges",
        "location_verified",
        server_default=None,
    )

def downgrade() -> None:
    op.drop_column("organizations", "locality")

    op.drop_column("challenges", "location_resolved_at")
    op.drop_column("challenges", "location_resolution_reason")
    op.drop_column("challenges", "locality")
    op.drop_column("challenges", "location_accuracy_meters")
    op.drop_column("challenges", "location_verified")
    op.drop_column("challenges", "location_source")

    sa.Enum(
        "MANUAL",
        "GPS",
        "GPS_VERIFIED_MANUAL",
        "CONFLICT",
        name="challengelocationsource",
    ).drop(op.get_bind(), checkfirst=True)