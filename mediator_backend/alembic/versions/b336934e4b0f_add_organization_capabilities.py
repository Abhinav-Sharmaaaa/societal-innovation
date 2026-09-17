"""add organization capabilities

Revision ID: b336934e4b0f
Revises: d8f3a6c91e42
Create Date: 2026-09-13
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql


revision: str = "b336934e4b0f"

down_revision: Union[str, Sequence[str], None] = "d8f3a6c91e42"

branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    capability_type_enum = postgresql.ENUM(
        "UNIVERSITY_DISCIPLINE",
        "UNIVERSITY_RESEARCH_AREA",
        "UNIVERSITY_LAB",
        "UNIVERSITY_EXPERTISE",
        "INDUSTRY_TECHNOLOGY",
        "INDUSTRY_SERVICE",
        "INDUSTRY_MANUFACTURING",
        "INDUSTRY_FUNDING",
        "INDUSTRY_DEPLOYMENT",
        "INDUSTRY_MENTORSHIP",
        name="capabilitytype",
    )

    capability_type_enum.create(
        op.get_bind(),
        checkfirst=True,
    )

    capability_type_column_enum = postgresql.ENUM(
        "UNIVERSITY_DISCIPLINE",
        "UNIVERSITY_RESEARCH_AREA",
        "UNIVERSITY_LAB",
        "UNIVERSITY_EXPERTISE",
        "INDUSTRY_TECHNOLOGY",
        "INDUSTRY_SERVICE",
        "INDUSTRY_MANUFACTURING",
        "INDUSTRY_FUNDING",
        "INDUSTRY_DEPLOYMENT",
        "INDUSTRY_MENTORSHIP",
        name="capabilitytype",
        create_type=False,
    )

    op.create_table(
        "organization_capabilities",
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
            "capability_type",
            capability_type_column_enum,
            nullable=False,
        ),
        sa.Column(
            "name",
            sa.String(length=255),
            nullable=False,
        ),
        sa.Column(
            "description",
            sa.Text(),
            nullable=True,
        ),
        sa.ForeignKeyConstraint(
            ["organization_id"],
            ["organizations.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_index(
        "ix_organization_capabilities_organization_id",
        "organization_capabilities",
        ["organization_id"],
        unique=False,
    )

    op.create_index(
        "ix_organization_capabilities_capability_type",
        "organization_capabilities",
        ["capability_type"],
        unique=False,
    )

    op.create_index(
        "ix_organization_capabilities_name",
        "organization_capabilities",
        ["name"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(
        "ix_organization_capabilities_name",
        table_name="organization_capabilities",
    )

    op.drop_index(
        "ix_organization_capabilities_capability_type",
        table_name="organization_capabilities",
    )

    op.drop_index(
        "ix_organization_capabilities_organization_id",
        table_name="organization_capabilities",
    )

    op.drop_table(
        "organization_capabilities",
    )

    capability_type_enum = postgresql.ENUM(
        "UNIVERSITY_DISCIPLINE",
        "UNIVERSITY_RESEARCH_AREA",
        "UNIVERSITY_LAB",
        "UNIVERSITY_EXPERTISE",
        "INDUSTRY_TECHNOLOGY",
        "INDUSTRY_SERVICE",
        "INDUSTRY_MANUFACTURING",
        "INDUSTRY_FUNDING",
        "INDUSTRY_DEPLOYMENT",
        "INDUSTRY_MENTORSHIP",
        name="capabilitytype",
    )

    capability_type_enum.drop(
        op.get_bind(),
        checkfirst=True,
    )