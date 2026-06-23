from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from src.auth import auth_router
from src.common import create_database_if_not_exists, create_tables
from src.picture import Picture, picture_router  # noqa: F401
from src.post import Post, post_router  # noqa: F401
from src.user import User, user_router  # noqa: F401

FRONTEND_DIST = Path(__file__).resolve().parents[2] / "frontend" / "dist"


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    await create_database_if_not_exists()
    await create_tables()
    yield


app = FastAPI(title="Mealcoach API", lifespan=lifespan)
app.include_router(auth_router)
app.include_router(user_router)
app.include_router(post_router)
app.include_router(picture_router)

# Раздача собранного фронта (prod). Монтируется последним, после всех
# API-роутеров, и только если фронт собран — иначе dev/тесты падали бы на
# отсутствующей директории dist. html=True даёт SPA-fallback на index.html.
if FRONTEND_DIST.is_dir():
    app.mount(
        "/",
        StaticFiles(directory=FRONTEND_DIST, html=True),
        name="static",
    )
