from fastapi import APIRouter

from src.auth.dependency import CurrentAuthDependency
from src.notification.dependency import NotificationServiceDependency
from src.notification.schema import NotificationRead

notification_router = APIRouter(
    prefix="/api/notifications", tags=["Notifications"]
)


@notification_router.get("", response_model=list[NotificationRead])
async def get_notifications_get(
    service: NotificationServiceDependency,
    current: CurrentAuthDependency,
) -> list[NotificationRead]:
    return await service.get_notifications_get(current)
