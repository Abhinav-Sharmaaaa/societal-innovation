from enum import Enum

from sqlalchemy import (
    Column,
    DateTime,
    Enum as SQLEnum,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.database import Base


class FundingTransactionType(str, Enum):
    ALLOCATION = "ALLOCATION"
    DISBURSEMENT = "DISBURSEMENT"
    UTILIZATION = "UTILIZATION"
    REFUND = "REFUND"


class FundingTransactionStatus(str, Enum):
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    COMPLETED = "COMPLETED"
    REJECTED = "REJECTED"


class ProjectFundingTransaction(Base):
    __tablename__ = "project_funding_transactions"
    
    

    id = Column(
        Integer,
        primary_key=True,
        index=True,
    )

    project_id = Column(
        Integer,
        ForeignKey(
            "projects.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    transaction_type = Column(
        SQLEnum(
            FundingTransactionType,
            name="fundingtransactiontype",
        ),
        nullable=False,
    )

    status = Column(
        SQLEnum(
            FundingTransactionStatus,
            name="fundingtransactionstatus",
        ),
        nullable=False,
        default=FundingTransactionStatus.PENDING,
    )

    amount = Column(
        Float,
        nullable=False,
    )

    transaction_date = Column(
        DateTime(timezone=True),
        nullable=True,
    )

    description = Column(
        Text,
        nullable=True,
    )

    reference_number = Column(
        String(255),
        nullable=True,
    )

    created_by = Column(
        Integer,
        ForeignKey(
            "users.id",
            ondelete="RESTRICT",
        ),
        nullable=False,
        index=True,
    )

    approved_by = Column(
        Integer,
        ForeignKey(
            "users.id",
            ondelete="RESTRICT",
        ),
        nullable=True,
    )

    approved_at = Column(
        DateTime(timezone=True),
        nullable=True,
    )

    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    updated_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    project = relationship(
        "Project",
        back_populates="funding_transactions",
    )

    creator = relationship(
        "User",
        foreign_keys=[created_by],
    )

    approver = relationship(
        "User",
        foreign_keys=[approved_by],
    )
    
    __table_args__ = (
        Index(
            "ix_project_funding_transactions_status",
            "status",
        ),
        Index(
            "ix_project_funding_transactions_transaction_type",
            "transaction_type",
        ),
    )