from datetime import datetime

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession

from src.post import Meal, Post
from src.user import UserRepository, UserRole, UserWrite
from test.helpers import get_statistics, login


@pytest_asyncio.fixture
async def stats_user(db_session: AsyncSession, auth):
    await UserRepository(db_session).create(
        UserWrite(
            auth_id=auth.id,
            role=UserRole.trainee,
            name="Stat",
            weight=80,
            height=180,
        )
    )
    posts = [
        Post(
            auth_id=auth.id,
            name="Breakfast",
            mark=4,
            comment="Great",
            created_at=datetime(2026, 7, 10),
            meals=[
                Meal(cal=500, protein=30, fat=10, carbohydrate=60),
                Meal(cal=300, protein=20, fat=5, carbohydrate=40),
            ],
        ),
        Post(
            auth_id=auth.id,
            name="Lunch",
            mark=2,
            created_at=datetime(2026, 7, 11),
            meals=[Meal(cal=400, protein=10, fat=20, carbohydrate=50)],
        ),
    ]
    db_session.add_all(posts)
    await db_session.commit()
    yield auth


@pytest.mark.asyncio
async def test_get_statistics_content(async_client, stats_user):
    await login(stats_user.email, stats_user.password, async_client)
    response = await get_statistics(stats_user.id, async_client)
    assert response.status_code == 200
    body = response.json()

    assert body["user_id"] == stats_user.id

    assert body["profile"]["bmi"] == 24.7
    assert body["profile"]["bmi_category"] == "normal"

    posts = body["posts"]
    assert posts["total"] == 2
    assert posts["graded"] == 2
    assert posts["ungraded"] == 0
    assert posts["with_comment"] == 1
    assert posts["active_days"] == 2
    assert posts["longest_streak"] == 2

    marks = body["marks"]
    assert marks["average"] == 3.0
    assert marks["best"] == 4
    assert marks["worst"] == 2
    assert marks["distribution"] == {"2": 1, "4": 1}

    nutrition = body["nutrition"]
    assert nutrition["total_calories"] == 1200
    assert nutrition["total_protein"] == 60
    assert nutrition["avg_calories_per_post"] == 600.0
    assert nutrition["avg_calories_per_meal"] == 400.0
    assert nutrition["macro_ratio"]["protein"] == 24.5
    assert nutrition["macro_ratio"]["carbohydrate"] == 61.2

    meals = body["meals"]
    assert meals["total"] == 3
    assert meals["avg_per_post"] == 1.5
    assert meals["with_picture"] == 0

    timeline = body["timeline"]
    assert len(timeline) == 2
    assert timeline[0] == {
        "date": "2026-07-10",
        "posts": 1,
        "calories": 800,
        "avg_mark": 4.0,
    }
    assert timeline[1]["calories"] == 400
    assert timeline[1]["avg_mark"] == 2.0


@pytest.mark.asyncio
async def test_get_statistics_empty(
    async_client, auth, user: UserWrite, db_session: AsyncSession
):
    await UserRepository(db_session).create(user)
    await login(auth.email, auth.password, async_client)
    response = await get_statistics(auth.id, async_client)
    assert response.status_code == 200
    body = response.json()
    assert body["posts"]["total"] == 0
    assert body["posts"]["longest_streak"] == 0
    assert body["marks"]["average"] is None
    assert body["marks"]["distribution"] == {}
    assert body["nutrition"]["total_calories"] == 0
    assert body["nutrition"]["macro_ratio"]["protein"] is None
    assert body["meals"]["avg_per_post"] is None
    assert body["timeline"] == []


@pytest.mark.asyncio
async def test_get_statistics_access(async_client, team, db_session):
    db_session.add(
        Post(
            auth_id=team[1].auth.id,
            name="Post",
            created_at=datetime(2026, 7, 10),
            meals=[Meal(cal=100)],
        )
    )
    await db_session.commit()

    await login(team[1].auth.email, team[1].auth.password, async_client)
    response = await get_statistics(team[1].auth.id, async_client)
    assert response.status_code == 200

    await login(team[0].auth.email, team[0].auth.password, async_client)
    response = await get_statistics(team[1].auth.id, async_client)
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_get_statistics_access_negative(async_client, team):
    await login(team[2].auth.email, team[2].auth.password, async_client)
    response = await get_statistics(team[1].auth.id, async_client)
    assert response.status_code == 403

    await login(
        team[-1].auth.email, team[-1].auth.password, async_client
    )
    response = await get_statistics(team[1].auth.id, async_client)
    assert response.status_code == 403

    await login(team[1].auth.email, team[1].auth.password, async_client)
    response = await get_statistics(-1, async_client)
    assert response.status_code == 404
