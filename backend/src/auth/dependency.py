from typing import Annotated

from fastapi import Depends, HTTPException, Request, status

from src.auth.schema import CurrentAuth
from src.auth.service import AuthService
from src.auth.token import decode_access_token
from src.common.database import SessionDependency


async def get_current_user(request: Request) -> CurrentAuth:
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

    try:
        payload = decode_access_token(token)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail=str(exc)
        ) from exc

    return CurrentAuth(id=payload["user_id"])


async def get_user_service(session: SessionDependency) -> AuthService:
    return AuthService(session)


CurrentAuthDependency = Annotated[
    CurrentAuth, Depends(get_current_user)
]
AuthServiceDependency = Annotated[
    AuthService, Depends(get_user_service)
]
