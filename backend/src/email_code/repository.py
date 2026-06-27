from sqlalchemy import delete, select

from src.common import BaseRepository
from src.email_code.model import EmailCode
from src.email_code.schema import EmailCodeWrite


class EmailCodeRepository(BaseRepository[EmailCode, EmailCodeWrite]):
    model = EmailCode

    async def get_active_by_auth_id(
        self, auth_id: int
    ) -> EmailCode | None:
        result = await self.session.execute(
            select(EmailCode)
            .where(
                EmailCode.auth_id == auth_id,
                EmailCode.used.is_(False),
            )
            .order_by(EmailCode.created_at.desc())
        )
        return result.scalars().first()

    async def delete_by_auth_id(self, auth_id: int) -> None:
        await self.session.execute(
            delete(EmailCode).where(EmailCode.auth_id == auth_id)
        )
        await self.session.commit()

    async def increment_attempts(self, code: EmailCode) -> None:
        code.attempts += 1
        await self.session.commit()
        await self.session.refresh(code)

    async def mark_used(self, code: EmailCode) -> None:
        code.used = True
        await self.session.commit()
        await self.session.refresh(code)
