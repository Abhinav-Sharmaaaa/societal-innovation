"""add project funding transactions

Revision ID: 2b22f288ca15
Revises: f40399eea8d7
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql


revision: str = "2b22f288ca15"

down_revision: Union[str, Sequence[str], None] = "f40399eea8d7"

branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ---------------------------------------------------------
    # Funding transaction type enum
    # ---------------------------------------------------------
    funding_transaction_type_enum = postgresql.ENUM(
        "ALLOCATION",
        "DISBURSEMENT",
        "UTILIZATION",
        "REFUND",
        name="fundingtransactiontype",
    )

    funding_transaction_type_enum.create(
        op.get_bind(),
        checkfirst=True,
    )

    funding_transaction_type_column_enum = postgresql.ENUM(
        "ALLOCATION",
        "DISBURSEMENT",
        "UTILIZATION",
        "REFUND",
        name="fundingtransactiontype",
        create_type=False,
    )

    # ---------------------------------------------------------
    # Funding transaction status enum
    # ---------------------------------------------------------
    funding_transaction_status_enum = postgresql.ENUM(
        "PENDING",
        "APPROVED",
        "COMPLETED",
        "REJECTED",
        name="fundingtransactionstatus",
    )

    funding_transaction_status_enum.create(
        op.get_bind(),
        checkfirst=True,
    )

    funding_transaction_status_column_enum = postgresql.ENUM(
        "PENDING",
        "APPROVED",
        "COMPLETED",
        "REJECTED",
        name="fundingtransactionstatus",
        create_type=False,
    )

    # ---------------------------------------------------------
    # Create project funding transactions table
    # ---------------------------------------------------------
    op.create_table(
        "project_funding_transactions",

        sa.Column(
            "id",
            sa.Integer(),
            autoincrement=True,
            nullable=False,
        ),

        sa.Column(
            "project_id",
            sa.Integer(),
            nullable=False,
        ),

        sa.Column(
            "transaction_type",
            funding_transaction_type_column_enum,
            nullable=False,
        ),

        sa.Column(
            "status",
            funding_transaction_status_column_enum,
            nullable=False,
        ),

        sa.Column(
            "amount",
            sa.Float(),
            nullable=False,
        ),

        sa.Column(
            "transaction_date",
            sa.DateTime(timezone=True),
            nullable=True,
        ),

        sa.Column(
            "description",
            sa.Text(),
            nullable=True,
        ),

        sa.Column(
            "reference_number",
            sa.String(length=255),
            nullable=True,
        ),

        sa.Column(
            "created_by",
            sa.Integer(),
            nullable=False,
        ),

        sa.Column(
            "approved_by",
            sa.Integer(),
            nullable=True,
        ),

        sa.Column(
            "approved_at",
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
            ["project_id"],
            ["projects.id"],
            ondelete="CASCADE",
        ),

        sa.ForeignKeyConstraint(
            ["created_by"],
            ["users.id"],
            ondelete="RESTRICT",
        ),

        sa.ForeignKeyConstraint(
            ["approved_by"],
            ["users.id"],
            ondelete="RESTRICT",
        ),

        sa.PrimaryKeyConstraint("id"),
    )

    # ---------------------------------------------------------
    # Indexes
    # ---------------------------------------------------------

    op.create_index(
        "ix_project_funding_transactions_id",
        "project_funding_transactions",
        ["id"],
        unique=False,
    )

    op.create_index(
        "ix_project_funding_transactions_project_id",
        "project_funding_transactions",
        ["project_id"],
        unique=False,
    )

    op.create_index(
        "ix_project_funding_transactions_created_by",
        "project_funding_transactions",
        ["created_by"],
        unique=False,
    )

    op.create_index(
        "ix_project_funding_transactions_status",
        "project_funding_transactions",
        ["status"],
        unique=False,
    )

    op.create_index(
        "ix_project_funding_transactions_transaction_type",
        "project_funding_transactions",
        ["transaction_type"],
        unique=False,
    )


def downgrade() -> None:
    # ---------------------------------------------------------
    # Drop indexes
    # ---------------------------------------------------------

    op.drop_index(
        "ix_project_funding_transactions_transaction_type",
        table_name="project_funding_transactions",
    )

    op.drop_index(
        "ix_project_funding_transactions_status",
        table_name="project_funding_transactions",
    )

    op.drop_index(
        "ix_project_funding_transactions_created_by",
        table_name="project_funding_transactions",
    )

    op.drop_index(
        "ix_project_funding_transactions_project_id",
        table_name="project_funding_transactions",
    )

    op.drop_index(
        "ix_project_funding_transactions_id",
        table_name="project_funding_transactions",
    )

    # ---------------------------------------------------------
    # Drop table
    # ---------------------------------------------------------

    op.drop_table(
        "project_funding_transactions",
    )

    # ---------------------------------------------------------
    # Drop enums
    # ---------------------------------------------------------

    funding_transaction_status_enum = postgresql.ENUM(
        "PENDING",
        "APPROVED",
        "COMPLETED",
        "REJECTED",
        name="fundingtransactionstatus",
    )

    funding_transaction_status_enum.drop(
        op.get_bind(),
        checkfirst=True,
    )

    funding_transaction_type_enum = postgresql.ENUM(
        "ALLOCATION",
        "DISBURSEMENT",
        "UTILIZATION",
        "REFUND",
        name="fundingtransactiontype",
    )

    funding_transaction_type_enum.drop(
        op.get_bind(),
        checkfirst=True,
    )