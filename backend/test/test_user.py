import pytest

from src.user import UserWrite

from test.helpers import (
    create_user,
    get_trainees,
    get_user,
    login,
    update_user,
)


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
async def test_get_trainees_get_positive(async_client, team):
    await login(team[0].auth.email, team[0].auth.password, async_client)
    response = await get_trainees(team[0].auth.id, async_client)
    assert response.status_code == 200
    assert len(response.json()) == 3


@pytest.mark.asyncio
async def test_get_trainees_get_negative(async_client, team):
    await login(team[0].auth.email, team[0].auth.password, async_client)
    response = await get_trainees(team[-1].auth.id, async_client)
    assert response.status_code == 403

    await login(team[1].auth.email, team[1].auth.password, async_client)
    response = await get_trainees(team[1].auth.id, async_client)
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
