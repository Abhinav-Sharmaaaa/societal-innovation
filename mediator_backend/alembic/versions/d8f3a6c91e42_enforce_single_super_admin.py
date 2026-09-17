"""enforce single super admin

Revision ID: d8f3a6c91e42
Revises: c4e7b8129d31
Create Date: 2026-09-13 02:30:00.000000
"""

from typing import Sequence, Union

from alembic import op


revision: str = "d8f3a6c91e42"

down_revision: Union[str, Sequence[str], None] = (
    "c4e7b8129d31"
)

branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        """
        CREATE UNIQUE INDEX IF NOT EXISTS
        uq_users_single_super_admin
        ON users ((1))
        WHERE role = 'SUPER_ADMIN'
        """
    )


def downgrade() -> None:
    op.execute(
        """
        DROP INDEX IF EXISTS
        uq_users_single_super_admin
        """
    )