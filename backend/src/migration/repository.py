from sqlalchemy import select

from src.common import BaseRepository
from src.migration.model import Migration
from src.migration.schema import MigrationWrite


class MigrationRepository(BaseRepository[Migration, MigrationWrite]):
    model = Migration

    async def get_applied_names(self) -> set[str]:
        result = await self.session.execute(select(Migration.name))
        return set(result.scalars().all())
