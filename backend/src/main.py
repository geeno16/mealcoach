from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, HTTPException, status
from fastapi.responses import FileResponse

from src.auth import auth_router
from src.common import create_database_if_not_exists, create_tables
from src.email_code import EmailCode  # noqa: F401
from src.picture import Picture, picture_router  # noqa: F401
from src.post import Post, post_router  # noqa: F401
from src.statistics import statistics_router
from src.user import User, user_router  # noqa: F401

FRONTEND_DIST = Path(__file__).resolve().parents[2] / "frontend" / "dist"
FRONTEND_INDEX = FRONTEND_DIST / "index.html"


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
app.include_router(statistics_router)

if FRONTEND_DIST.is_dir():

    @app.get("/{full_path:path}")
    async def serve_spa(full_path: str) -> FileResponse:
        if full_path.startswith("api/"):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

        candidate = (FRONTEND_DIST / full_path).resolve()
        if candidate.is_file() and FRONTEND_DIST in candidate.parents:
            return FileResponse(candidate)

        return FileResponse(FRONTEND_INDEX)
