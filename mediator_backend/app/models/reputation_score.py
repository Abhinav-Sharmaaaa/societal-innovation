from enum import Enum

from sqlalchemy import (
    Column,
    DateTime,
    Enum as SQLEnum,
    ForeignKey,
    Integer,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.database import Base


class ReputationScoreEntityType(str, Enum):
    CITIZEN = "CITIZEN"
    UNIVERSITY = "UNIVERSITY"
    INDUSTRY = "INDUSTRY"


class ReputationScore(Base):
    __tablename__ = "reputation_scores"

    id = Column(
        Integer,
        primary_key=True,
        index=True,
    )

    entity_type = Column(
        SQLEnum(
            ReputationScoreEntityType,
            name="reputationscoreentitytype",
        ),
        nullable=False,
    )

    user_id = Column(
        Integer,
        ForeignKey(
            "users.id",
            ondelete="CASCADE",
        ),
        nullable=True,
    )

    organization_id = Column(
        Integer,
        ForeignKey(
            "organizations.id",
            ondelete="CASCADE",
        ),
        nullable=True,
    )

    total_points = Column(
        Integer,
        nullable=False,
        default=0,
    )

    contribution_count = Column(
        Integer,
        nullable=False,
        default=0,
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

    user = relationship(
        "User",
    )

    organization = relationship(
        "Organization",
    )

    __table_args__ = (
        UniqueConstraint(
            "entity_type",
            "user_id",
            "organization_id",
            name="uq_reputation_score_entity",
        ),
    )