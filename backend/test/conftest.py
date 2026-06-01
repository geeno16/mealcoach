import asyncio
from collections.abc import AsyncGenerator
from dataclasses import dataclass

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
)

from src import app
from src.auth import Auth, AuthRepository, AuthWrite
from src.common import create_tables, engine, get_session
from src.user import User, UserRepository, UserRole, UserWrite
from test.helpers import basic_email, basic_password


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="session", autouse=True)
async def setup_tables():
    await create_tables()
    await engine.dispose()


@pytest_asyncio.fixture
async def db_session():
    async with engine.connect() as connection:
        transaction = await connection.begin()

        session_factory = async_sessionmaker(
            bind=connection,
            class_=AsyncSession,
            expire_on_commit=False,
        )

        session = session_factory()

        try:
            yield session
        finally:
            await session.close()
            await transaction.rollback()


@pytest_asyncio.fixture
async def async_client(db_session: AsyncSession):
    async def override_get_session():
        yield db_session

    app.dependency_overrides[get_session] = override_get_session

    async with AsyncClient(
        transport=ASGITransport(app=app),  # ty: ignore[invalid-argument-type]
        base_url="http://test",
    ) as client:
        yield client

    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def auth(db_session: AsyncSession) -> AsyncGenerator[Auth, None]:
    repo = AuthRepository(db_session)

    auth = await repo.create(
        AuthWrite(email=basic_email, password=basic_password)
    )

    yield auth


@pytest_asyncio.fixture
async def user(auth: Auth) -> AsyncGenerator[UserWrite, None]:
    new_user = UserWrite(
        auth_id=auth.id, role=UserRole.trainee, name="geeno16"
    )

    yield new_user


@dataclass
class AuthUserPair:
    auth: Auth
    user: User


@pytest_asyncio.fixture
async def team(
    db_session: AsyncSession,
) -> AsyncGenerator[list[AuthUserPair], None]:
    auth_repo = AuthRepository(db_session)
    user_repo = UserRepository(db_session)

    coach_auth_list = [
        await auth_repo.create(
            AuthWrite(
                email=f"coach{i}@test.com", password=basic_password
            )
        )
        for i in range(2)
    ]
    coach_user_list = [
        await user_repo.create(
            UserWrite(
                auth_id=coach_auth_list[i].id,
                role=UserRole.coach,
                name="Coach",
            )
        )
        for i in range(2)
    ]

    pairs: list[AuthUserPair] = [
        AuthUserPair(auth=coach_auth_list[0], user=coach_user_list[0])
    ]

    for i in range(3):
        trainee_auth = await auth_repo.create(
            AuthWrite(
                email=f"trainee{i}@test.com", password=basic_password
            )
        )
        trainee_user = await user_repo.create(
            UserWrite(
                auth_id=trainee_auth.id,
                role=UserRole.trainee,
                name=f"Trainee{i}",
                coach_id=coach_auth_list[0].id,
            )
        )
        pairs.append(AuthUserPair(auth=trainee_auth, user=trainee_user))

    pairs.append(
        AuthUserPair(auth=coach_auth_list[1], user=coach_user_list[1])
    )

    yield pairs
