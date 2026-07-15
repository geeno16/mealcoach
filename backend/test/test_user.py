import pytest

from src.user import UserWrite
from test.helpers import (
    approve_request,
    create_user,
    delete_coach,
    get_requests,
    get_trainees,
    get_user,
    login,
    request_coach,
    update_user,
)


@pytest.mark.asyncio
async def test_create_user_post_positive(async_client, auth, user, team):
    await login(auth.email, auth.password, async_client)
    user.coach_email = team[0].auth.email
    response = await create_user(user, async_client)

    assert response.status_code == 201
    assert response.json()


@pytest.mark.asyncio
async def test_create_user_post_negative(async_client, auth, user, team):
    await login(auth.email, auth.password, async_client)
    user.coach_email = team[0].auth.email
    user.auth_id = -1
    response = await create_user(user, async_client)
    assert response.status_code == 403

    user.auth_id = auth.id
    for _ in range(2):
        response = await create_user(user, async_client)
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_create_user_trainee_without_coach(async_client, auth, user):
    await login(auth.email, auth.password, async_client)
    response = await create_user(user, async_client)
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_create_user_with_coach_email_positive(
    async_client, auth, user, team
):
    await login(auth.email, auth.password, async_client)
    user.coach_email = team[0].auth.email
    response = await create_user(user, async_client)

    assert response.status_code == 201
    assert response.json()["coach_id"] is None
    assert response.json()["coach_request_id"] == team[0].auth.id


@pytest.mark.asyncio
async def test_approve_request_positive(async_client, auth, user, team):
    await login(auth.email, auth.password, async_client)
    user.coach_email = team[0].auth.email
    await create_user(user, async_client)

    await login(team[0].auth.email, team[0].auth.password, async_client)
    response = await get_requests(team[0].auth.id, async_client)
    assert response.status_code == 200
    assert any(r["auth_id"] == auth.id for r in response.json())

    response = await approve_request(auth.id, async_client)
    assert response.status_code == 200
    assert response.json()["coach_id"] == team[0].auth.id
    assert response.json()["coach_request_id"] is None

    response = await get_requests(team[0].auth.id, async_client)
    assert all(r["auth_id"] != auth.id for r in response.json())


@pytest.mark.asyncio
async def test_reject_request_positive(async_client, auth, user, team):
    await login(auth.email, auth.password, async_client)
    user.coach_email = team[0].auth.email
    await create_user(user, async_client)

    await login(team[0].auth.email, team[0].auth.password, async_client)
    response = await delete_coach(auth.id, async_client)
    assert response.status_code == 204

    response = await get_requests(team[0].auth.id, async_client)
    assert all(r["auth_id"] != auth.id for r in response.json())


@pytest.mark.asyncio
async def test_cancel_own_request(async_client, auth, user, team):
    await login(auth.email, auth.password, async_client)
    user.coach_email = team[0].auth.email
    await create_user(user, async_client)

    response = await delete_coach(auth.id, async_client)
    assert response.status_code == 204

    response = await get_user(auth.id, async_client)
    assert response.json()["coach_request_id"] is None
    assert response.json()["coach_id"] is None


@pytest.mark.asyncio
async def test_approve_request_negative(async_client, auth, user, team):
    await login(auth.email, auth.password, async_client)
    user.coach_email = team[0].auth.email
    await create_user(user, async_client)

    await login(
        team[-1].auth.email, team[-1].auth.password, async_client
    )
    response = await approve_request(auth.id, async_client)
    assert response.status_code == 404

    await login(team[1].auth.email, team[1].auth.password, async_client)
    response = await approve_request(auth.id, async_client)
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_request_coach_flow(async_client, auth, user, team):
    await login(auth.email, auth.password, async_client)
    user.coach_email = team[0].auth.email
    await create_user(user, async_client)

    await login(team[0].auth.email, team[0].auth.password, async_client)
    await delete_coach(auth.id, async_client)

    await login(auth.email, auth.password, async_client)
    response = await request_coach(
        auth.id, team[0].auth.email, async_client
    )
    assert response.status_code == 200
    assert response.json()["coach_request_id"] == team[0].auth.id

    await login(team[0].auth.email, team[0].auth.password, async_client)
    await approve_request(auth.id, async_client)

    await login(auth.email, auth.password, async_client)
    response = await request_coach(
        auth.id, team[-1].auth.email, async_client
    )
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_delete_coach_by_trainee(async_client, team):
    await login(team[1].auth.email, team[1].auth.password, async_client)
    response = await delete_coach(team[1].auth.id, async_client)
    assert response.status_code == 204

    response = await get_user(team[1].auth.id, async_client)
    assert response.json()["coach_id"] is None
    assert response.json()["coach_request_id"] is None

    response = await delete_coach(team[1].auth.id, async_client)
    assert response.status_code == 204


@pytest.mark.asyncio
async def test_delete_coach_by_coach(async_client, team):
    await login(team[0].auth.email, team[0].auth.password, async_client)
    response = await delete_coach(team[1].auth.id, async_client)
    assert response.status_code == 204

    response = await get_trainees(team[0].auth.id, async_client)
    assert all(t["auth_id"] != team[1].auth.id for t in response.json())


@pytest.mark.asyncio
async def test_delete_coach_negative(async_client, team):
    await login(
        team[-1].auth.email, team[-1].auth.password, async_client
    )
    response = await delete_coach(team[1].auth.id, async_client)
    assert response.status_code == 403

    await login(team[2].auth.email, team[2].auth.password, async_client)
    response = await delete_coach(team[1].auth.id, async_client)
    assert response.status_code == 403

    await login(team[0].auth.email, team[0].auth.password, async_client)
    response = await delete_coach(-1, async_client)
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_request_coach_while_pending(
    async_client, auth, user, team
):
    await login(auth.email, auth.password, async_client)
    user.coach_email = team[0].auth.email
    await create_user(user, async_client)

    response = await request_coach(
        auth.id, team[-1].auth.email, async_client
    )
    assert response.status_code == 400

    response = await get_user(auth.id, async_client)
    assert response.json()["coach_request_id"] == team[0].auth.id


@pytest.mark.asyncio
async def test_approve_cancelled_request(
    async_client, auth, user, team
):
    await login(auth.email, auth.password, async_client)
    user.coach_email = team[0].auth.email
    await create_user(user, async_client)
    await delete_coach(auth.id, async_client)

    await login(team[0].auth.email, team[0].auth.password, async_client)
    response = await approve_request(auth.id, async_client)
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_approve_request_readdressed(
    async_client, auth, user, team
):
    await login(auth.email, auth.password, async_client)
    user.coach_email = team[0].auth.email
    await create_user(user, async_client)
    await delete_coach(auth.id, async_client)
    await request_coach(auth.id, team[-1].auth.email, async_client)

    await login(team[0].auth.email, team[0].auth.password, async_client)
    response = await approve_request(auth.id, async_client)
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_get_requests_negative(async_client, team):
    await login(team[1].auth.email, team[1].auth.password, async_client)
    response = await get_requests(team[1].auth.id, async_client)
    assert response.status_code == 403

    await login(team[0].auth.email, team[0].auth.password, async_client)
    response = await get_requests(team[-1].auth.id, async_client)
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_create_user_with_coach_email_not_found(
    async_client, auth, user
):
    await login(auth.email, auth.password, async_client)
    user.coach_email = "nocoach@example.com"
    response = await create_user(user, async_client)

    assert response.status_code == 400


@pytest.mark.asyncio
async def test_create_user_with_coach_email_not_a_coach(
    async_client, auth, user, team
):
    await login(auth.email, auth.password, async_client)
    user.coach_email = team[1].auth.email
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
