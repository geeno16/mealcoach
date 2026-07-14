from fastapi import HTTPException, status

from src.auth.schema import CurrentAuth
from src.user.model import UserRole
from src.user.repository import UserRepository


async def assert_can_view(
    user_repo: UserRepository,
    target_auth_id: int,
    current: CurrentAuth,
) -> None:
    if target_auth_id == current.id:
        return

    current_user = await user_repo.get_by_id(current.id)
    if current_user and current_user.role == UserRole.coach:
        owner = await user_repo.get_by_id(target_auth_id)
        if owner and owner.coach_id == current.id:
            return

    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Access denied",
    )
