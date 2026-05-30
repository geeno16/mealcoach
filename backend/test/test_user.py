from collections.abc import AsyncGenerator
from dataclasses import dataclass

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth import Auth, AuthRepository, AuthWrite
from src.user import User, UserRepository, UserRole, UserWrite
from test.helpers import (
    basic_email,
    basic_password,
    create_user,
    get_user,
    login,
    update_user,
)


@dataclass
class AuthUserPair:
    auth: Auth
    user: User


@pytest_asyncio.fixture
async def auth(db_session: AsyncSession) -> AsyncGenerator[Auth, None]:
    repo = AuthRepository(db_session)

    auth = await repo.create(
        AuthWrite(email=basic_email, password=basic_password)
    )

    yield auth


@pytest_asyncio.fixture
async def user(auth) -> AsyncGenerator[UserWrite, None]:
    new_user = UserWrite(
        auth_id=auth.id, role=UserRole.trainee, name="geeno16"
    )

    yield new_user


@pytest_asyncio.fixture
async def team(
    db_session: AsyncSession,
) -> AsyncGenerator[list[AuthUserPair], None]:
    auth_repo = AuthRepository(db_session)
    user_repo = UserRepository(db_session)

    coach_auth_list = [
        await auth_repo.create(
            AuthWrite(
                email=f"coach{i}@test.com", password=basic_password
            )
        )
        for i in range(2)
    ]
    coach_user_list = [
        await user_repo.create(
            UserWrite(
                auth_id=coach_auth_list[i].id,
                role=UserRole.coach,
                name="Coach",
            )
        )
        for i in range(2)
    ]

    pairs: list[AuthUserPair] = [
        AuthUserPair(auth=coach_auth_list[0], user=coach_user_list[0])
    ]

    for i in range(3):
        trainee_auth = await auth_repo.create(
            AuthWrite(
                email=f"trainee{i}@test.com", password=basic_password
            )
        )
        trainee_user = await user_repo.create(
            UserWrite(
                auth_id=trainee_auth.id,
                role=UserRole.trainee,
                name=f"Trainee{i}",
                coach_id=coach_auth_list[0].id,
            )
        )
        pairs.append(AuthUserPair(auth=trainee_auth, user=trainee_user))

    pairs.append(
        AuthUserPair(auth=coach_auth_list[1], user=coach_user_list[1])
    )

    yield pairs


@pytest.mark.asyncio
async def test_create_user_post_positive(async_client, auth, user):
    await login(auth.email, auth.password, async_client)
    response = await create_user(user, async_client)

    assert response.status_code == 201
    assert response.json()


@pytest.mark.asyncio
async def test_create_user_post_negative(async_client, auth, user):
    await login(auth.email, auth.password, async_client)
    user.auth_id = -1
    response = await create_user(user, async_client)
    assert response.status_code == 403

    user.auth_id = auth.id
    for _ in range(2):
        response = await create_user(user, async_client)
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_get_user_get_positive(async_client, team):
    await login(team[0].auth.email, team[0].auth.password, async_client)
    response = await get_user(team[0].auth.id, async_client)
    assert response.json()["auth_id"] == team[0].auth.id

    response = await get_user(team[1].user.auth_id, async_client)
    assert response.json()["auth_id"] == team[1].auth.id

    await login(team[1].auth.email, team[1].auth.password, async_client)
    response = await get_user(team[0].auth.id, async_client)
    assert response.status_code == 200

    response = await get_user(team[1].auth.id, async_client)
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_get_user_get_negative(async_client, team):
    await login(
        team[-1].auth.email, team[-1].auth.password, async_client
    )
    response = await get_user(team[0].auth.id, async_client)
    assert response.status_code == 403

    await login(team[1].auth.email, team[1].auth.password, async_client)
    response = await get_user(team[2].auth.id, async_client)
    assert response.status_code == 403

    response = await get_user(team[-1].auth.id, async_client)
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_update_user_put_positive(async_client, team, user):
    await login(team[1].auth.email, team[1].auth.password, async_client)
    response = await update_user(
        team[1].auth.id, UserWrite.model_validate(user), async_client
    )
    assert response.status_code == 200
    assert response.json()["auth_id"] == team[1].auth.id


@pytest.mark.asyncio
async def test_update_user_put_negative(async_client, team, user):
    await login(team[1].auth.email, team[1].auth.password, async_client)
    response = await update_user(
        team[2].auth.id, UserWrite.model_validate(user), async_client
    )
    assert response.status_code == 403


