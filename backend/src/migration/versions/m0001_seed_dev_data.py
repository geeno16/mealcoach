import colorsys
import random
import struct
import zlib
from datetime import datetime, timedelta
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.repository import AuthRepository
from src.auth.schema import AuthWrite
from src.notification.model import Notification, NotificationType
from src.picture.model import Picture
from src.post.model import Meal, Post
from src.user.model import UserRole
from src.user.repository import UserRepository
from src.user.schema import UserWrite

DEV_ONLY = True

PASSWORD = "Seed12345"

_BASE = datetime.now().replace(
    hour=12, minute=0, second=0, microsecond=0
)

_RNG = random.Random(42)

_MEAL_POOL = [
    ("Овсянка с ягодами", 310, 11, 6, 52),
    ("Гречка с курицей", 430, 34, 9, 48),
    ("Творог с мёдом", 190, 24, 4, 14),
    ("Салат Цезарь", 360, 22, 24, 12),
    ("Паста с томатами", 480, 16, 12, 78),
    ("Рыба на пару", 240, 32, 8, 2),
    ("Йогурт с гранолой", 260, 10, 8, 36),
    ("Борщ", 210, 9, 8, 24),
    ("Плов", 520, 20, 18, 66),
    ("Омлет с овощами", 280, 20, 18, 6),
    ("Сэндвич с индейкой", 340, 22, 10, 38),
    ("Роллы", 400, 18, 10, 58),
    ("Куриный суп", 190, 14, 6, 18),
    ("Блины со сметаной", 380, 10, 16, 48),
    ("Тост с авокадо", 260, 7, 15, 24),
    ("Печёный картофель с сыром", 330, 12, 14, 40),
    ("Кефир", 90, 6, 3, 8),
    ("Орехи и сухофрукты", 220, 6, 16, 18),
    ("Стейк из индейки", 300, 38, 10, 0),
    ("Фруктовый салат", 140, 2, 1, 32),
]

_NAME_POOL: dict[str, list[str]] = {
    "short": [
        "Завтрак",
        "Обед",
        "Ужин",
        "Перекус",
        "Кофе",
        "Салат",
        "Йогурт",
        "Суп",
    ],
    "medium": [
        "Лёгкий завтрак перед пробежкой",
        "Обед после тренировки",
        "Ужин с семьёй",
        "Перекус на работе",
        "Плотный завтрак в выходной",
        "Быстрый обед между делами",
    ],
    "long": [
        "Большой воскресный обед со всей семьёй",
        "Поздний ужин после долгой смены на работе",
        "Праздничный стол на день рождения коллеги",
        "Обед в кафе с друзьями после работы",
    ],
}

_DESC_POOL: dict[str, list[str] | list[None]] = {
    "none": [None],
    "short": [
        "Всё по плану.",
        "Быстро и просто.",
        "Вкусно вышло.",
        "Не идеально, но норм.",
    ],
    "medium": [
        "Держался норм КБЖУ, но перекусил сладким после.",
        "Готовил сам, вышло дольше, чем рассчитывал.",
        "Хотел меньше жира, но вышло как вышло.",
        "Порция получилась больше, чем планировал.",
    ],
    "long": [
        (
            "Старался следовать плану питания, но день выдался "
            "суматошным — пришлось есть на бегу и не всё успел "
            "приготовить заранее. В целом калорийность в норме, "
            "но белка маловато."
        ),
        (
            "Готовили большой компанией, было сложно контролировать "
            "порции. Получилось вкусно, но явно больше обычной нормы "
            "по калориям и жирам — постараюсь не повторять так часто."
        ),
    ],
}

_COMMENTS = [
    None,
    None,
    None,
    "Хорошо",
    "Неплохо, но можно лучше",
    "Отличная работа, продолжай в том же духе",
]

_MARKS = [None, None, 1, 2, 3, 4, 5]


def _photo_color(index: int) -> tuple[int, int, int]:
    hue = (index * 0.618033988749895) % 1.0
    r, g, b = colorsys.hsv_to_rgb(hue, 0.55, 0.85)
    return (round(r * 255), round(g * 255), round(b * 255))


def _solid_png(
    width: int, height: int, rgb: tuple[int, int, int]
) -> bytes:
    def chunk(tag: bytes, data: bytes) -> bytes:
        return (
            struct.pack(">I", len(data))
            + tag
            + data
            + struct.pack(">I", zlib.crc32(tag + data))
        )

    signature = b"\x89PNG\r\n\x1a\n"
    header = struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0)
    row = b"\x00" + bytes(rgb) * width
    data = zlib.compress(row * height, 9)
    return (
        signature
        + chunk(b"IHDR", header)
        + chunk(b"IDAT", data)
        + chunk(b"IEND", b"")
    )


async def _create_auth(session: AsyncSession, email: str) -> int:
    auth = await AuthRepository(session).create(
        AuthWrite(email=email, password=PASSWORD)
    )
    auth.is_verified = True
    await session.commit()
    return auth.id


def _meal(
    name: str, cal: int, protein: int, fat: int, carbohydrate: int
) -> dict[str, Any]:
    return {
        "name": name,
        "cal": cal,
        "protein": protein,
        "fat": fat,
        "carbohydrate": carbohydrate,
    }


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


def _generate_posts(
    auth_id: int, start_day: int, count: int
) -> list[Post]:
    posts = []
    for i in range(count):
        name_tier = _RNG.choices(
            ["short", "medium", "long"], weights=[3, 3, 2]
        )[0]
        name = _RNG.choice(_NAME_POOL[name_tier])

        desc_tier = _RNG.choices(
            ["none", "short", "medium", "long"], weights=[3, 3, 2, 2]
        )[0]
        description = _RNG.choice(_DESC_POOL[desc_tier])

        meal_count = _RNG.choice([1, 1, 2, 2, 3])
        meals = [
            _meal(*_RNG.choice(_MEAL_POOL)) for _ in range(meal_count)
        ]

        posts.append(
            _post(
                auth_id,
                name,
                start_day + i,
                meals,
                mark=_RNG.choice(_MARKS),
                comment=_RNG.choice(_COMMENTS),
                description=description,
            )
        )
    return posts


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

    posts = [
        _post(
            ivan,
            "Плотный завтрак после утренней тренировки в зале",
            0,
            [
                _meal("Овсянка на молоке", 320, 12, 6, 54),
                _meal("Кофе с молоком", 60, 3, 3, 5),
            ],
            mark=4,
            comment="Хорошее начало дня",
            description=(
                "Держался плана: сложные углеводы, достаточно белка и "
                "минимум быстрых сахаров. Съел всё в течение часа после "
                "зала — самочувствие отличное, энергии хватило до обеда."
            ),
        ),
        _post(
            ivan,
            "Обед по плану питания",
            1,
            [
                _meal("Куриная грудка", 340, 62, 8, 0),
                _meal("Гречка", 280, 10, 3, 56),
                _meal("Салат", 90, 2, 7, 6),
            ],
            mark=5,
            comment="Отличный баланс, так держать",
            description="Сбалансированно, но вечером явно перебрал с жирами.",
        ),
        _post(
            ivan,
            "Ужин",
            2,
            [_meal("Творог", 180, 30, 3, 8)],
            mark=3,
        ),
        _post(
            ivan,
            "Поздний перекус перед сном после работы",
            3,
            [_meal("Протеиновый батончик", 220, 20, 8, 22)],
            description="Немного, но зря.",
        ),
        _post(
            ivan,
            "Кофе",
            4,
            [_meal("Латте большой", 180, 9, 8, 18)],
            description=(
                "Взял большой латте и не заметил, как выпил второй. "
                "Понимаю, что это лишние калории и кофеин на ночь, но "
                "без него днём вообще не могу собраться."
            ),
        ),
        _post(
            ivan,
            "Большой семейный обед на выходных",
            5,
            [
                _meal("Стейк", 520, 46, 34, 0),
                _meal("Картофель запечённый", 240, 5, 6, 42),
                _meal("Овощи гриль", 110, 3, 5, 14),
            ],
            mark=2,
            comment="Слишком большая порция",
        ),
        _post(
            ivan,
            "Смузи",
            6,
            [_meal("Смузи ягодный", 210, 6, 3, 40)],
            mark=5,
            description="Быстрый вариант на бегу, зато свежий и лёгкий.",
        ),
        _post(
            ivan,
            "Обед в столовой на работе вместе с коллегами",
            8,
            [
                _meal("Суп-лапша", 180, 8, 5, 26),
                _meal("Котлета с пюре", 430, 24, 22, 38),
            ],
            description="Особого выбора не было, взял что дают.",
        ),
        _post(
            maria,
            "Завтрак",
            0,
            [_meal("Смузи протеиновый", 240, 22, 4, 30)],
            mark=5,
            description=(
                "Начала утро со смузи из банана, шпината и протеина — "
                "вышло вкусно и сытно. Держит до обеда без перекусов, "
                "что для меня редкость. Буду делать так чаще."
            ),
        ),
        _post(
            maria,
            "Обед с большим салатом из свежих овощей и тунца",
            2,
            [
                _meal("Салат с тунцом", 310, 28, 14, 12),
                _meal("Хлебцы", 90, 3, 1, 18),
            ],
            mark=4,
            comment="Отлично",
        ),
        _post(
            maria,
            "Ужин",
            4,
            [_meal("Индейка с овощами", 380, 42, 12, 24)],
            description="Лёгкий, как и хотела.",
        ),
        _post(
            olga,
            "Сырники с утра",
            1,
            [_meal("Сырники со сметаной", 420, 24, 18, 40)],
            description="Домашние, со сметаной — не самый диетический вариант.",
        ),
    ]

    posts += _generate_posts(ivan, 9, 24)
    posts += _generate_posts(maria, 5, 9)
    posts += _generate_posts(olga, 2, 3)

    for i, post in enumerate(posts):
        if i % 3 == 2:
            continue
        picture = Picture(data=_solid_png(320, 320, _photo_color(i)))
        session.add(picture)
        await session.flush()
        post.meals[0].picture_id = picture.id

    session.add_all(posts)
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
