from sqlalchemy import select

from src.common import BaseRepository
from src.post.model import Post
from src.post.schema import PostWrite


class PostRepository(BaseRepository[Post, PostWrite]):
    model = Post

    async def get_all_by_auth_id(self, auth_id: int) -> list[Post]:
        result = await self.session.execute(
            select(Post).where(Post.auth_id == auth_id)
        )
        return list(result.scalars().all())

    async def update_by_id(
        self, id: int, data: PostWrite, exclude: set[str] | None = None
    ) -> Post | None:
        post = await self.get_by_id(id)

        if not post:
            return None

        if exclude is None:
            exclude = {"auth_id"}

        for key, value in data.model_dump(exclude=exclude).items():
            setattr(post, key, value)

        await self.session.commit()
        await self.session.refresh(post)

        return post
