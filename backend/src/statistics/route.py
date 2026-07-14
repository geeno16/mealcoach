from fastapi import APIRouter

from src.auth.dependency import CurrentAuthDependency
from src.statistics.dependency import StatisticsServiceDependency
from src.statistics.schema import StatisticsRead

statistics_router = APIRouter(prefix="/api/users", tags=["Statistics"])


@statistics_router.get(
    "/{id}/statistics", response_model=StatisticsRead
)
async def get_user_statistics_get(
    id: int,
    service: StatisticsServiceDependency,
    current: CurrentAuthDependency,
) -> StatisticsRead:
    return await service.get_user_statistics(id, current)
