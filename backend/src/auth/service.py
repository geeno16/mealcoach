from fastapi import HTTPException, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.repository import AuthRepository
from src.auth.schema import AuthRead, AuthWrite, CurrentAuth
from src.auth.token import create_access_token


class AuthService:
    def __init__(self, session: AsyncSession):
        self.repo = AuthRepository(session)

    async def register_post(self, data: AuthWrite) -> int:
        existing = await self.repo.get_by_email(data.email)

        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"User with email={data.email} already exists",
            )

        auth = await self.repo.create(data)
        return auth.id

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

    async def logout_post(self, response: Response) -> dict:
        response.delete_cookie(
            key="access_token",
            path="/",
            samesite="lax",
        )
        return {"message": "Logged out"}

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

        deleted = await self.repo.delete_by_id(id)

        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found",
            )
