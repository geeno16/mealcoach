from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column

from src.common import Base


class EmailCode(Base):
    __tablename__ = "email_code"

    id: Mapped[int] = mapped_column(primary_key=True)
    auth_id: Mapped[int] = mapped_column(
        ForeignKey("auth.id", ondelete="CASCADE"), nullable=False
    )
    code_hash: Mapped[str] = mapped_column(nullable=False)
    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    attempts: Mapped[int] = mapped_column(nullable=False, default=0)
    used: Mapped[bool] = mapped_column(nullable=False, default=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=func.now()
    )
