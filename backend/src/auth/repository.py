from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.model import Auth
from src.auth.schema import AuthWrite


class AuthRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, id: int) -> Auth | None:
        result = await self.session.execute(
            select(Auth).where(Auth.id == id)
        )
        return result.scalar_one_or_none()

    async def get_by_email(self, email: str) -> Auth | None:
        result = await self.session.execute(
            select(Auth).where(Auth.email == email)
        )
        return result.scalar_one_or_none()

    async def create(self, data: AuthWrite) -> Auth:
        auth = Auth(**data.model_dump())
        self.session.add(auth)

        await self.session.commit()
        await self.session.refresh(auth)

        return auth

    async def update_by_id(
        self, id: int, data: AuthWrite
    ) -> Auth | None:
        auth = await self.get_by_id(id)

        if not auth:
            return None

        auth.email = data.email
        auth.password = data.password

        await self.session.commit()
        await self.session.refresh(auth)

        return auth

    async def verify_password(self, auth: Auth, password: str) -> bool:
        return auth.password == password

    async def delete_by_id(self, id: int) -> bool:
        auth = await self.get_by_id(id)

        if not auth:
            return False

        await self.session.delete(auth)
        await self.session.commit()

        return True
