from src.statistics.dependency import StatisticsServiceDependency
from src.statistics.route import statistics_router
from src.statistics.schema import StatisticsRead
from src.statistics.service import StatisticsService

__all__ = [
    "StatisticsServiceDependency",
    "statistics_router",
    "StatisticsRead",
    "StatisticsService",
]
