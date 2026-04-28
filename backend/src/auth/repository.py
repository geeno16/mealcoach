from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.model import Auth
from src.auth.schema import AuthRead, AuthWrite


class AuthRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, id: int) -> AuthRead:
        auth = await self.__get_obj(id)
        return AuthRead.model_validate(auth)

    async def get_by_email(self, email: str) -> AuthRead:
        auth = await self.__get_obj(email)
        return AuthRead.model_validate(auth)

    async def create(self, data: AuthWrite) -> int:
        try:
            auth = Auth(**data.model_dump())
            self.session.add(auth)
            await self.session.commit()
            await self.session.refresh(auth)
        except Exception as e:
            raise AttributeError("Auth data is not valid") from e

        return auth.id

    async def update_by_id(self, id: int, data: AuthWrite) -> AuthRead:
        auth = await self.__get_obj(id)
        auth.email = data.email
        auth.password = data.password
        try:
            result_auth = AuthRead.model_validate(auth)
            await self.session.commit()
            await self.session.refresh(auth)
        except Exception as e:
            raise AttributeError("Auth data is not valid") from e

        return result_auth

    async def verify_password(self, id: int, password: str) -> bool:
        auth = await self.__get_obj(id)
        if auth.password == password:
            return True

        return False

    async def __get_obj(self, identificator: int | str) -> Auth:
        if isinstance(identificator, int):
            stmnt = Auth.id == identificator
        else:
            stmnt = Auth.email == identificator

        result = await self.session.execute(select(Auth).where(stmnt))
        auth = result.scalar_one_or_none()
        if auth is None:
            raise KeyError("Auth entity with was not found")

        return auth
