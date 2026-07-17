from datetime import datetime

from pydantic import BaseModel

from src.notification.model import NotificationType


class NotificationWrite(BaseModel):
    recipient_id: int
    type: NotificationType
    actor_id: int | None = None
    post_id: int | None = None


class NotificationRead(BaseModel):
    id: int
    type: NotificationType
    actor_id: int | None = None
    actor_name: str | None = None
    post_id: int | None = None
    post_name: str | None = None
    created_at: datetime
