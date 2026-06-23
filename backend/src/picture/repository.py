from sqlalchemy import func, select

from src.common import BaseRepository
from src.picture.model import Picture
from src.picture.schema import PictureWrite


class PictureRepository(BaseRepository[Picture, PictureWrite]):
    model = Picture

    async def get_all_by_post_id(self, post_id: int) -> list[Picture]:
        result = await self.session.execute(
            select(Picture).where(Picture.post_id == post_id)
        )
        return list(result.scalars().all())

    async def count_by_post_id(self, post_id: int) -> int:
        result = await self.session.execute(
            select(func.count(Picture.id)).where(
                Picture.post_id == post_id
            )
        )
        return result.scalar_one()

    async def update_by_id(
        self, id: int, data: PictureWrite
    ) -> Picture | None:
        picture = await self.get_by_id(id)
        if not picture:
            return None
        picture.data = data.data
        await self.session.commit()
        await self.session.refresh(picture)
        return picture
