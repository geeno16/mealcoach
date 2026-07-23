from datetime import datetime

from sqlalchemy import ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.common import Base
from src.picture.model import Picture


class Post(Base):
    __tablename__ = "post"

    id: Mapped[int] = mapped_column(primary_key=True)
    auth_id: Mapped[int] = mapped_column(
        ForeignKey("user.auth_id"), nullable=False
    )
    name: Mapped[str] = mapped_column(nullable=False)
    mark: Mapped[int | None] = mapped_column(nullable=True)
    description: Mapped[str | None] = mapped_column(nullable=True)
    comment: Mapped[str | None] = mapped_column(nullable=True)

    updated_at: Mapped[datetime] = mapped_column(
        nullable=False, default=func.now(), onupdate=func.now()
    )
    created_at: Mapped[datetime] = mapped_column(
        nullable=False, default=func.now()
    )

    meals: Mapped[list["Meal"]] = relationship(
        back_populates="post",
        cascade="all, delete-orphan",
        lazy="selectin",
        order_by="Meal.id",
    )


class Meal(Base):
    __tablename__ = "meal"

    id: Mapped[int] = mapped_column(primary_key=True)
    post_id: Mapped[int] = mapped_column(
        ForeignKey("post.id", ondelete="CASCADE"), nullable=False
    )
    picture_id: Mapped[int | None] = mapped_column(
        ForeignKey(
            "picture.id", use_alter=True, name="fk_meal_picture_id"
        ),
        nullable=True,
    )
    name: Mapped[str | None] = mapped_column(nullable=True)
    cal: Mapped[int | None] = mapped_column(nullable=True)
    protein: Mapped[int | None] = mapped_column(nullable=True)
    fat: Mapped[int | None] = mapped_column(nullable=True)
    carbohydrate: Mapped[int | None] = mapped_column(nullable=True)

    post: Mapped["Post"] = relationship(back_populates="meals")
    picture: Mapped[Picture | None] = relationship(
        lazy="selectin", viewonly=True
    )

    @property
    def picture_width(self) -> int | None:
        return self.picture.width if self.picture else None

    @property
    def picture_height(self) -> int | None:
        return self.picture.height if self.picture else None
