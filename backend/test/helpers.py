from src.post import PostWrite
from src.user import UserWrite

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


async def delete_account(id: int, async_client):
    return await async_client.delete(f"/api/auth/{id}")


async def get_user(id: int, async_client):
    return await async_client.get(f"/api/users/{id}")


async def get_trainees(coach_id: int, async_client):
    return await async_client.get(f"/api/users/all/{coach_id}")


async def create_user(data: UserWrite, async_client):
    return await async_client.post(
        "/api/users", json=data.model_dump(mode="json")
    )


async def update_user(id: int, data, async_client):
    return await async_client.put(
        f"/api/users/{id}", json=data.model_dump(mode="json")
    )


async def get_post(id: int, async_client):
    return await async_client.get(f"/api/posts/{id}")


async def get_posts(auth_id: int, async_client):
    return await async_client.get(f"/api/posts/all/{auth_id}")


async def create_post(data: PostWrite, async_client):
    return await async_client.post(
        "/api/posts", json=data.model_dump(mode="json")
    )


async def update_post(id: int, data: PostWrite, async_client):
    return await async_client.put(
        f"/api/posts/{id}", json=data.model_dump(mode="json")
    )


async def delete_post(id: int, async_client):
    return await async_client.delete(f"/api/posts/{id}")
