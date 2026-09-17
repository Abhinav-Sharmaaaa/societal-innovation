from datetime import datetime, timezone
from enum import Enum

from sqlalchemy import (
    DateTime,
    Enum as SQLEnum,
    ForeignKey,
    Integer,
    String,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import Base


# ============================================================
# Evidence Type
# ============================================================

class EvidenceType(str, Enum):
    IMAGE = "IMAGE"
    VIDEO = "VIDEO"
    DOCUMENT = "DOCUMENT"
    OTHER = "OTHER"


# ============================================================
# Challenge Evidence Model
# ============================================================

class ChallengeEvidence(Base):
    __tablename__ = "challenge_evidence"

    # --------------------------------------------------------
    # Primary Key
    # --------------------------------------------------------

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    # --------------------------------------------------------
    # Challenge Relationship
    # --------------------------------------------------------

    challenge_id: Mapped[int] = mapped_column(
        ForeignKey(
            "challenges.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    challenge: Mapped["Challenge"] = relationship(
        "Challenge",
        back_populates="evidence",
    )

    # --------------------------------------------------------
    # File Information
    # --------------------------------------------------------

    evidence_type: Mapped[EvidenceType] = mapped_column(
        SQLEnum(EvidenceType),
        nullable=False,
        index=True,
    )

    original_filename: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    stored_filename: Mapped[str] = mapped_column(
        String(500),
        nullable=False,
        unique=True,
    )

    content_type: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    file_size: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    file_url: Mapped[str | None] = mapped_column(
        String(1000),
        nullable=True,
    )

    # --------------------------------------------------------
    # Upload Metadata
    # --------------------------------------------------------

    uploaded_by: Mapped[int] = mapped_column(
        ForeignKey(
            "users.id",
            ondelete="RESTRICT",
        ),
        nullable=False,
        index=True,
    )

    # --------------------------------------------------------
    # Timestamp
    # --------------------------------------------------------

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # --------------------------------------------------------
    # Representation
    # --------------------------------------------------------

    def __repr__(self) -> str:
        return (
            f"<ChallengeEvidence("
            f"id={self.id}, "
            f"challenge_id={self.challenge_id}, "
            f"type='{self.evidence_type}', "
            f"filename='{self.original_filename}'"
            f")>"
        )