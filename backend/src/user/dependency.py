from typing import Annotated

from fastapi import Depends

from src.auth.dependency import CurrentAuthDependency  # noqa: F401
from src.common.database import SessionDependency
from src.user.service import UserService


async def get_user_service(session: SessionDependency) -> UserService:
    return UserService(session)


UserServiceDependency = Annotated[
    UserService, Depends(get_user_service)
]
