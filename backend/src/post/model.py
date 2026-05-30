from datetime import datetime

from sqlalchemy import ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column

from src.common import Base


class Post(Base):
    __tablename__ = "post"

    id: Mapped[int] = mapped_column(primary_key=True)
    auth_id: Mapped[int] = mapped_column(
        ForeignKey("user.auth_id"), nullable=False
    )
    name: Mapped[str] = mapped_column(nullable=False)
    mark: Mapped[int | None] = mapped_column(nullable=True)
    energy: Mapped[int | None] = mapped_column(nullable=True)
    description: Mapped[str | None] = mapped_column(nullable=True)
    comment: Mapped[str | None] = mapped_column(nullable=True)

    updated_at: Mapped[datetime] = mapped_column(
        nullable=False, default=func.now(), onupdate=func.now()
    )
    created_at: Mapped[datetime] = mapped_column(
        nullable=False, default=func.now()
    )
