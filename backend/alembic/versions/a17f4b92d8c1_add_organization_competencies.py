"""add organization competencies

Revision ID: a17f4b92d8c1
Revises: 36154f2d98f8
Create Date: 2026-09-12 23:20:00.000000
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision: str = "a17f4b92d8c1"
down_revision: Union[str, Sequence[str], None] = (
    "36154f2d98f8"
)
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    challenge_category_enum = postgresql.ENUM(
        "WATER",
        "SANITATION",
        "WASTE_MANAGEMENT",
        "HEALTHCARE",
        "EDUCATION",
        "AGRICULTURE",
        "TRANSPORTATION",
        "ENERGY",
        "ENVIRONMENT",
        "PUBLIC_SAFETY",
        "INFRASTRUCTURE",
        "DIGITAL_SERVICES",
        "EMPLOYMENT",
        "SOCIAL_WELFARE",
        "DISASTER_MANAGEMENT",
        "OTHER",
        name="challengecategory",
        create_type=False,
    )

    op.create_table(
        "organization_competencies",
        sa.Column(
            "id",
            sa.Integer(),
            autoincrement=True,
            nullable=False,
        ),
        sa.Column(
            "organization_id",
            sa.Integer(),
            nullable=False,
        ),
        sa.Column(
            "category",
            challenge_category_enum,
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["organization_id"],
            ["organizations.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "organization_id",
            "category",
            name="uq_organization_competency",
        ),
    )

    op.create_index(
        "ix_organization_competencies_organization_id",
        "organization_competencies",
        ["organization_id"],
        unique=False,
    )

    op.create_index(
        "ix_organization_competencies_category",
        "organization_competencies",
        ["category"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(
        "ix_organization_competencies_category",
        table_name="organization_competencies",
    )

    op.drop_index(
        "ix_organization_competencies_organization_id",
        table_name="organization_competencies",
    )

    op.drop_table(
        "organization_competencies",
    )