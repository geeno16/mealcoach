from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.repository import AuthRepository
from src.auth.schema import CurrentAuth
from src.notification.model import NotificationType
from src.notification.repository import NotificationRepository
from src.notification.schema import NotificationWrite
from src.user.model import User, UserRole
from src.user.repository import UserRepository
from src.user.schema import CoachRequest, UserRead, UserWrite


class UserService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.repo = UserRepository(session)
        self.auth_repo = AuthRepository(session)
        self.notif_repo = NotificationRepository(session)

    async def _assert_coach(self, current: CurrentAuth) -> None:
        coach = await self.repo.get_by_id(current.id)
        if not coach or coach.role != UserRole.coach:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only a coach can do this",
            )

    async def _get_pending_request_or_404(
        self, trainee_id: int, coach_id: int
    ) -> User:
        trainee = await self.repo.get_by_id(trainee_id)
        if not trainee or trainee.coach_request_id != coach_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Request not found",
            )
        return trainee

    async def _resolve_coach_id(self, email: str) -> int:
        coach_auth = await self.auth_repo.get_by_email(email)
        coach = (
            await self.repo.get_by_id(coach_auth.id)
            if coach_auth
            else None
        )
        if not coach or coach.role != UserRole.coach:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Coach not found",
            )
        return coach.auth_id

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

        if data.role == UserRole.trainee:
            if not data.coach_email:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Trainee must specify a coach",
                )
            coach_id = await self._resolve_coach_id(data.coach_email)
            data = data.model_copy(
                update={
                    "coach_id": None,
                    "coach_request_id": coach_id,
                }
            )
        else:
            data = data.model_copy(
                update={"coach_id": None, "coach_request_id": None}
            )

        user = await self.repo.create(data)

        if user.coach_request_id is not None:
            await self.notif_repo.create(
                NotificationWrite(
                    recipient_id=user.coach_request_id,
                    actor_id=user.auth_id,
                    type=NotificationType.coach_request,
                )
            )

        return UserRead.model_validate(user)

    async def request_coach_post(
        self, auth_id: int, data: CoachRequest, current: CurrentAuth
    ) -> UserRead:
        if auth_id != current.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can request a coach only for yourself",
            )

        user = await self.repo.get_by_id(auth_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found",
            )
        if user.role != UserRole.trainee:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only a trainee can request a coach",
            )
        if user.coach_id is not None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="You already have a coach",
            )
        if user.coach_request_id is not None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="You already have a pending request",
            )

        coach_id = await self._resolve_coach_id(data.coach_email)
        user.coach_request_id = coach_id
        await self.session.commit()
        await self.session.refresh(user)

        await self.notif_repo.create(
            NotificationWrite(
                recipient_id=coach_id,
                actor_id=user.auth_id,
                type=NotificationType.coach_request,
            )
        )

        return UserRead.model_validate(user)

    async def delete_coach_delete(
        self, trainee_id: int, current: CurrentAuth
    ) -> None:
        trainee = await self.repo.get_by_id(trainee_id)
        if not trainee:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found",
            )

        allowed = (
            trainee_id == current.id
            or trainee.coach_id == current.id
            or trainee.coach_request_id == current.id
        )
        if not allowed:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied",
            )

        prev_coach = trainee.coach_id
        prev_request = trainee.coach_request_id

        trainee.coach_id = None
        trainee.coach_request_id = None
        await self.session.commit()

        if prev_request is not None:
            pending = await self.notif_repo.get_coach_request(
                recipient_id=prev_request, actor_id=trainee_id
            )
            if pending:
                await self.notif_repo.delete_by_id(pending.id)

        if prev_coach is not None and current.id != prev_coach:
            await self.notif_repo.create(
                NotificationWrite(
                    recipient_id=prev_coach,
                    actor_id=trainee_id,
                    type=NotificationType.trainee_removed,
                )
            )

    async def get_requests_get(
        self, coach_id: int, current: CurrentAuth
    ) -> list[UserRead]:
        if coach_id != current.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only view your own requests",
            )
        await self._assert_coach(current)

        requests = await self.repo.get_all_by_coach_request_id(coach_id)
        return [UserRead.model_validate(r) for r in requests]

    async def approve_request_post(
        self, trainee_id: int, current: CurrentAuth
    ) -> UserRead:
        await self._assert_coach(current)
        trainee = await self._get_pending_request_or_404(
            trainee_id, current.id
        )
        trainee.coach_id = current.id
        trainee.coach_request_id = None
        await self.session.commit()
        await self.session.refresh(trainee)

        pending = await self.notif_repo.get_coach_request(
            recipient_id=current.id, actor_id=trainee_id
        )
        if pending:
            pending.type = NotificationType.trainee_added
            await self.session.commit()

        await self.notif_repo.create(
            NotificationWrite(
                recipient_id=trainee_id,
                actor_id=current.id,
                type=NotificationType.request_accepted,
            )
        )

        return UserRead.model_validate(trainee)

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

