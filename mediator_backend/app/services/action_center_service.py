from sqlalchemy.orm import Session

from app.models.notification import (
    Notification,
    NotificationPriority,
    NotificationType,
)
from app.models.user import User


def get_action_center(
    db: Session,
    current_user: User,
) -> dict:

    notifications = (
        db.query(Notification)
        .filter(
            Notification.user_id == current_user.id,
        )
        .order_by(
            Notification.is_read.asc(),
            Notification.created_at.desc(),
        )
        .limit(50)
        .all()
    )

    unread = [
        notification
        for notification in notifications
        if not notification.is_read
    ]

    critical = [
        notification
        for notification in unread
        if notification.priority
        == NotificationPriority.CRITICAL
    ]

    high = [
        notification
        for notification in unread
        if notification.priority
        == NotificationPriority.HIGH
    ]

    medium = [
        notification
        for notification in unread
        if notification.priority
        == NotificationPriority.MEDIUM
    ]

    low = [
        notification
        for notification in unread
        if notification.priority
        == NotificationPriority.LOW
    ]

    notification_data = []

    for notification in notifications:
        notification_data.append(
            {
                "id": notification.id,
                "type": (
                    notification.notification_type.value
                    if hasattr(
                        notification.notification_type,
                        "value",
                    )
                    else str(
                        notification.notification_type
                    )
                ),
                "priority": (
                    notification.priority.value
                    if hasattr(
                        notification.priority,
                        "value",
                    )
                    else str(
                        notification.priority
                    )
                ),
                "title": notification.title,
                "message": notification.message,
                "project_id": notification.project_id,
                "is_read": notification.is_read,
                "created_at": notification.created_at,
                "read_at": notification.read_at,
            }
        )

    return {
        "summary": {
            "total": len(notifications),
            "unread": len(unread),
            "critical": len(critical),
            "high": len(high),
            "medium": len(medium),
            "low": len(low),
        },
        "notifications": notification_data,
    }