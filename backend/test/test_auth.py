import pytest

from test.helpers import (
    basic_email,
    basic_password,
    create_account,
    delete_account,
    forgot_password,
    get_me,
    get_user,
    login,
    reset_password,
    verify_email,
)


@pytest.mark.asyncio
async def test_register_post_positive(async_client):
    response = await create_account(
        basic_email, basic_password, async_client
    )

    assert response.status_code == 201
    assert response.json()["is_verified"] is False


@pytest.mark.asyncio
async def test_register_post_negative(async_client):
    await create_account(basic_email, basic_password, async_client)
    response = await create_account(
        basic_email, basic_password, async_client
    )
    assert response.status_code == 400

    response = await create_account(
        "test", basic_password, async_client
    )
    assert response.status_code == 422

    response = await create_account(basic_email, "test", async_client)
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_login_post_positive(async_client):
    auth = await create_account(
        basic_email, basic_password, async_client
    )
    id = auth.json()["id"]
    await verify_email(basic_email, async_client)
    response = await login(basic_email, basic_password, async_client)
    assert response.json()["id"] == id

    assert "access_token" in async_client.cookies
    assert async_client.cookies["access_token"] != ""


@pytest.mark.asyncio
async def test_login_post_negative(async_client):
    response = await login(basic_email, basic_password, async_client)
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_login_unverified_forbidden(async_client):
    await create_account(basic_email, basic_password, async_client)
    response = await login(basic_email, basic_password, async_client)
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_me_positive(async_client):
    auth = await create_account(
        basic_email, basic_password, async_client
    )
    id = auth.json()["id"]
    await verify_email(basic_email, async_client)
    await login(basic_email, basic_password, async_client)

    response = await get_me(async_client)
    assert response.status_code == 200
    assert response.json()["id"] == id
    assert response.json()["email"] == basic_email


@pytest.mark.asyncio
async def test_me_unauthorized(async_client):
    response = await get_me(async_client)
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_reset_password_flow(async_client):
    new_password = "NewPass123"
    await create_account(basic_email, basic_password, async_client)
    await verify_email(basic_email, async_client)

    response = await forgot_password(basic_email, async_client)
    assert response.status_code == 200

    response = await reset_password(
        basic_email, new_password, async_client
    )
    assert response.status_code == 200

    response = await login(basic_email, basic_password, async_client)
    assert response.status_code == 401

    response = await login(basic_email, new_password, async_client)
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_forgot_password_unknown_email(async_client):
    response = await forgot_password("nobody@example.com", async_client)
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_reset_password_wrong_code(async_client):
    await create_account(basic_email, basic_password, async_client)
    await verify_email(basic_email, async_client)
    await forgot_password(basic_email, async_client)

    response = await reset_password(
        basic_email, "NewPass123", async_client, code="000000"
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_reset_password_weak_password(async_client):
    await create_account(basic_email, basic_password, async_client)
    await verify_email(basic_email, async_client)
    await forgot_password(basic_email, async_client)

    response = await reset_password(basic_email, "short", async_client)
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_logout_post(async_client):
    auth = await create_account(
        basic_email, basic_password, async_client
    )
    id = auth.json()["id"]
    await verify_email(basic_email, async_client)
    response = await login(basic_email, basic_password, async_client)
    assert response.json()["id"] == id

    response = await async_client.post("/api/auth/logout")

    assert "access_token" not in async_client.cookies
    assert response.json()["message"] == "Logged out"


@pytest.mark.asyncio
async def test_update_put_positive(async_client):
    email = "test1@gmail.com"
    password = "1816bg123Qaz-"

    auth = await create_account(
        basic_email, basic_password, async_client
    )
    id = auth.json()["id"]
    await verify_email(basic_email, async_client)
    await login(basic_email, basic_password, async_client)
    response = await async_client.put(
        f"/api/auth/{id}",
        json={"email": email, "password": password},
    )
    assert response.json()["id"] == id
    assert response.json()["email"] == email


@pytest.mark.asyncio
async def test_update_put_negative(async_client):
    await create_account(basic_email, basic_password, async_client)
    await verify_email(basic_email, async_client)
    await login(basic_email, basic_password, async_client)

    response = await async_client.put(
        f"/api/auth/{-1}",
        json={"email": basic_email, "password": basic_password},
    )
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_delete_auth_delete_positive(async_client):
    auth = await create_account(
        basic_email, basic_password, async_client
    )
    id = auth.json()["id"]
    await verify_email(basic_email, async_client)
    await login(basic_email, basic_password, async_client)

    response = await delete_account(id, async_client)
    assert response.status_code == 204

    response = await get_user(id, async_client)
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_delete_auth_delete_negative(async_client):
    await create_account(basic_email, basic_password, async_client)
    await verify_email(basic_email, async_client)
    await login(basic_email, basic_password, async_client)

    response = await delete_account(-1, async_client)
    assert response.status_code == 403
