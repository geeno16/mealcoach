from typing import Annotated

from fastapi import Depends

from src.common.database import SessionDependency
from src.notification.service import NotificationService


async def get_notification_service(
    session: SessionDependency,
) -> NotificationService:
    return NotificationService(session)


NotificationServiceDependency = Annotated[
    NotificationService, Depends(get_notification_service)
]
