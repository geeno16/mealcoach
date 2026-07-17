import enum
from datetime import datetime

from sqlalchemy import Enum, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column

from src.common import Base


class NotificationType(enum.Enum):
    coach_request = "coach_request"
    trainee_added = "trainee_added"
    trainee_removed = "trainee_removed"
    request_accepted = "request_accepted"
    post_graded = "post_graded"
    post_created = "post_created"


class Notification(Base):
    __tablename__ = "notification"

    id: Mapped[int] = mapped_column(primary_key=True)
    recipient_id: Mapped[int] = mapped_column(
        ForeignKey("user.auth_id", ondelete="CASCADE"), nullable=False
    )
    actor_id: Mapped[int | None] = mapped_column(
        ForeignKey("user.auth_id", ondelete="SET NULL"), nullable=True
    )
    post_id: Mapped[int | None] = mapped_column(
        ForeignKey("post.id", ondelete="CASCADE"), nullable=True
    )
    type: Mapped[NotificationType] = mapped_column(
        Enum(NotificationType), nullable=False
    )

    updated_at: Mapped[datetime] = mapped_column(
        nullable=False, default=func.now(), onupdate=func.now()
    )
    created_at: Mapped[datetime] = mapped_column(
        nullable=False, default=func.now()
    )
