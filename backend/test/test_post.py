import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession

from src.picture import PictureRepository, PictureWrite
from src.post import MealWrite, PostRepository, PostWrite
from src.user import UserRepository, UserWrite
from test.helpers import (
    create_post,
    delete_post,
    get_picture,
    get_post,
    get_posts,
    login,
    update_post,
)


@pytest_asyncio.fixture
async def post_data(db_session: AsyncSession, auth, user: UserWrite):
    await UserRepository(db_session).create(user)
    schema = PostWrite(
        auth_id=auth.id,
        name="Test post",
        meals=[MealWrite(name="Egg", cal=100)],
    )
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
        PostWrite(
            auth_id=team[1].auth.id,
            name="Trainee post",
            meals=[MealWrite(name="Oatmeal", cal=250)],
        )
    )
    yield model


@pytest.mark.asyncio
async def test_create_post_post_positive(async_client, auth, post_data):
    await login(auth.email, auth.password, async_client)
    response = await create_post(post_data, async_client)

    assert response.status_code == 201
    body = response.json()
    assert body["comment"] is None
    assert body["mark"] is None
    assert len(body["meals"]) == 1
    assert body["meals"][0]["name"] == "Egg"
    assert body["meals"][0]["cal"] == 100
    assert isinstance(body["meals"][0]["id"], int)
    assert body["meals"][0]["picture_id"] is None


@pytest.mark.asyncio
async def test_create_post_post_meals_boundaries(
    async_client, auth, user: UserWrite, db_session: AsyncSession
):
    await UserRepository(db_session).create(user)
    await login(auth.email, auth.password, async_client)

    response = await create_post(
        PostWrite(auth_id=auth.id, name="No meals", meals=[]),
        async_client,
    )
    assert response.status_code == 400

    response = await create_post(
        PostWrite(
            auth_id=auth.id,
            name="Too many meals",
            meals=[MealWrite(name=f"Meal {i}") for i in range(4)],
        ),
        async_client,
    )
    assert response.status_code == 400

    response = await create_post(
        PostWrite(
            auth_id=auth.id,
            name="Three meals",
            meals=[MealWrite(name=f"Meal {i}") for i in range(3)],
        ),
        async_client,
    )
    assert response.status_code == 201
    assert len(response.json()["meals"]) == 3


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
        PostWrite(
            auth_id=team[0].auth.id,
            name="Coach post",
            meals=[MealWrite(name="Steak")],
        ),
        async_client,
    )
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_get_post_get_positive(async_client, team, trainee_post):
    await login(team[1].auth.email, team[1].auth.password, async_client)
    response = await get_post(trainee_post.id, async_client)
    assert response.status_code == 200
    assert response.json()["id"] == trainee_post.id
    assert response.json()["meals"][0]["name"] == "Oatmeal"

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
async def test_update_post_put_owner(async_client, auth, post):
    await login(auth.email, auth.password, async_client)
    response = await update_post(
        post.id,
        PostWrite(
            auth_id=auth.id,
            name="Updated name",
            description="Updated description",
            comment="Own comment",
            mark=4,
            meals=[
                MealWrite(
                    id=post.meals[0].id, name="Updated meal", cal=100
                )
            ],
        ),
        async_client,
    )
    assert response.status_code == 200
    body = response.json()
    assert body["name"] == "Updated name"
    assert body["description"] == "Updated description"
    assert body["comment"] == "Own comment"
    assert body["mark"] == 4
    assert len(body["meals"]) == 1
    assert body["meals"][0]["name"] == "Updated meal"
    assert body["meals"][0]["cal"] == 100


@pytest.mark.asyncio
async def test_update_post_put_owner_multi_meal(
    async_client, auth, user: UserWrite, db_session: AsyncSession
):
    await UserRepository(db_session).create(user)
    repo = PostRepository(db_session)
    multi_post = await repo.create(
        PostWrite(
            auth_id=auth.id,
            name="Multi",
            meals=[
                MealWrite(name="First", cal=100),
                MealWrite(name="Second", cal=200),
            ],
        )
    )

    await login(auth.email, auth.password, async_client)
    response = await update_post(
        multi_post.id,
        PostWrite(
            auth_id=auth.id,
            name="Multi",
            meals=[
                MealWrite(
                    id=multi_post.meals[0].id,
                    name="First updated",
                    cal=150,
                ),
                MealWrite(
                    id=multi_post.meals[1].id,
                    name="Second updated",
                    cal=250,
                ),
            ],
        ),
        async_client,
    )
    assert response.status_code == 200
    meals = response.json()["meals"]
    assert meals[0]["name"] == "First updated"
    assert meals[0]["cal"] == 150
    assert meals[1]["name"] == "Second updated"
    assert meals[1]["cal"] == 250


@pytest.mark.asyncio
async def test_update_post_put_owner_preserves_picture(
    async_client, auth, post, db_session: AsyncSession
):
    picture = await PictureRepository(db_session).create(
        PictureWrite(data=b"\xff\xd8\xff\xe0-fake-jpeg-bytes")
    )
    meal = post.meals[0]
    meal.picture_id = picture.id
    await db_session.commit()

    await login(auth.email, auth.password, async_client)
    response = await update_post(
        post.id,
        PostWrite(
            auth_id=auth.id,
            name=post.name,
            meals=[MealWrite(id=meal.id, name="Renamed", cal=100)],
        ),
        async_client,
    )
    assert response.status_code == 200
    assert response.json()["meals"][0]["name"] == "Renamed"
    assert response.json()["meals"][0]["picture_id"] == picture.id


@pytest.mark.asyncio
async def test_update_post_put_owner_add_meal(async_client, auth, post):
    await login(auth.email, auth.password, async_client)
    response = await update_post(
        post.id,
        PostWrite(
            auth_id=auth.id,
            name=post.name,
            meals=[
                MealWrite(id=post.meals[0].id, name="Egg", cal=100),
                MealWrite(name="Toast", cal=80),
            ],
        ),
        async_client,
    )
    assert response.status_code == 200
    meals = response.json()["meals"]
    assert len(meals) == 2
    assert meals[0]["id"] == post.meals[0].id
    assert meals[1]["name"] == "Toast"
    assert meals[1]["cal"] == 80
    assert isinstance(meals[1]["id"], int)
    assert meals[1]["id"] != post.meals[0].id


@pytest.mark.asyncio
async def test_update_post_put_owner_remove_meal(
    async_client, auth, user: UserWrite, db_session: AsyncSession
):
    await UserRepository(db_session).create(user)
    repo = PostRepository(db_session)
    multi_post = await repo.create(
        PostWrite(
            auth_id=auth.id,
            name="Multi",
            meals=[
                MealWrite(name="First", cal=100),
                MealWrite(name="Second", cal=200),
            ],
        )
    )
    picture = await PictureRepository(db_session).create(
        PictureWrite(data=b"\xff\xd8\xff\xe0-fake-jpeg-bytes")
    )
    removed_meal = multi_post.meals[1]
    removed_meal.picture_id = picture.id
    await db_session.commit()

    await login(auth.email, auth.password, async_client)
    response = await update_post(
        multi_post.id,
        PostWrite(
            auth_id=auth.id,
            name="Multi",
            meals=[
                MealWrite(
                    id=multi_post.meals[0].id, name="First", cal=100
                )
            ],
        ),
        async_client,
    )
    assert response.status_code == 200
    meals = response.json()["meals"]
    assert len(meals) == 1
    assert meals[0]["id"] == multi_post.meals[0].id

    picture_response = await get_picture(picture.id, async_client)
    assert picture_response.status_code == 404


@pytest.mark.asyncio
async def test_update_post_put_meals_boundaries(
    async_client, auth, post
):
    await login(auth.email, auth.password, async_client)

    response = await update_post(
        post.id,
        PostWrite(auth_id=auth.id, name=post.name, meals=[]),
        async_client,
    )
    assert response.status_code == 400

    response = await update_post(
        post.id,
        PostWrite(
            auth_id=auth.id,
            name=post.name,
            meals=[MealWrite(name=f"Meal {i}") for i in range(4)],
        ),
        async_client,
    )
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_update_post_put_coach(async_client, team, trainee_post):
    await login(team[0].auth.email, team[0].auth.password, async_client)
    response = await update_post(
        trainee_post.id,
        PostWrite(
            auth_id=team[1].auth.id,
            name="Coach renamed",
            comment="Coach comment",
            mark=5,
            meals=[MealWrite(name="Hacked meal")],
        ),
        async_client,
    )
    assert response.status_code == 200
    body = response.json()
    assert body["comment"] == "Coach comment"
    assert body["mark"] == 5
    assert body["name"] == "Coach renamed"
    assert len(body["meals"]) == 1
    assert body["meals"][0]["name"] == "Oatmeal"


@pytest.mark.asyncio
async def test_update_post_put_negative(
    async_client, team, trainee_post
):
    await login(team[2].auth.email, team[2].auth.password, async_client)
    response = await update_post(
        trainee_post.id,
        PostWrite(
            auth_id=team[1].auth.id,
            name="hack",
            meals=[MealWrite(name="hack")],
        ),
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
            meals=[MealWrite(name="hack")],
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
