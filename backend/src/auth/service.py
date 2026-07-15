import os
import secrets
from datetime import UTC, datetime, timedelta

from fastapi import HTTPException, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.model import Auth
from src.auth.repository import AuthRepository
from src.auth.schema import (
    AuthRead,
    AuthWrite,
    CurrentAuth,
    EmailVerify,
    MessageResponse,
    PasswordForgot,
    PasswordReset,
)
from src.auth.token import create_access_token
from src.common import hash_secret, verify_secret
from src.email_code.repository import EmailCodeRepository
from src.email_code.schema import EmailCodeWrite
from src.mailer import sender

_CODE_TTL = timedelta(
    seconds=int(os.getenv("EMAIL_CODE_TTL_SECONDS", "600"))
)
_MAX_ATTEMPTS = int(os.getenv("EMAIL_CODE_MAX_ATTEMPTS", "5"))
_RESEND_COOLDOWN = timedelta(
    seconds=int(os.getenv("EMAIL_CODE_RESEND_COOLDOWN_SECONDS", "60"))
)


def _generate_code() -> str:
    return f"{secrets.randbelow(1_000_000):06d}"


class AuthService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.repo = AuthRepository(session)
        self.code_repo = EmailCodeRepository(session)

    async def _issue_code(self, auth: Auth, send=None) -> None:
        if send is None:
            send = sender.send_verification_code
        await self.code_repo.delete_by_auth_id(auth.id)
        code = _generate_code()
        await self.code_repo.create(
            EmailCodeWrite(
                auth_id=auth.id,
                code_hash=hash_secret(code),
                expires_at=datetime.now(UTC) + _CODE_TTL,
            )
        )
        await send(auth.email, code)

    async def _consume_active_code(
        self, auth: Auth, code_value: str
    ) -> None:
        code = await self.code_repo.get_active_by_auth_id(auth.id)
        if (
            not code
            or code.used
            or code.expires_at < datetime.now(UTC)
        ):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Code is invalid or expired",
            )

        if code.attempts >= _MAX_ATTEMPTS:
            await self.code_repo.mark_used(code)
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Too many attempts, request a new code",
            )

        if not verify_secret(code_value, code.code_hash):
            await self.code_repo.increment_attempts(code)
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect code",
            )

        await self.code_repo.mark_used(code)

    async def register_post(self, data: AuthWrite) -> AuthRead:
        existing = await self.repo.get_by_email(data.email)

        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"User with email={data.email} already exists",
            )

        auth = await self.repo.create(data)

        try:
            await self._issue_code(auth)
        except Exception as exc:
            await self.repo.delete_by_id(auth.id)
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="Could not send verification email",
            ) from exc

        return AuthRead.model_validate(auth)

    async def me(self, current: CurrentAuth) -> AuthRead:
        auth = await self.repo.get_by_id(current.id)

        if not auth:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found",
            )

        return AuthRead.model_validate(auth)

    async def resend_code_post(
        self, data: AuthWrite
    ) -> MessageResponse:
        auth = await self.repo.get_by_email(data.email)
        if not auth or not await self.repo.verify_password(
            auth, data.password
        ):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect login or password",
            )

        if auth.is_verified:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email is already verified",
            )

        active = await self.code_repo.get_active_by_auth_id(auth.id)
        if (
            active
            and active.expires_at > datetime.now(UTC)
            and datetime.now(UTC) - active.created_at < _RESEND_COOLDOWN
        ):
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Please wait before requesting a new code",
            )

        try:
            await self._issue_code(auth)
        except Exception as exc:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="Could not send verification email",
            ) from exc

        return MessageResponse(message="Code sent")

    async def forgot_password_post(
        self, data: PasswordForgot
    ) -> MessageResponse:
        auth = await self.repo.get_by_email(data.email)

        if auth:
            try:
                await self._issue_code(
                    auth, sender.send_password_reset_code
                )
            except Exception as exc:
                raise HTTPException(
                    status_code=status.HTTP_502_BAD_GATEWAY,
                    detail="Could not send password reset email",
                ) from exc

        return MessageResponse(
            message="If the account exists, a reset code was sent"
        )

    async def reset_password_post(
        self, data: PasswordReset
    ) -> AuthRead:
        auth = await self.repo.get_by_email(data.email)

        if not auth:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Code is invalid or expired",
            )

        await self._consume_active_code(auth, data.code)

        updated = await self.repo.update_by_id(
            auth.id,
            AuthWrite(email=auth.email, password=data.password),
        )

        return AuthRead.model_validate(updated)

    async def verify_email_post(self, data: EmailVerify) -> AuthRead:
        auth = await self.repo.get_by_email(data.email)
        if not auth:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Code is invalid or expired",
            )

        if auth.is_verified:
            return AuthRead.model_validate(auth)

        await self._consume_active_code(auth, data.code)

        auth.is_verified = True
        await self.session.commit()
        await self.session.refresh(auth)

        return AuthRead.model_validate(auth)

    async def login_post(
        self, data: AuthWrite, response: Response
    ) -> AuthRead:
        auth = await self.repo.get_by_email(data.email)

        if not auth or not await self.repo.verify_password(
            auth, data.password
        ):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect login or password",
            )

        if not auth.is_verified:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Email is not verified",
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
