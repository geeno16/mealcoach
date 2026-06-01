from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.schema import CurrentAuth
from src.user.model import UserRole
from src.user.repository import UserRepository
from src.user.schema import UserRead, UserWrite


class UserService:
    def __init__(self, session: AsyncSession):
        self.repo = UserRepository(session)

    async def _assert_access(
        self, auth_id: int, current: CurrentAuth
    ) -> None:
        if auth_id == current.id:
            return

        current_user = await self.repo.get_by_id(current.id)

        if not current_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Current user not found",
            )

        if current_user.role == UserRole.trainee:
            if current_user.coach_id != auth_id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Trainee can only view themselves or their coach",
                )
        elif current_user.role == UserRole.coach:
            target = await self.repo.get_by_id(auth_id)
            if not target or target.coach_id != current.id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Coach can only view themselves or their trainees",
                )

    async def get_user_get(
        self, auth_id: int, current: CurrentAuth
    ) -> UserRead:
        await self._assert_access(auth_id, current)

        user = await self.repo.get_by_id(auth_id)

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found",
            )

        return UserRead.model_validate(user)

    async def create_user_post(
        self, data: UserWrite, current: CurrentAuth
    ) -> UserRead:
        if data.auth_id != current.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can create a profile only for yourself",
            )

        existing = await self.repo.get_by_id(data.auth_id)

        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"User with auth_id={data.auth_id} already exists",
            )

        user = await self.repo.create(data)
        return UserRead.model_validate(user)

    async def get_trainees_get(
        self, coach_id: int, current: CurrentAuth
    ) -> list[UserRead]:
        if coach_id != current.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only view your own trainees",
            )

        current_user = await self.repo.get_by_id(current.id)

        if not current_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found",
            )

        if current_user.role != UserRole.coach:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only coaches can view their trainees",
            )

        trainees = await self.repo.get_all_by_coach_id(coach_id)
        return [UserRead.model_validate(t) for t in trainees]

    async def update_user_put(
        self, auth_id: int, data: UserWrite, current: CurrentAuth
    ) -> UserRead:
        if auth_id != current.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can update only yourself",
            )

        user = await self.repo.update_by_id(auth_id, data)

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found",
            )

        return UserRead.model_validate(user)

