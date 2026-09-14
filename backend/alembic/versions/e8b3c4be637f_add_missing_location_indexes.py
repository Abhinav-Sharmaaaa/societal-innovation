"""add missing location indexes

Revision ID: e8b3c4be637f
Revises: b336934e4b0f
"""

from typing import Sequence, Union

from alembic import op


revision: str = "e8b3c4be637f"

down_revision: Union[str, Sequence[str], None] = (
    "b336934e4b0f"
)

branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_index(
        "ix_challenges_locality",
        "challenges",
        ["locality"],
        unique=False,
    )

    op.create_index(
        "ix_challenges_location_source",
        "challenges",
        ["location_source"],
        unique=False,
    )

    op.create_index(
        "ix_organizations_locality",
        "organizations",
        ["locality"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(
        "ix_organizations_locality",
        table_name="organizations",
    )

    op.drop_index(
        "ix_challenges_location_source",
        table_name="challenges",
    )

    op.drop_index(
        "ix_challenges_locality",
        table_name="challenges",
    )