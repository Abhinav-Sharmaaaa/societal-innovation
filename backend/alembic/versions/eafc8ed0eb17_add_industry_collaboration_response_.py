"""add industry collaboration response deadline

Revision ID: eafc8ed0eb17
Revises: 02c2a7636688
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op


revision: str = "eafc8ed0eb17"

down_revision: Union[str, Sequence[str], None] = "02c2a7636688"

branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "industry_collaboration_proposals",
        sa.Column(
            "response_deadline",
            sa.DateTime(timezone=True),
            nullable=True,
        ),
    )


def downgrade() -> None:
    op.drop_column(
        "industry_collaboration_proposals",
        "response_deadline",
    )