import pytest

from src.post import MealWrite, PostWrite
from test.helpers import (
    approve_request,
    create_post,
    create_user,
    delete_coach,
    get_notifications,
    login,
    update_post,
)


def _types(response):
    return [n["type"] for n in response.json()]


@pytest.mark.asyncio
async def test_request_and_approve_flow(async_client, auth, user, team):
    await login(auth.email, auth.password, async_client)
    user.coach_email = team[0].auth.email
    await create_user(user, async_client)

    await login(team[0].auth.email, team[0].auth.password, async_client)
    response = await get_notifications(async_client)
    assert response.status_code == 200
    request = next(
        n for n in response.json() if n["type"] == "coach_request"
    )
    assert request["actor_id"] == auth.id
    assert request["actor_name"]

    await approve_request(auth.id, async_client)
    response = await get_notifications(async_client)
    assert "trainee_added" in _types(response)
    assert "coach_request" not in _types(response)

    await login(auth.email, auth.password, async_client)
    response = await get_notifications(async_client)
    assert "request_accepted" in _types(response)


@pytest.mark.asyncio
async def test_reject_removes_request_notification(
    async_client, auth, user, team
):
    await login(auth.email, auth.password, async_client)
    user.coach_email = team[0].auth.email
    await create_user(user, async_client)

    await login(team[0].auth.email, team[0].auth.password, async_client)
    await delete_coach(auth.id, async_client)

    response = await get_notifications(async_client)
    assert "coach_request" not in _types(response)
    assert "trainee_added" not in _types(response)


@pytest.mark.asyncio
async def test_trainee_left_notifies_coach(async_client, team):
    await login(team[1].auth.email, team[1].auth.password, async_client)
    await delete_coach(team[1].auth.id, async_client)

    await login(team[0].auth.email, team[0].auth.password, async_client)
    response = await get_notifications(async_client)
    removed = [
        n for n in response.json() if n["type"] == "trainee_removed"
    ]
    assert removed and removed[0]["actor_id"] == team[1].auth.id


@pytest.mark.asyncio
async def test_coach_remove_has_no_self_notification(async_client, team):
    await login(team[0].auth.email, team[0].auth.password, async_client)
    await delete_coach(team[1].auth.id, async_client)

    response = await get_notifications(async_client)
    assert "trainee_removed" not in _types(response)


@pytest.mark.asyncio
async def test_post_created_notifies_coach(async_client, team):
    await login(team[1].auth.email, team[1].auth.password, async_client)
    await create_post(
        PostWrite(
            auth_id=team[1].auth.id,
            name="Lunch",
            meals=[MealWrite(name="Soup")],
        ),
        async_client,
    )

    await login(team[0].auth.email, team[0].auth.password, async_client)
    response = await get_notifications(async_client)
    created = [
        n for n in response.json() if n["type"] == "post_created"
    ]
    assert created
    assert created[0]["actor_id"] == team[1].auth.id
    assert created[0]["post_name"] == "Lunch"


@pytest.mark.asyncio
async def test_post_graded_notifies_trainee(async_client, team):
    await login(team[1].auth.email, team[1].auth.password, async_client)
    response = await create_post(
        PostWrite(
            auth_id=team[1].auth.id,
            name="Dinner",
            meals=[MealWrite(name="Steak")],
        ),
        async_client,
    )
    post_id = response.json()["id"]

    await login(team[0].auth.email, team[0].auth.password, async_client)
    await update_post(
        post_id,
        PostWrite(
            auth_id=team[1].auth.id,
            name="Dinner",
            mark=5,
            comment="Good",
            meals=[MealWrite(name="Steak")],
        ),
        async_client,
    )

    await login(team[1].auth.email, team[1].auth.password, async_client)
    response = await get_notifications(async_client)
    graded = [n for n in response.json() if n["type"] == "post_graded"]
    assert graded and graded[0]["post_id"] == post_id


@pytest.mark.asyncio
async def test_notifications_unauthorized(async_client):
    response = await get_notifications(async_client)
    assert response.status_code == 401
