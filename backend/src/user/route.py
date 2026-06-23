from fastapi import APIRouter, Response, status

from src.auth.dependency import CurrentAuthDependency
from src.user.dependency import UserServiceDependency
from src.user.schema import UserRead, UserWrite

user_router = APIRouter(prefix="/api/users", tags=["Users"])


@user_router.get("", response_model=list[UserRead])
async def get_trainees_get(
    coach_id: int,
    service: UserServiceDependency,
    current: CurrentAuthDependency,
) -> list[UserRead]:
    return await service.get_trainees_get(coach_id, current)


@user_router.get("/{id}", response_model=UserRead)
async def get_user_get(
    id: int,
    service: UserServiceDependency,
    current: CurrentAuthDependency,
) -> UserRead:
    return await service.get_user_get(id, current)


@user_router.post(
    "", status_code=status.HTTP_201_CREATED, response_model=UserRead
)
async def create_user_post(
    data: UserWrite,
    service: UserServiceDependency,
    current: CurrentAuthDependency,
    response: Response,
) -> UserRead:
    user = await service.create_user_post(data, current)
    response.headers["Location"] = f"/api/users/{user.auth_id}"
    return user


@user_router.put("/{id}", response_model=UserRead)
async def update_user_put(
    id: int,
    data: UserWrite,
    service: UserServiceDependency,
    current: CurrentAuthDependency,
) -> UserRead:
    return await service.update_user_put(id, data, current)


