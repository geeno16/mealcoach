from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from src.auth.route import auth_router
from src.common import create_database_if_not_exists, create_tables

app = FastAPI(title="Mealcoach API")


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    await create_database_if_not_exists()
    await create_tables()
    yield


app = FastAPI(title="Meald API", lifespan=lifespan)
app.include_router(auth_router)
