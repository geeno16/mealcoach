from fastapi import APIRouter, Response, status

from src.auth.dependency import (
    AuthServiceDependency,
    CurrentAuthDependency,
)
from src.auth.schema import (
    AuthRead,
    AuthWrite,
    EmailVerify,
    MessageResponse,
)

auth_router = APIRouter(prefix="/api/auth", tags=["Auth"])


@auth_router.post(
    "", status_code=status.HTTP_201_CREATED, response_model=AuthRead
)
async def register_post(
    data: AuthWrite, service: AuthServiceDependency, response: Response
) -> AuthRead:
    auth = await service.register_post(data)
    response.headers["Location"] = f"/api/auth/{auth.id}"
    return auth


@auth_router.post("/verify-email", response_model=AuthRead)
async def verify_email_post(
    data: EmailVerify, service: AuthServiceDependency
) -> AuthRead:
    return await service.verify_email_post(data)


@auth_router.post("/resend-code", response_model=MessageResponse)
async def resend_code_post(
    data: AuthWrite, service: AuthServiceDependency
) -> MessageResponse:
    return await service.resend_code_post(data)


@auth_router.post("/login", response_model=AuthRead)
async def login_post(
    data: AuthWrite, service: AuthServiceDependency, response: Response
) -> AuthRead:
    return await service.login_post(data, response)


@auth_router.post("/logout", response_model=MessageResponse)
async def logout_post(
    service: AuthServiceDependency, response: Response
) -> MessageResponse:
    return await service.logout_post(response)


@auth_router.put("/{id}", response_model=AuthRead)
async def update_auth_post(
    id: int,
    data: AuthWrite,
    service: AuthServiceDependency,
    current: CurrentAuthDependency,
):
    return await service.update_auth_put(id, data, current)


@auth_router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_auth_delete(
    id: int,
    service: AuthServiceDependency,
    current: CurrentAuthDependency,
) -> None:
    await service.delete_auth_delete(id, current)
