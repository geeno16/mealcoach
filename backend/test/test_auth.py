import pytest

basic_email = "test@gmail.com"
basic_password = "1816bg123Qaz"


async def create_account(email: str, password: str, async_client):
    return await async_client.post(
        "/api/auth",
        json={
            "email": email,
            "password": password,
        },
    )


async def login(email: str, password: str, async_client):
    return await async_client.post(
        "/api/auth/login",
        json={
            "email": email,
            "password": password,
        },
    )


@pytest.mark.asyncio
async def test_register_post_positive(async_client):
    response = await create_account(
        basic_email, basic_password, async_client
    )

    assert response.status_code == 201
    assert response.json()


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
    id = auth.json()
    response = await login(basic_email, basic_password, async_client)
    assert response.json()["id"] == id

    assert "access_token" in async_client.cookies
    assert async_client.cookies["access_token"] != ""


@pytest.mark.asyncio
async def test_login_post_negative(async_client):
    response = await login(basic_email, basic_password, async_client)
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_logout_post(async_client):
    auth = await create_account(
        basic_email, basic_password, async_client
    )
    id = auth.json()
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
    id = auth.json()
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
    await login(basic_email, basic_password, async_client)

    response = await async_client.put(
        f"/api/auth/{-1}",
        json={"email": basic_email, "password": basic_password},
    )
    assert response.status_code == 403
