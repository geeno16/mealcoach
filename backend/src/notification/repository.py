from sqlalchemy import select

from src.common import BaseRepository
from src.notification.model import Notification, NotificationType
from src.notification.schema import NotificationWrite


class NotificationRepository(
    BaseRepository[Notification, NotificationWrite]
):
    model = Notification

    async def get_all_by_recipient(
        self, recipient_id: int
    ) -> list[Notification]:
        result = await self.session.execute(
            select(Notification)
            .where(Notification.recipient_id == recipient_id)
            .order_by(Notification.created_at.desc())
        )
        return list(result.scalars().all())

    async def get_coach_request(
        self, recipient_id: int, actor_id: int
    ) -> Notification | None:
        result = await self.session.execute(
            select(Notification).where(
                Notification.recipient_id == recipient_id,
                Notification.actor_id == actor_id,
                Notification.type == NotificationType.coach_request,
            )
        )
        return result.scalars().first()
