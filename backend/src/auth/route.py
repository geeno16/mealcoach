from fastapi import APIRouter, Response, status

from src.auth.dependency import (
    AuthServiceDependency,
    CurrentAuthDependency,
)
from src.auth.schema import AuthRead, AuthWrite

auth_router = APIRouter(prefix="/api/auth", tags=["Auth"])


@auth_router.post("", status_code=status.HTTP_201_CREATED)
async def register_post(
    data: AuthWrite, service: AuthServiceDependency
) -> int:
    return await service.register_post(data)


@auth_router.post("/login", response_model=AuthRead)
async def login_post(
    data: AuthWrite, service: AuthServiceDependency, response: Response
) -> AuthRead:
    return await service.login_post(data, response)


@auth_router.post("/logout")
async def logout_post(
    service: AuthServiceDependency, response: Response
) -> dict:
    return await service.logout_post(response)


@auth_router.put("/{id}", response_model=AuthRead)
async def update_auth_post(
    id: int,
    data: AuthWrite,
    service: AuthServiceDependency,
    current: CurrentAuthDependency,
):
    return await service.update_auth_put(id, data, current)
