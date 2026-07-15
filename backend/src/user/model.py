import enum

from sqlalchemy import Enum, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from src.common import Base


class UserRole(enum.Enum):
    coach = "coach"
    trainee = "trainee"


class User(Base):
    __tablename__ = "user"

    auth_id: Mapped[int] = mapped_column(
        ForeignKey("auth.id", ondelete="CASCADE"), primary_key=True, autoincrement=False
    )
    coach_id: Mapped[int | None] = mapped_column(
        ForeignKey("user.auth_id"), nullable=True
    )
    coach_request_id: Mapped[int | None] = mapped_column(
        ForeignKey("user.auth_id"), nullable=True
    )
    picture_id: Mapped[int | None] = mapped_column(
        ForeignKey("picture.id", use_alter=True, name="fk_user_picture_id"), nullable=True
    )
    role: Mapped[UserRole] = mapped_column(
        Enum(UserRole), nullable=False
    )
    name: Mapped[str] = mapped_column(nullable=False)
    surname: Mapped[str | None] = mapped_column(nullable=True)
    age: Mapped[int | None] = mapped_column(nullable=True)
    weight: Mapped[int | None] = mapped_column(nullable=True)
    height: Mapped[int | None] = mapped_column(nullable=True)
