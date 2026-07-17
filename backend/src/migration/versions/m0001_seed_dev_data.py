from datetime import datetime, timedelta
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.repository import AuthRepository
from src.auth.schema import AuthWrite
from src.notification.model import Notification, NotificationType
from src.post.model import Meal, Post
from src.user.model import UserRole
from src.user.repository import UserRepository
from src.user.schema import UserWrite

DEV_ONLY = True

PASSWORD = "Seed12345"

_BASE = datetime.now().replace(
    hour=12, minute=0, second=0, microsecond=0
)


async def _create_auth(session: AsyncSession, email: str) -> int:
    auth = await AuthRepository(session).create(
        AuthWrite(email=email, password=PASSWORD)
    )
    auth.is_verified = True
    await session.commit()
    return auth.id


def _post(
    auth_id: int,
    name: str,
    days_ago: int,
    meals: list[dict[str, Any]],
    mark: int | None = None,
    comment: str | None = None,
    description: str | None = None,
) -> Post:
    moment = _BASE - timedelta(days=days_ago)
    return Post(
        auth_id=auth_id,
        name=name,
        description=description,
        mark=mark,
        comment=comment,
        created_at=moment,
        updated_at=moment,
        meals=[Meal(**meal) for meal in meals],
    )


async def upgrade(session: AsyncSession) -> None:
    user_repo = UserRepository(session)

    coach_anna = await _create_auth(session, "coach1@example.com")
    await user_repo.create(
        UserWrite(
            auth_id=coach_anna,
            role=UserRole.coach,
            name="Анна",
            surname="Тренерова",
        )
    )

    coach_boris = await _create_auth(session, "coach2@example.com")
    await user_repo.create(
        UserWrite(
            auth_id=coach_boris,
            role=UserRole.coach,
            name="Борис",
            surname="Безучеников",
        )
    )

    ivan = await _create_auth(session, "trainee1@example.com")
    await user_repo.create(
        UserWrite(
            auth_id=ivan,
            role=UserRole.trainee,
            name="Иван",
            surname="Активный",
            age=28,
            weight=82,
            height=181,
            coach_id=coach_anna,
        )
    )

    maria = await _create_auth(session, "trainee2@example.com")
    await user_repo.create(
        UserWrite(
            auth_id=maria,
            role=UserRole.trainee,
            name="Мария",
            surname="Новенькая",
            age=24,
            weight=58,
            height=166,
            coach_id=coach_anna,
        )
    )

    petr = await _create_auth(session, "trainee3@example.com")
    await user_repo.create(
        UserWrite(
            auth_id=petr,
            role=UserRole.trainee,
            name="Пётр",
            surname="Ожидающий",
            age=35,
            weight=95,
            height=178,
            coach_request_id=coach_anna,
        )
    )

    olga = await _create_auth(session, "trainee4@example.com")
    await user_repo.create(
        UserWrite(
            auth_id=olga,
            role=UserRole.trainee,
            name="Ольга",
            surname="Безтренера",
            age=31,
            weight=64,
            height=170,
        )
    )

    session.add_all(
        [
            _post(
                ivan,
                "Завтрак",
                0,
                [
                    {
                        "name": "Овсянка на молоке",
                        "cal": 320,
                        "protein": 12,
                        "fat": 6,
                        "carbohydrate": 54,
                    },
                    {
                        "name": "Кофе с молоком",
                        "cal": 60,
                        "protein": 3,
                        "fat": 3,
                        "carbohydrate": 5,
                    },
                ],
                description="Лёгкое начало дня",
            ),
            _post(
                ivan,
                "Обед",
                1,
                [
                    {
                        "name": "Куриная грудка",
                        "cal": 340,
                        "protein": 62,
                        "fat": 8,
                        "carbohydrate": 0,
                    },
                    {
                        "name": "Гречка",
                        "cal": 280,
                        "protein": 10,
                        "fat": 3,
                        "carbohydrate": 56,
                    },
                    {
                        "name": "Салат",
                        "cal": 90,
                        "protein": 2,
                        "fat": 7,
                        "carbohydrate": 6,
                    },
                ],
                mark=5,
                comment="Отличный баланс, так держать",
            ),
            _post(
                ivan,
                "Ужин",
                2,
                [
                    {
                        "name": "Лосось",
                        "cal": 410,
                        "protein": 40,
                        "fat": 27,
                        "carbohydrate": 0,
                    },
                    {
                        "name": "Рис",
                        "cal": 210,
                        "protein": 4,
                        "fat": 1,
                        "carbohydrate": 46,
                    },
                ],
                mark=4,
                comment="Много жира вечером",
            ),
            _post(
                ivan,
                "Перекус",
                3,
                [
                    {
                        "name": "Протеиновый батончик",
                        "cal": 220,
                        "protein": 20,
                        "fat": 8,
                        "carbohydrate": 22,
                    }
                ],
                mark=3,
            ),
            _post(
                ivan,
                "Фастфуд",
                5,
                [
                    {
                        "name": "Бургер",
                        "cal": 780,
                        "protein": 32,
                        "fat": 45,
                        "carbohydrate": 58,
                    },
                    {
                        "name": "Картофель фри",
                        "cal": 340,
                        "protein": 4,
                        "fat": 17,
                        "carbohydrate": 43,
                    },
                    {
                        "name": "Кола",
                        "cal": 150,
                        "protein": 0,
                        "fat": 0,
                        "carbohydrate": 39,
                    },
                ],
                mark=1,
                comment="Так лучше не делать",
                description="Сорвался",
            ),
            _post(
                ivan,
                "Завтрак",
                6,
                [
                    {
                        "name": "Яичница из трёх яиц",
                        "cal": 260,
                        "protein": 19,
                        "fat": 20,
                        "carbohydrate": 2,
                    },
                    {
                        "name": "Тост",
                        "cal": 120,
                        "protein": 4,
                        "fat": 2,
                        "carbohydrate": 22,
                    },
                ],
                mark=4,
            ),
            _post(
                ivan,
                "Обед",
                8,
                [
                    {
                        "name": "Паста болоньезе",
                        "cal": 620,
                        "protein": 28,
                        "fat": 18,
                        "carbohydrate": 84,
                    }
                ],
            ),
            _post(
                ivan,
                "Ужин",
                9,
                [
                    {
                        "name": "Творог",
                        "cal": 180,
                        "protein": 30,
                        "fat": 3,
                        "carbohydrate": 8,
                    },
                    {
                        "name": "Банан",
                        "cal": 105,
                        "protein": 1,
                        "fat": 0,
                        "carbohydrate": 27,
                    },
                ],
                mark=5,
                comment="Хороший белковый ужин",
            ),
            _post(
                maria,
                "Завтрак",
                0,
                [
                    {
                        "name": "Смузи",
                        "cal": 240,
                        "protein": 6,
                        "fat": 4,
                        "carbohydrate": 46,
                    }
                ],
            ),
            _post(
                maria,
                "Обед",
                2,
                [
                    {
                        "name": "Салат с тунцом",
                        "cal": 310,
                        "protein": 28,
                        "fat": 14,
                        "carbohydrate": 12,
                    },
                    {
                        "name": "Хлебцы",
                        "cal": 90,
                        "protein": 3,
                        "fat": 1,
                        "carbohydrate": 18,
                    },
                ],
                mark=5,
                comment="Отлично",
            ),
            _post(
                maria,
                "Ужин",
                4,
                [
                    {
                        "name": "Индейка с овощами",
                        "cal": 380,
                        "protein": 42,
                        "fat": 12,
                        "carbohydrate": 24,
                    }
                ],
                mark=4,
            ),
            _post(
                olga,
                "Завтрак",
                1,
                [
                    {
                        "name": "Сырники",
                        "cal": 420,
                        "protein": 24,
                        "fat": 18,
                        "carbohydrate": 40,
                    }
                ],
            ),
        ]
    )
    await session.commit()

    ivan_post = (
        (
            await session.execute(
                select(Post.id)
                .where(Post.auth_id == ivan)
                .order_by(Post.created_at.desc())
            )
        )
        .scalars()
        .first()
    )
    maria_post = (
        (
            await session.execute(
                select(Post.id)
                .where(Post.auth_id == maria)
                .order_by(Post.created_at.desc())
            )
        )
        .scalars()
        .first()
    )

    session.add_all(
        [
            Notification(
                recipient_id=coach_anna,
                actor_id=petr,
                type=NotificationType.coach_request,
            ),
            Notification(
                recipient_id=ivan,
                actor_id=coach_anna,
                type=NotificationType.request_accepted,
            ),
            Notification(
                recipient_id=maria,
                actor_id=coach_anna,
                type=NotificationType.request_accepted,
            ),
            Notification(
                recipient_id=coach_anna,
                actor_id=ivan,
                post_id=ivan_post,
                type=NotificationType.post_created,
            ),
            Notification(
                recipient_id=coach_anna,
                actor_id=maria,
                post_id=maria_post,
                type=NotificationType.post_created,
            ),
            Notification(
                recipient_id=ivan,
                actor_id=coach_anna,
                post_id=ivan_post,
                type=NotificationType.post_graded,
            ),
        ]
    )
    await session.commit()
