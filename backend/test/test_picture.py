import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession

from src.picture import Picture, PictureRepository, PictureWrite
from src.post import PostRepository, PostWrite
from src.user import UserRepository, UserWrite
from test.helpers import (
    create_post_picture,
    delete_account,
    delete_picture,
    delete_post,
    get_picture,
    get_post_pictures,
    login,
    set_avatar,
    update_picture,
)

IMAGE = b"\xff\xd8\xff\xe0-fake-jpeg-bytes"
NEW_IMAGE = b"\xff\xd8\xff\xe0-updated-bytes"


async def _set_avatar(db_session: AsyncSession, auth_id: int):
    user_repo = UserRepository(db_session)
    picture = await PictureRepository(db_session).create(
        PictureWrite(data=IMAGE)
    )
    user = await user_repo.get_by_id(auth_id)
    assert user is not None
    user.picture_id = picture.id
    await user_repo.update_by_id(
        auth_id, UserWrite.model_validate(user, from_attributes=True)
    )
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
        PostWrite(auth_id=team[1].auth.id, name="Trainee post")
    )
    yield model


@pytest_asyncio.fixture
async def post_picture(db_session: AsyncSession, trainee_post):
    model = await PictureRepository(db_session).create(
        PictureWrite(data=IMAGE, post_id=trainee_post.id)
    )
    yield model


@pytest.mark.asyncio
async def test_create_picture_post_positive(
    async_client, trainee, team, trainee_post
):
    await login(trainee.email, trainee.password, async_client)
    response = await set_avatar(trainee.id, IMAGE, async_client)
    assert response.status_code == 200
    assert isinstance(response.json()["id"], int)

    await login(team[1].auth.email, team[1].auth.password, async_client)
    response = await create_post_picture(
        trainee_post.id, IMAGE, async_client
    )
    assert response.status_code == 201


@pytest.mark.asyncio
async def test_create_picture_post_negative(
    async_client, trainee, team, trainee_post
):
    await login(trainee.email, trainee.password, async_client)
    response = await set_avatar(-1, IMAGE, async_client)
    assert response.status_code == 403

    response = await create_post_picture(-1, IMAGE, async_client)
    assert response.status_code == 404

    await login(team[2].auth.email, team[2].auth.password, async_client)
    response = await create_post_picture(
        trainee_post.id, IMAGE, async_client
    )
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_create_picture_post_limit(
    async_client, team, trainee_post
):
    await login(team[1].auth.email, team[1].auth.password, async_client)
    for _ in range(3):
        response = await create_post_picture(
            trainee_post.id, IMAGE, async_client
        )
        assert response.status_code == 201

    response = await create_post_picture(
        trainee_post.id, IMAGE, async_client
    )
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_get_picture_get_positive(
    async_client, team, team_avatar, post_picture
):
    await login(team[1].auth.email, team[1].auth.password, async_client)
    response = await get_picture(team_avatar.id, async_client)
    assert response.status_code == 200
    assert response.content == IMAGE

    response = await get_picture(post_picture.id, async_client)
    assert response.status_code == 200

    await login(team[0].auth.email, team[0].auth.password, async_client)
    response = await get_picture(team_avatar.id, async_client)
    assert response.status_code == 200

    response = await get_picture(post_picture.id, async_client)
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_get_picture_get_negative(
    async_client, team, team_avatar, post_picture
):
    await login(team[2].auth.email, team[2].auth.password, async_client)
    response = await get_picture(team_avatar.id, async_client)
    assert response.status_code == 403

    response = await get_picture(post_picture.id, async_client)
    assert response.status_code == 403

    await login(
        team[-1].auth.email, team[-1].auth.password, async_client
    )
    response = await get_picture(team_avatar.id, async_client)
    assert response.status_code == 403

    await login(team[1].auth.email, team[1].auth.password, async_client)
    response = await get_picture(-1, async_client)
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_get_post_pictures_positive(
    async_client, team, post_picture, trainee_post
):
    await login(team[1].auth.email, team[1].auth.password, async_client)
    response = await get_post_pictures(trainee_post.id, async_client)
    assert response.status_code == 200
    assert response.json() == [post_picture.id]

    await login(team[0].auth.email, team[0].auth.password, async_client)
    response = await get_post_pictures(trainee_post.id, async_client)
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_get_post_pictures_negative(
    async_client, team, trainee_post
):
    await login(team[2].auth.email, team[2].auth.password, async_client)
    response = await get_post_pictures(trainee_post.id, async_client)
    assert response.status_code == 403

    await login(team[1].auth.email, team[1].auth.password, async_client)
    response = await get_post_pictures(-1, async_client)
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_update_picture_put_positive(
    async_client, trainee, avatar, team, trainee_post, post_picture
):
    await login(trainee.email, trainee.password, async_client)
    response = await update_picture(avatar.id, NEW_IMAGE, async_client)
    assert response.status_code == 204

    response = await get_picture(avatar.id, async_client)
    assert response.content == NEW_IMAGE

    await login(team[1].auth.email, team[1].auth.password, async_client)
    response = await update_picture(
        post_picture.id, NEW_IMAGE, async_client
    )
    assert response.status_code == 204


@pytest.mark.asyncio
async def test_update_picture_put_negative(
    async_client, team, team_avatar, post_picture
):
    await login(team[0].auth.email, team[0].auth.password, async_client)
    response = await update_picture(
        team_avatar.id, NEW_IMAGE, async_client
    )
    assert response.status_code == 403

    await login(team[2].auth.email, team[2].auth.password, async_client)
    response = await update_picture(
        post_picture.id, NEW_IMAGE, async_client
    )
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_delete_picture_delete_positive(
    async_client, trainee, avatar, db_session, team, post_picture
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
    response = await delete_picture(post_picture.id, async_client)
    assert response.status_code == 204


@pytest.mark.asyncio
async def test_delete_picture_delete_negative(
    async_client, team, team_avatar, post_picture
):
    await login(team[0].auth.email, team[0].auth.password, async_client)
    response = await delete_picture(team_avatar.id, async_client)
    assert response.status_code == 403

    await login(team[2].auth.email, team[2].auth.password, async_client)
    response = await delete_picture(post_picture.id, async_client)
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_delete_post_cascades_pictures(
    async_client, team, trainee_post, post_picture, db_session
):
    await login(team[1].auth.email, team[1].auth.password, async_client)
    response = await delete_post(trainee_post.id, async_client)
    assert response.status_code == 204
    db_session.expunge_all()
    picture = await db_session.get(Picture, post_picture.id)
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
