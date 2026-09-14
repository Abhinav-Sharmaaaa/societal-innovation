from datetime import datetime, timezone
from enum import Enum

from sqlalchemy import (
    DateTime,
    Enum as SQLEnum,
    ForeignKey,
    Integer,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.db.database import Base


class AssignmentAction(str, Enum):
    AUTO_ASSIGNED = "AUTO_ASSIGNED"
    HUMAN_ASSIGNED = "HUMAN_ASSIGNED"
    REASSIGNED = "REASSIGNED"
    ESCALATED = "ESCALATED"
    DELEGATED_DOWN = "DELEGATED_DOWN"
    SENT_TO_INNOVATION = "SENT_TO_INNOVATION"


class AssignmentStatus(str, Enum):
    ACTIVE = "ACTIVE"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"


class ChallengeAssignment(Base):
    __tablename__ = "challenge_assignments"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    challenge_id: Mapped[int] = mapped_column(
        ForeignKey("challenges.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    from_authority_id: Mapped[int | None] = mapped_column(
        ForeignKey("organizations.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    to_authority_id: Mapped[int] = mapped_column(
        ForeignKey("organizations.id", ondelete="SET NULL"),
        nullable=False,
        index=True,
    )

    performed_by: Mapped[int | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    action: Mapped[AssignmentAction] = mapped_column(
        SQLEnum(AssignmentAction),
        nullable=False,
        index=True,
    )

    status: Mapped[AssignmentStatus] = mapped_column(
        SQLEnum(AssignmentStatus),
        default=AssignmentStatus.ACTIVE,
        nullable=False,
        index=True,
    )

    reason: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    remarks: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    completed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )