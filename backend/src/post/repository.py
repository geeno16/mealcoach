from sqlalchemy import select

from src.common import BaseRepository
from src.post.model import Meal, Post
from src.post.schema import MealWrite, PostWrite


class PostRepository(BaseRepository[Post, PostWrite]):
    model = Post

    async def create(self, data: PostWrite) -> Post:
        post = Post(**data.model_dump(exclude={"meals"}))
        post.meals = [Meal(**meal.model_dump()) for meal in data.meals]

        self.session.add(post)
        await self.session.commit()

        created = await self.get_by_id(post.id)
        assert created is not None
        return created

    async def get_all_by_auth_id(self, auth_id: int) -> list[Post]:
        result = await self.session.execute(
            select(Post)
            .where(Post.auth_id == auth_id)
            .order_by(Post.created_at.desc())
        )
        return list(result.scalars().all())

    async def update_by_id(
        self,
        id: int,
        data: PostWrite,
        exclude: set[str] | None = None,
        refresh_fields: list[str] | None = None,
    ) -> Post | None:
        if exclude is None:
            exclude = {"auth_id"}

        return await super().update_by_id(
            id,
            data,
            exclude=exclude | {"meals"},
            refresh_fields=refresh_fields or ["updated_at"],
        )


class MealRepository(BaseRepository[Meal, MealWrite]):
    model = Meal

    async def get_by_picture_id(self, picture_id: int) -> Meal | None:
        result = await self.session.execute(
            select(Meal).where(Meal.picture_id == picture_id)
        )
        return result.scalar_one_or_none()
