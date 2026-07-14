from typing import Annotated

from fastapi import Depends

from src.common.database import SessionDependency
from src.statistics.service import StatisticsService


async def get_statistics_service(
    session: SessionDependency,
) -> StatisticsService:
    return StatisticsService(session)


StatisticsServiceDependency = Annotated[
    StatisticsService, Depends(get_statistics_service)
]
