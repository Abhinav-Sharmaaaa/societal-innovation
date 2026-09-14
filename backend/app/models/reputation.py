from enum import Enum

from sqlalchemy import (
    Column,
    DateTime,
    Enum as SQLEnum,
    ForeignKey,
    Integer,
    Text,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.database import Base


class ReputationEntityType(str, Enum):
    CITIZEN = "CITIZEN"
    UNIVERSITY = "UNIVERSITY"
    INDUSTRY = "INDUSTRY"


class ReputationEventType(str, Enum):
    CHALLENGE_SUBMITTED = "CHALLENGE_SUBMITTED"
    CHALLENGE_VALIDATED = "CHALLENGE_VALIDATED"
    UNIVERSITY_PROPOSAL = "UNIVERSITY_PROPOSAL"
    PROJECT_CONTRIBUTION = "PROJECT_CONTRIBUTION"
    MILESTONE_COMPLETED = "MILESTONE_COMPLETED"
    DELIVERABLE_APPROVED = "DELIVERABLE_APPROVED"
    FUNDING_CONTRIBUTION = "FUNDING_CONTRIBUTION"
    PROJECT_COMPLETED = "PROJECT_COMPLETED"
    POSITIVE_PROJECT_OUTCOME = "POSITIVE_PROJECT_OUTCOME"


class ReputationEvent(Base):
    __tablename__ = "reputation_events"

    id = Column(
        Integer,
        primary_key=True,
        index=True,
    )

    entity_type = Column(
        SQLEnum(
            ReputationEntityType,
            name="reputationentitytype",
        ),
        nullable=False,
        index=True,
    )

    user_id = Column(
        Integer,
        ForeignKey(
            "users.id",
            ondelete="CASCADE",
        ),
        nullable=True,
        index=True,
    )

    organization_id = Column(
        Integer,
        ForeignKey(
            "organizations.id",
            ondelete="CASCADE",
        ),
        nullable=True,
        index=True,
    )

    event_type = Column(
        SQLEnum(
            ReputationEventType,
            name="reputationeventtype",
        ),
        nullable=False,
        index=True,
    )

    points = Column(
        Integer,
        nullable=False,
    )

    description = Column(
        Text,
        nullable=True,
    )

    project_id = Column(
        Integer,
        ForeignKey(
            "projects.id",
            ondelete="SET NULL",
        ),
        nullable=True,
        index=True,
    )

    created_at = Column(
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

    project = relationship(
        "Project",
    )