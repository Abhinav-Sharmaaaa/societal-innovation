"""add review officer role

Revision ID: b6c2a91f4e73
Revises: a17f4b92d8c1
Create Date: 2026-09-13 01:25:00.000000
"""

from typing import Sequence, Union

from alembic import op


revision: str = "b6c2a91f4e73"

down_revision: Union[str, Sequence[str], None] = (
    "a17f4b92d8c1"
)

branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        """
        ALTER TYPE userrole
        ADD VALUE IF NOT EXISTS 'REVIEW_OFFICER'
        """
    )


def downgrade() -> None:
    # PostgreSQL does not safely support removing an enum
    # value with a simple ALTER TYPE statement.
    #
    # The role value should therefore remain in the enum
    # during downgrade.
    pass