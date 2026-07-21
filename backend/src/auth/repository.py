from sqlalchemy import select

from src.auth.model import Auth
from src.auth.schema import AuthWrite
from src.common import BaseRepository, hash_secret, verify_secret


class AuthRepository(BaseRepository[Auth, AuthWrite]):
    model = Auth

    async def create(self, data: AuthWrite) -> Auth:
        return await super().create(self._with_hashed_password(data))

    async def update_by_id(
        self,
        id: int,
        data: AuthWrite,
        exclude: set[str] | None = None,
        refresh_fields: list[str] | None = None,
    ) -> Auth | None:
        return await super().update_by_id(
            id,
            self._with_hashed_password(data),
            exclude=exclude,
            refresh_fields=refresh_fields,
        )

    def _with_hashed_password(self, data: AuthWrite) -> AuthWrite:
        return data.model_copy(
            update={"password": hash_secret(data.password)}
        )

    async def get_by_email(self, email: str) -> Auth | None:
        result = await self.session.execute(
            select(Auth).where(Auth.email == email)
        )
        return result.scalar_one_or_none()

    async def verify_password(self, auth: Auth, password: str) -> bool:
        return verify_secret(password, auth.password)
