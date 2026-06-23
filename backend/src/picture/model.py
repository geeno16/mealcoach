from datetime import datetime

from sqlalchemy import ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column

from src.common import Base


class Picture(Base):
    __tablename__ = "picture"

    id: Mapped[int] = mapped_column(primary_key=True)
    post_id: Mapped[int | None] = mapped_column(
        ForeignKey("post.id", ondelete="CASCADE"), nullable=True
    )
    data: Mapped[bytes] = mapped_column(nullable=False)

    updated_at: Mapped[datetime] = mapped_column(
        nullable=False, default=func.now(), onupdate=func.now()
    )
    created_at: Mapped[datetime] = mapped_column(
        nullable=False, default=func.now()
    )
