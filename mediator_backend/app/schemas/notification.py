from datetime import datetime

from pydantic import BaseModel, ConfigDict


class NotificationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    project_id: int | None

    notification_type: str
    priority: str

    title: str
    message: str

    is_read: bool

    created_at: datetime
    read_at: datetime | None

class NotificationMarkRead(BaseModel):
    pass