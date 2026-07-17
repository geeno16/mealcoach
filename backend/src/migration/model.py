from datetime import datetime

from sqlalchemy import func
from sqlalchemy.orm import Mapped, mapped_column

from src.common import Base


class Migration(Base):
    __tablename__ = "migration"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(nullable=False, unique=True)
    applied_at: Mapped[datetime] = mapped_column(
        nullable=False, default=func.now()
    )
