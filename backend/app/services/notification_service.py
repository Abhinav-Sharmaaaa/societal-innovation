from datetime import datetime, timezone

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.notification import (
    Notification,
    NotificationPriority,
    NotificationType,
)
from app.models.project import Project
from app.models.project_risk import (
    ProjectRisk,
    ProjectRiskLevel,
)
from app.models.user import User, UserRole


GOVERNMENT_ROLES = {
    UserRole.SUPER_ADMIN,
    UserRole.GOVERNMENT_OFFICER,
    UserRole.MUNICIPALITY_OFFICER,
}


def create_notification(
    db: Session,
    user_id: int,
    title: str,
    message: str,
    notification_type: NotificationType,
    priority: NotificationPriority,
    project_id: int | None = None,
) -> Notification:

    notification = Notification(
        user_id=user_id,
        project_id=project_id,
        notification_type=notification_type,
        priority=priority,
        title=title,
        message=message,
        is_read=False,
    )

    db.add(notification)
    db.commit()
    db.refresh(notification)

    return notification


def notify_government_of_risk(
    db: Session,
    project: Project,
    risk: ProjectRisk,
) -> list[Notification]:

    notifications: list[Notification] = []

    priority_map = {
        ProjectRiskLevel.LOW: NotificationPriority.LOW,
        ProjectRiskLevel.MEDIUM: NotificationPriority.MEDIUM,
        ProjectRiskLevel.HIGH: NotificationPriority.HIGH,
        ProjectRiskLevel.CRITICAL: NotificationPriority.CRITICAL,
    }

    priority = priority_map[risk.risk_level]

    if risk.risk_level == ProjectRiskLevel.LOW:
        return notifications

    government_users = (
        db.query(User)
        .filter(
            User.role.in_(GOVERNMENT_ROLES),
            User.is_active.is_(True),
        )
        .all()
    )

    for user in government_users:

        # -----------------------------------------------------
        # Prevent duplicate unread risk notification
        # -----------------------------------------------------
        existing_notification = (
            db.query(Notification)
            .filter(
                Notification.user_id == user.id,
                Notification.project_id == project.id,
                Notification.notification_type
                == NotificationType.RISK_ALERT,
                Notification.priority == priority,
                Notification.is_read.is_(False),
            )
            .first()
        )

        if existing_notification:
            continue

        notification = Notification(
            user_id=user.id,
            project_id=project.id,
            notification_type=NotificationType.RISK_ALERT,
            priority=priority,
            title=(
                f"{risk.risk_level.value} risk detected "
                f"for project #{project.id}"
            ),
            message=(
                f"{risk.description}\n\n"
                f"Risk score: {risk.risk_score}\n\n"
                f"Detected factors:\n"
                f"{risk.detected_factors or 'None'}\n\n"
                f"Recommended action:\n"
                f"{risk.recommended_action or 'Review project status.'}"
            ),
            is_read=False,
        )

        db.add(notification)
        notifications.append(notification)

    db.commit()

    for notification in notifications:
        db.refresh(notification)

    return notifications


def list_user_notifications(
    db: Session,
    current_user: User,
) -> list[Notification]:

    return (
        db.query(Notification)
        .filter(
            Notification.user_id == current_user.id
        )
        .order_by(
            Notification.created_at.desc()
        )
        .all()
    )


def mark_notification_read(
    db: Session,
    notification_id: int,
    current_user: User,
) -> Notification:

    notification = (
        db.query(Notification)
        .filter(
            Notification.id == notification_id
        )
        .first()
    )

    if not notification:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification not found.",
        )

    if notification.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=(
                "You are not authorized to modify "
                "this notification."
            ),
        )

    notification.is_read = True
    notification.read_at = datetime.now(
        timezone.utc
    )

    db.commit()
    db.refresh(notification)

    return notification