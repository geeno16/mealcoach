import io
from datetime import timedelta

import pytest
import pytest_asyncio
from PIL import Image
from sqlalchemy.ext.asyncio import AsyncSession

from src.picture import Picture, PictureRepository, PictureWrite
from src.post import (
    MealRepository,
    MealWrite,
    PostRepository,
    PostWrite,
)
from src.user import UserRepository, UserWrite
from test.helpers import (
    delete_account,
    delete_picture,
    delete_post,
    get_picture,
    login,
    set_avatar,
    set_meal_picture,
)


def _png_bytes(width: int, height: int) -> bytes:
    buffer = io.BytesIO()
    Image.new("RGB", (width, height), (200, 100, 50)).save(
        buffer, format="PNG"
    )
    return buffer.getvalue()


IMAGE_WIDTH = 100
IMAGE_HEIGHT = 80
NEW_IMAGE_WIDTH = 64
NEW_IMAGE_HEIGHT = 48

IMAGE = _png_bytes(IMAGE_WIDTH, IMAGE_HEIGHT)
NEW_IMAGE = _png_bytes(NEW_IMAGE_WIDTH, NEW_IMAGE_HEIGHT)
NOT_AN_IMAGE = b"not-an-image"


async def _set_avatar(db_session: AsyncSession, auth_id: int):
    user_repo = UserRepository(db_session)
    picture = await PictureRepository(db_session).create(
        PictureWrite(data=IMAGE, width=IMAGE_WIDTH, height=IMAGE_HEIGHT)
    )
    user = await user_repo.get_by_id(auth_id)
    assert user is not None
    user.picture_id = picture.id
    await user_repo.update_by_id(
        auth_id, UserWrite.model_validate(user, from_attributes=True)
    )
    return picture


async def _set_meal_picture(db_session: AsyncSession, meal_id: int):
    meal_repo = MealRepository(db_session)
    picture = await PictureRepository(db_session).create(
        PictureWrite(data=IMAGE, width=IMAGE_WIDTH, height=IMAGE_HEIGHT)
    )
    meal = await meal_repo.get_by_id(meal_id)
    assert meal is not None
    meal.picture_id = picture.id
    await db_session.commit()
    return picture


@pytest_asyncio.fixture
async def trainee(db_session: AsyncSession, auth, user: UserWrite):
    await UserRepository(db_session).create(user)
    yield auth


@pytest_asyncio.fixture
async def avatar(trainee, db_session: AsyncSession):
    yield await _set_avatar(db_session, trainee.id)


@pytest_asyncio.fixture
async def team_avatar(db_session: AsyncSession, team):
    yield await _set_avatar(db_session, team[1].auth.id)


@pytest_asyncio.fixture
async def trainee_post(db_session: AsyncSession, team):
    model = await PostRepository(db_session).create(
        PostWrite(
            auth_id=team[1].auth.id,
            name="Trainee post",
            meals=[MealWrite(name="Oatmeal")],
        )
    )
    yield model


@pytest_asyncio.fixture
async def meal(trainee_post):
    yield trainee_post.meals[0]


@pytest_asyncio.fixture
async def meal_picture(db_session: AsyncSession, meal):
    yield await _set_meal_picture(db_session, meal.id)


@pytest.mark.asyncio
async def test_set_avatar_positive(async_client, trainee):
    await login(trainee.email, trainee.password, async_client)
    response = await set_avatar(trainee.id, IMAGE, async_client)
    assert response.status_code == 200
    body = response.json()
    assert isinstance(body["id"], int)
    assert body["width"] == IMAGE_WIDTH
    assert body["height"] == IMAGE_HEIGHT


@pytest.mark.asyncio
async def test_set_avatar_negative(async_client, trainee, team):
    await login(trainee.email, trainee.password, async_client)
    response = await set_avatar(-1, IMAGE, async_client)
    assert response.status_code == 403

    await login(team[2].auth.email, team[2].auth.password, async_client)
    response = await set_avatar(trainee.id, IMAGE, async_client)
    assert response.status_code == 403

    await login(trainee.email, trainee.password, async_client)
    response = await set_avatar(trainee.id, NOT_AN_IMAGE, async_client)
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_set_meal_picture_positive(async_client, team, meal):
    await login(team[1].auth.email, team[1].auth.password, async_client)
    response = await set_meal_picture(meal.id, IMAGE, async_client)
    assert response.status_code == 200
    body = response.json()
    picture_id = body["id"]
    assert isinstance(picture_id, int)
    assert body["width"] == IMAGE_WIDTH
    assert body["height"] == IMAGE_HEIGHT

    response = await get_picture(picture_id, async_client)
    assert response.status_code == 200
    assert response.content == IMAGE

    response = await set_meal_picture(meal.id, NEW_IMAGE, async_client)
    assert response.status_code == 200
    body = response.json()
    assert body["id"] == picture_id
    assert body["width"] == NEW_IMAGE_WIDTH
    assert body["height"] == NEW_IMAGE_HEIGHT

    response = await get_picture(picture_id, async_client)
    assert response.content == NEW_IMAGE


@pytest.mark.asyncio
async def test_set_meal_picture_negative(async_client, team, meal):
    await login(team[2].auth.email, team[2].auth.password, async_client)
    response = await set_meal_picture(meal.id, IMAGE, async_client)
    assert response.status_code == 403

    await login(team[0].auth.email, team[0].auth.password, async_client)
    response = await set_meal_picture(meal.id, IMAGE, async_client)
    assert response.status_code == 403

    await login(team[1].auth.email, team[1].auth.password, async_client)
    response = await set_meal_picture(-1, IMAGE, async_client)
    assert response.status_code == 404

    response = await set_meal_picture(
        meal.id, NOT_AN_IMAGE, async_client
    )
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_get_picture_get_positive(
    async_client, team, team_avatar, meal_picture
):
    await login(team[1].auth.email, team[1].auth.password, async_client)
    response = await get_picture(team_avatar.id, async_client)
    assert response.status_code == 200
    assert response.content == IMAGE

    response = await get_picture(meal_picture.id, async_client)
    assert response.status_code == 200

    await login(team[0].auth.email, team[0].auth.password, async_client)
    response = await get_picture(team_avatar.id, async_client)
    assert response.status_code == 200

    response = await get_picture(meal_picture.id, async_client)
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_get_picture_get_negative(
    async_client, team, team_avatar, meal_picture
):
    await login(team[2].auth.email, team[2].auth.password, async_client)
    response = await get_picture(team_avatar.id, async_client)
    assert response.status_code == 403

    response = await get_picture(meal_picture.id, async_client)
    assert response.status_code == 403

    await login(
        team[-1].auth.email, team[-1].auth.password, async_client
    )
    response = await get_picture(team_avatar.id, async_client)
    assert response.status_code == 403

    response = await get_picture(meal_picture.id, async_client)
    assert response.status_code == 403

    await login(team[1].auth.email, team[1].auth.password, async_client)
    response = await get_picture(-1, async_client)
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_get_picture_get_cache_headers(
    async_client, team, db_session, meal_picture
):
    await login(team[1].auth.email, team[1].auth.password, async_client)
    response = await get_picture(meal_picture.id, async_client)
    assert response.status_code == 200
    assert "max-age" in response.headers["cache-control"]
    etag = response.headers["etag"]
    assert etag

    response = await get_picture(
        meal_picture.id,
        async_client,
        headers={"If-None-Match": etag},
    )
    assert response.status_code == 304
    assert response.content == b""

    meal_picture.updated_at += timedelta(seconds=1)
    await db_session.commit()

    response = await get_picture(
        meal_picture.id,
        async_client,
        headers={"If-None-Match": etag},
    )
    assert response.status_code == 200
    assert response.headers["etag"] != etag


@pytest.mark.asyncio
async def test_delete_picture_delete_positive(
    async_client, trainee, avatar, db_session, team, meal, meal_picture
):
    await login(trainee.email, trainee.password, async_client)
    response = await delete_picture(avatar.id, async_client)
    assert response.status_code == 204

    response = await get_picture(avatar.id, async_client)
    assert response.status_code == 404

    owner = await UserRepository(db_session).get_by_id(trainee.id)
    assert owner is not None
    assert owner.picture_id is None

    await login(team[1].auth.email, team[1].auth.password, async_client)
    response = await delete_picture(meal_picture.id, async_client)
    assert response.status_code == 204

    refreshed = await MealRepository(db_session).get_by_id(meal.id)
    assert refreshed is not None
    assert refreshed.picture_id is None


@pytest.mark.asyncio
async def test_delete_picture_delete_negative(
    async_client, team, team_avatar, meal_picture
):
    await login(team[0].auth.email, team[0].auth.password, async_client)
    response = await delete_picture(team_avatar.id, async_client)
    assert response.status_code == 403

    response = await delete_picture(meal_picture.id, async_client)
    assert response.status_code == 403

    await login(team[2].auth.email, team[2].auth.password, async_client)
    response = await delete_picture(meal_picture.id, async_client)
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_delete_post_cascades_pictures(
    async_client, team, trainee_post, meal_picture, db_session
):
    await login(team[1].auth.email, team[1].auth.password, async_client)
    response = await delete_post(trainee_post.id, async_client)
    assert response.status_code == 204
    db_session.expunge_all()
    picture = await db_session.get(Picture, meal_picture.id)
    assert picture is None


@pytest.mark.asyncio
async def test_delete_account_removes_avatar(
    async_client, trainee, avatar, db_session
):
    await login(trainee.email, trainee.password, async_client)
    response = await delete_account(trainee.id, async_client)
    assert response.status_code == 204

    picture = await PictureRepository(db_session).get_by_id(avatar.id)
    assert picture is None
