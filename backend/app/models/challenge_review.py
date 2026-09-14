from datetime import datetime, timezone
from enum import Enum
from typing import TYPE_CHECKING

from sqlalchemy import (
    DateTime,
    Enum as SQLEnum,
    ForeignKey,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import Base

if TYPE_CHECKING:
    from app.models.challenge import Challenge
    from app.models.organization import Organization
    from app.models.user import User


class ReviewDecision(str, Enum):
    ACCEPT_RECOMMENDATION = "ACCEPT_RECOMMENDATION"
    OVERRIDE_AUTHORITY = "OVERRIDE_AUTHORITY"


class ChallengeReview(Base):
    __tablename__ = "challenge_reviews"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True,
    )

    challenge_id: Mapped[int] = mapped_column(
        ForeignKey(
            "challenges.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    reviewer_id: Mapped[int] = mapped_column(
        ForeignKey(
            "users.id",
            ondelete="SET NULL",
        ),
        nullable=False,
        index=True,
    )

    decision: Mapped[ReviewDecision] = mapped_column(
        SQLEnum(ReviewDecision),
        nullable=False,
        index=True,
    )

    recommended_authority_id: Mapped[int | None] = mapped_column(
        ForeignKey(
            "organizations.id",
            ondelete="SET NULL",
        ),
        nullable=True,
    )

    selected_authority_id: Mapped[int] = mapped_column(
        ForeignKey(
            "organizations.id",
            ondelete="SET NULL",
        ),
        nullable=False,
    )

    reason: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    challenge: Mapped["Challenge"] = relationship(
        "Challenge",
    )

    reviewer: Mapped["User"] = relationship(
        "User",
        foreign_keys=[reviewer_id],
    )

    recommended_authority: Mapped[
        "Organization | None"
    ] = relationship(
        "Organization",
        foreign_keys=[recommended_authority_id],
    )

    selected_authority: Mapped[
        "Organization"
    ] = relationship(
        "Organization",
        foreign_keys=[selected_authority_id],
    )