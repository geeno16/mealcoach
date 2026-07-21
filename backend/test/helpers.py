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


_sent_codes: dict[str, str] = {}


async def verify_email(
    email: str, async_client, code: str | None = None
):
    if code is None:
        code = _sent_codes[email]
    return await async_client.post(
        "/api/auth/verify-email",
        json={
            "email": email,
            "code": code,
        },
    )


async def get_me(async_client):
    return await async_client.get("/api/auth/me")


async def get_notifications(async_client):
    return await async_client.get("/api/notifications")


async def login(email: str, password: str, async_client):
    return await async_client.post(
        "/api/auth/login",
        json={
            "email": email,
            "password": password,
        },
    )


async def resend_code(email: str, password: str, async_client):
    return await async_client.post(
        "/api/auth/resend-code",
        json={
            "email": email,
            "password": password,
        },
    )


async def forgot_password(email: str, async_client):
    return await async_client.post(
        "/api/auth/forgot-password",
        json={"email": email},
    )


async def reset_password(
    email: str, password: str, async_client, code: str | None = None
):
    if code is None:
        code = _sent_codes[email]
    return await async_client.post(
        "/api/auth/reset-password",
        json={"email": email, "code": code, "password": password},
    )


async def signup(email: str, password: str, async_client):
    await create_account(email, password, async_client)
    return await verify_email(email, async_client)


async def delete_account(id: int, async_client):
    return await async_client.delete(f"/api/auth/{id}")


async def get_user(id: int, async_client):
    return await async_client.get(f"/api/users/{id}")


async def get_trainees(coach_id: int, async_client):
    return await async_client.get(
        "/api/users", params={"coach_id": coach_id}
    )


async def create_user(data: UserWrite, async_client):
    return await async_client.post(
        "/api/users", json=data.model_dump(mode="json")
    )


async def update_user(id: int, data, async_client):
    return await async_client.put(
        f"/api/users/{id}", json=data.model_dump(mode="json")
    )


async def get_requests(coach_id: int, async_client):
    return await async_client.get(f"/api/users/{coach_id}/requests")


async def request_coach(id: int, coach_email: str, async_client):
    return await async_client.post(
        f"/api/users/{id}/request-coach",
        json={"coach_email": coach_email},
    )


async def approve_request(trainee_id: int, async_client):
    return await async_client.post(f"/api/users/{trainee_id}/approve")


async def delete_coach(trainee_id: int, async_client):
    return await async_client.delete(f"/api/users/{trainee_id}/coach")


async def get_post(id: int, async_client):
    return await async_client.get(f"/api/posts/{id}")


async def get_posts(auth_id: int, async_client):
    return await async_client.get(
        "/api/posts", params={"auth_id": auth_id}
    )


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


async def get_statistics(id: int, async_client):
    return await async_client.get(f"/api/users/{id}/statistics")


async def get_picture(id: int, async_client, headers=None):
    return await async_client.get(
        f"/api/pictures/{id}", headers=headers
    )


_JPEG_HEADERS = {"Content-Type": "image/jpeg"}


async def set_meal_picture(meal_id: int, data: bytes, async_client):
    return await async_client.put(
        f"/api/meals/{meal_id}/picture",
        content=data,
        headers=_JPEG_HEADERS,
    )


async def set_avatar(user_id: int, data: bytes, async_client):
    return await async_client.put(
        f"/api/users/{user_id}/avatar",
        content=data,
        headers=_JPEG_HEADERS,
    )


async def delete_picture(id: int, async_client):
    return await async_client.delete(f"/api/pictures/{id}")
