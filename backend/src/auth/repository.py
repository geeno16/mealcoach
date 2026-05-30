from sqlalchemy import select

from src.auth.model import Auth
from src.auth.schema import AuthWrite
from src.common import BaseRepository


class AuthRepository(BaseRepository[Auth, AuthWrite]):
    model = Auth

    async def get_by_email(self, email: str) -> Auth | None:
        result = await self.session.execute(
            select(Auth).where(Auth.email == email)
        )
        return result.scalar_one_or_none()

    async def verify_password(self, auth: Auth, password: str) -> bool:
        return auth.password == password
