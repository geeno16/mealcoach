from src.common import BaseRepository
from src.user.model import User
from src.user.schema import UserWrite


class UserRepository(BaseRepository[User, UserWrite]):
    model = User

    async def update_by_id(
        self, id: int, data: UserWrite
    ) -> User | None:
        user = await self.get_by_id(id)

        if not user:
            return None

        for key, value in data.model_dump(exclude={"auth_id"}).items():
            setattr(user, key, value)

        await self.session.commit()
        await self.session.refresh(user)

        return user
