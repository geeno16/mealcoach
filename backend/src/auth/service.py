from fastapi import HTTPException, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.repository import AuthRepository
from src.auth.schema import (
    AuthRead,
    AuthWrite,
    CurrentAuth,
    MessageResponse,
)
from src.auth.token import create_access_token


class AuthService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.repo = AuthRepository(session)

    async def register_post(self, data: AuthWrite) -> AuthRead:
        existing = await self.repo.get_by_email(data.email)

        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"User with email={data.email} already exists",
            )

        auth = await self.repo.create(data)
        return AuthRead.model_validate(auth)

    async def login_post(
        self, data: AuthWrite, response: Response
    ) -> AuthRead:
        auth = await self.repo.get_by_email(data.email)

        if not auth:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect login or password",
            )

        if not await self.repo.verify_password(auth, data.password):
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

        return AuthRead.model_validate(auth)

    async def logout_post(self, response: Response) -> MessageResponse:
        response.delete_cookie(
            key="access_token",
            path="/",
            samesite="lax",
        )
        return MessageResponse(message="Logged out")

    def _assert_owner(self, id: int, current: CurrentAuth) -> None:
        if id != current.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can modify only yourself",
            )

    async def update_auth_put(
        self, id: int, data: AuthWrite, current: CurrentAuth
    ) -> AuthRead:
        self._assert_owner(id, current)

        auth = await self.repo.update_by_id(id, data)

        if not auth:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found",
            )

        return AuthRead.model_validate(auth)

    async def delete_auth_delete(
        self, id: int, current: CurrentAuth
    ) -> None:
        self._assert_owner(id, current)

        # Imported lazily: auth is imported first at startup, so a
        # module-level import here would create a circular import.
        from src.picture.repository import PictureRepository
        from src.user.repository import UserRepository

        user = await UserRepository(self.session).get_by_id(id)
        picture_id = user.picture_id if user else None

        deleted = await self.repo.delete_by_id(id)

        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found",
            )

        if picture_id is not None:
            await PictureRepository(self.session).delete_by_id(picture_id)
