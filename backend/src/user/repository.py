from sqlalchemy import select

from src.common import BaseRepository
from src.user.model import User
from src.user.schema import UserWrite


class UserRepository(BaseRepository[User, UserWrite]):
    model = User

    async def create(self, data: UserWrite) -> User:
        user = User(**data.model_dump(exclude={"coach_email"}))
        self.session.add(user)
        await self.session.commit()
        await self.session.refresh(user)
        return user

    async def get_by_picture_id(self, picture_id: int) -> User | None:
        result = await self.session.execute(
            select(User).where(User.picture_id == picture_id)
        )
        return result.scalar_one_or_none()

    async def get_all_by_coach_id(self, coach_id: int) -> list[User]:
        result = await self.session.execute(
            select(User).where(User.coach_id == coach_id)
        )
        return list(result.scalars().all())

    async def get_all_by_coach_request_id(
        self, coach_id: int
    ) -> list[User]:
        result = await self.session.execute(
            select(User).where(User.coach_request_id == coach_id)
        )
        return list(result.scalars().all())

    async def update_by_id(
        self,
        id: int,
        data: UserWrite,
        exclude: set[str] | None = None,
        refresh_fields: list[str] | None = None,
    ) -> User | None:
        base_exclude = {
            "auth_id",
            "coach_email",
            "coach_id",
            "coach_request_id",
            "role",
        }
        return await super().update_by_id(
            id,
            data,
            exclude=(exclude or set()) | base_exclude,
            refresh_fields=refresh_fields,
        )
