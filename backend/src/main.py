from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from src.auth import auth_router
from src.common import create_database_if_not_exists, create_tables
from src.picture import Picture  # noqa: F401
from src.post import Post, post_router  # noqa: F401
from src.user import User, user_router  # noqa: F401


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    await create_database_if_not_exists()
    await create_tables()
    yield


app = FastAPI(title="Mealcoach API", lifespan=lifespan)
app.include_router(auth_router)
app.include_router(user_router)
app.include_router(post_router)
