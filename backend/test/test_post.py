import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession

from src.post import PostRepository, PostWrite
from src.user import UserRepository, UserWrite
from test.helpers import (
    create_post,
    delete_post,
    get_post,
    get_posts,
    login,
    update_post,
)


@pytest_asyncio.fixture
async def post_data(db_session: AsyncSession, auth, user: UserWrite):
    await UserRepository(db_session).create(user)
    schema = PostWrite(auth_id=auth.id, name="Test post")
    yield schema


@pytest_asyncio.fixture
async def post(db_session: AsyncSession, post_data):
    repo = PostRepository(db_session)
    model = await repo.create(post_data)
    yield model


@pytest_asyncio.fixture
async def trainee_post(db_session: AsyncSession, team):
    repo = PostRepository(db_session)
    model = await repo.create(
        PostWrite(auth_id=team[1].auth.id, name="Trainee post")
    )
    yield model


@pytest.mark.asyncio
async def test_create_post_post_positive(async_client, auth, post_data):
    await login(auth.email, auth.password, async_client)
    response = await create_post(post_data, async_client)

    assert response.status_code == 201
    assert response.json()["comment"] is None
    assert response.json()["mark"] is None


@pytest.mark.asyncio
async def test_create_post_post_negative(
    async_client, auth, post_data, team
):
    await login(auth.email, auth.password, async_client)
    post_data.auth_id = -1
    response = await create_post(post_data, async_client)
    assert response.status_code == 403

    await login(team[0].auth.email, team[0].auth.password, async_client)
    response = await create_post(
        PostWrite(auth_id=team[0].auth.id, name="Coach post"),
        async_client,
    )
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_get_post_get_positive(async_client, team, trainee_post):
    await login(team[1].auth.email, team[1].auth.password, async_client)
    response = await get_post(trainee_post.id, async_client)
    assert response.status_code == 200
    assert response.json()["id"] == trainee_post.id

    await login(team[0].auth.email, team[0].auth.password, async_client)
    response = await get_post(trainee_post.id, async_client)
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_get_post_get_negative(async_client, team, trainee_post):
    await login(team[2].auth.email, team[2].auth.password, async_client)
    response = await get_post(trainee_post.id, async_client)
    assert response.status_code == 403

    await login(
        team[-1].auth.email, team[-1].auth.password, async_client
    )
    response = await get_post(trainee_post.id, async_client)
    assert response.status_code == 403

    await login(team[1].auth.email, team[1].auth.password, async_client)
    response = await get_post(-1, async_client)
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_get_all_posts_get_positive(
    async_client, team, trainee_post
):
    await login(team[1].auth.email, team[1].auth.password, async_client)
    response = await get_posts(team[1].auth.id, async_client)
    assert response.status_code == 200
    assert len(response.json()) == 1

    await login(team[0].auth.email, team[0].auth.password, async_client)
    response = await get_posts(team[1].auth.id, async_client)
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_get_all_posts_get_negative(
    async_client, team, trainee_post
):
    await login(team[2].auth.email, team[2].auth.password, async_client)
    response = await get_posts(team[1].auth.id, async_client)
    assert response.status_code == 403

    await login(
        team[-1].auth.email, team[-1].auth.password, async_client
    )
    response = await get_posts(team[1].auth.id, async_client)
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_update_post_put_positive(
    async_client, auth, post, team, trainee_post
):
    await login(auth.email, auth.password, async_client)
    response = await update_post(
        post.id,
        PostWrite(
            auth_id=auth.id, name="Updated name", comment="ignored"
        ),
        async_client,
    )
    assert response.status_code == 200
    assert response.json()["name"] == "Updated name"
    assert response.json()["comment"] is None

    await login(team[0].auth.email, team[0].auth.password, async_client)
    response = await update_post(
        trainee_post.id,
        PostWrite(
            auth_id=team[1].auth.id,
            name="ignored",
            comment="Coach comment",
            mark=5,
        ),
        async_client,
    )
    assert response.status_code == 200
    assert response.json()["comment"] == "Coach comment"
    assert response.json()["mark"] == 5
    assert response.json()["name"] == "Trainee post"


@pytest.mark.asyncio
async def test_update_post_put_negative(
    async_client, team, trainee_post
):
    await login(team[2].auth.email, team[2].auth.password, async_client)
    response = await update_post(
        trainee_post.id,
        PostWrite(auth_id=team[1].auth.id, name="hack"),
        async_client,
    )
    assert response.status_code == 403

    await login(
        team[-1].auth.email, team[-1].auth.password, async_client
    )
    response = await update_post(
        trainee_post.id,
        PostWrite(
            auth_id=team[1].auth.id,
            name=trainee_post.name,
            comment="hack",
        ),
        async_client,
    )
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_delete_post_delete_positive(async_client, auth, post):
    await login(auth.email, auth.password, async_client)
    response = await delete_post(post.id, async_client)
    assert response.status_code == 204

    response = await get_post(post.id, async_client)
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_delete_post_delete_negative(
    async_client, team, trainee_post
):
    await login(team[0].auth.email, team[0].auth.password, async_client)
    response = await delete_post(trainee_post.id, async_client)
    assert response.status_code == 403

    await login(team[2].auth.email, team[2].auth.password, async_client)
    response = await delete_post(trainee_post.id, async_client)
    assert response.status_code == 403
