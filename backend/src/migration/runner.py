import importlib
import logging
import pkgutil
from types import ModuleType

from sqlalchemy.ext.asyncio import async_sessionmaker

from src.common import IS_DEV, engine
from src.migration.repository import MigrationRepository
from src.migration.schema import MigrationWrite

logger = logging.getLogger(__name__)


def _discover() -> list[tuple[str, ModuleType]]:
    from src.migration import versions

    found = [
        (
            info.name,
            importlib.import_module(f"{versions.__name__}.{info.name}"),
        )
        for info in pkgutil.iter_modules(versions.__path__)
    ]
    found.sort(key=lambda item: item[0])
    return found


async def run_migrations() -> None:
    factory = async_sessionmaker(engine, expire_on_commit=False)

    async with factory() as session:
        repo = MigrationRepository(session)
        applied = await repo.get_applied_names()

        for name, module in _discover():
            if name in applied:
                continue

            if getattr(module, "DEV_ONLY", False) and not IS_DEV:
                logger.info("Migration %s skipped: dev only", name)
                continue

            logger.info("Applying migration %s", name)
            await module.upgrade(session)
            await repo.create(MigrationWrite(name=name))
            logger.info("Migration %s applied", name)
