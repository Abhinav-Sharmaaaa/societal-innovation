from datetime import datetime

from pydantic import BaseModel


class ActionCenterSummary(BaseModel):
    total: int
    unread: int
    critical: int
    high: int
    medium: int
    low: int


class ActionCenterNotification(BaseModel):
    id: int
    type: str
    priority: str
    title: str
    message: str
    project_id: int | None = None
    is_read: bool
    created_at: datetime
    read_at: datetime | None = None


class ActionCenterResponse(BaseModel):
    summary: ActionCenterSummary
    notifications: list[ActionCenterNotification]