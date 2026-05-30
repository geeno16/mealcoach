from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.user.model import User
from src.user.schema import UserWrite


class UserRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, auth_id: int) -> User | None:
        result = await self.session.execute(
            select(User).where(User.auth_id == auth_id)
        )
        return result.scalar_one_or_none()

    async def create(self, data: UserWrite) -> User:
        user = User(**data.model_dump())
        self.session.add(user)

        await self.session.commit()
        await self.session.refresh(user)

        return user

    async def update_by_id(
        self, auth_id: int, data: UserWrite
    ) -> User | None:
        user = await self.get_by_id(auth_id)

        if not user:
            return None

        user.role = data.role
        user.name = data.name
        user.surname = data.surname
        user.age = data.age
        user.weight = data.weight
        user.height = data.height
        user.coach_id = data.coach_id
        user.picture_id = data.picture_id

        await self.session.commit()
        await self.session.refresh(user)

        return user

    async def delete_by_id(self, auth_id: int) -> bool:
        user = await self.get_by_id(auth_id)

        if not user:
            return False

        await self.session.delete(user)
        await self.session.commit()

        return True
