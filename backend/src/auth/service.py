from fastapi import HTTPException, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.repository import AuthRepository
from src.auth.schema import AuthRead, AuthWrite, CurrentAuth
from src.auth.token import create_access_token


class AuthService:
    def __init__(self, session: AsyncSession):
        self.repo = AuthRepository(session)

    async def register_post(self, data: AuthWrite) -> int:
        if await self.__email_exists(data.email):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"User with email={data.email} already exists",
            )

        try:
            id = await self.repo.create(data)
        except AttributeError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)
            ) from e

        return id

    async def login_post(
        self, data: AuthWrite, response: Response
    ) -> AuthRead:
        valid = True
        if not await self.__email_exists(data.email):
            valid = False

        auth = await self.repo.get_by_email(data.email)
        if not await self.repo.verify_password(auth.id, data.password):
            valid = False

        if not valid:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect login or password",
            )

        token = create_access_token({"user_id": auth.id})
        response.set_cookie(
            key="access_token",
            value=token,
            httponly=True,
            path="/",
            samesite="lax",
        )

        return auth

    async def logout_post(self, response: Response) -> dict:
        response.delete_cookie(
            key="access_token",
            path="/",
            samesite="lax",
        )
        return {"message": "Logged out"}

    async def update_auth_put(
        self, id: int, data: AuthWrite, current: CurrentAuth
    ) -> AuthRead:
        if id != current.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can update only youself",
            )

        try:
            auth = await self.repo.update_by_id(id, data)
        except AttributeError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)
            ) from e

        return auth

    async def __email_exists(self, email: str) -> bool:
        exists = True
        try:
            await self.repo.get_by_email(email)
        except KeyError:
            exists = False

        return exists
