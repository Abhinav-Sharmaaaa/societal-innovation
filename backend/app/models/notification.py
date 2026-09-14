from enum import Enum

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Enum as SQLEnum,
    ForeignKey,
    Index,
    Integer,
    Text,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.database import Base


class NotificationType(str, Enum):
    RISK_ALERT = "RISK_ALERT"
    DEADLINE_ALERT = "DEADLINE_ALERT"
    PROJECT_UPDATE = "PROJECT_UPDATE"
    MILESTONE_UPDATE = "MILESTONE_UPDATE"
    FUNDING_ALERT = "FUNDING_ALERT"


class NotificationPriority(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class Notification(Base):
    __tablename__ = "notifications"
    
    __table_args__ = (
        Index(
            "ix_notifications_created_at",
            "created_at",
        ),
    )

    id = Column(
        Integer,
        primary_key=True,
        index=True,
    )

    user_id = Column(
        Integer,
        ForeignKey(
            "users.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    project_id = Column(
        Integer,
        ForeignKey(
            "projects.id",
            ondelete="CASCADE",
        ),
        nullable=True,
        index=True,
    )

    notification_type = Column(
        SQLEnum(
            NotificationType,
            name="notificationtype",
        ),
        nullable=False,
    )

    priority = Column(
        SQLEnum(
            NotificationPriority,
            name="notificationpriority",
        ),
        nullable=False,
    )

    title = Column(
        Text,
        nullable=False,
    )

    message = Column(
        Text,
        nullable=False,
    )

    is_read = Column(
        Boolean,
        nullable=False,
        default=False,
    )

    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    read_at = Column(
        DateTime(timezone=True),
        nullable=True,
    )

    user = relationship(
        "User",
    )

    project = relationship(
        "Project",
    )