from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.schema import CurrentAuth
from src.notification.model import Notification
from src.notification.repository import NotificationRepository
from src.notification.schema import NotificationRead
from src.post.repository import PostRepository
from src.user.repository import UserRepository


class NotificationService:
    def __init__(self, session: AsyncSession):
        self.repo = NotificationRepository(session)
        self.user_repo = UserRepository(session)
        self.post_repo = PostRepository(session)

    async def _to_read(self, item: Notification) -> NotificationRead:
        actor_name = None
        if item.actor_id is not None:
            actor = await self.user_repo.get_by_id(item.actor_id)
            actor_name = actor.name if actor else None

        post_name = None
        if item.post_id is not None:
            post = await self.post_repo.get_by_id(item.post_id)
            post_name = post.name if post else None

        return NotificationRead(
            id=item.id,
            type=item.type,
            actor_id=item.actor_id,
            actor_name=actor_name,
            post_id=item.post_id,
            post_name=post_name,
            created_at=item.created_at,
        )

    async def get_notifications_get(
        self, current: CurrentAuth
    ) -> list[NotificationRead]:
        items = await self.repo.get_all_by_recipient(current.id)
        return [await self._to_read(item) for item in items]
