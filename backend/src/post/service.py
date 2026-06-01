from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.schema import CurrentAuth
from src.post.repository import PostRepository
from src.post.schema import PostRead, PostWrite
from src.user.model import UserRole
from src.user.repository import UserRepository


class PostService:
    def __init__(self, session: AsyncSession):
        self.repo = PostRepository(session)
        self.user_repo = UserRepository(session)

    async def _assert_access(
        self, post_auth_id: int, current: CurrentAuth
    ) -> None:
        if post_auth_id == current.id:
            return

        current_user = await self.user_repo.get_by_id(current.id)

        if not current_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Current user not found",
            )

        if current_user.role == UserRole.coach:
            owner = await self.user_repo.get_by_id(post_auth_id)
            if owner and owner.coach_id == current.id:
                return

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied",
        )

    async def create_post_post(
        self, data: PostWrite, current: CurrentAuth
    ) -> PostRead:
        if data.auth_id != current.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can create posts only for yourself",
            )

        current_user = await self.user_repo.get_by_id(current.id)

        if not current_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found",
            )

        if current_user.role == UserRole.coach:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Coach cannot create posts",
            )

        post = await self.repo.create(
            data.model_copy(update={"comment": None, "mark": None})
        )
        return PostRead.model_validate(post)

    async def get_post_get(
        self, id: int, current: CurrentAuth
    ) -> PostRead:
        post = await self.repo.get_by_id(id)

        if not post:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Post not found",
            )

        await self._assert_access(post.auth_id, current)

        return PostRead.model_validate(post)

    async def get_all_posts_get(
        self, auth_id: int, current: CurrentAuth
    ) -> list[PostRead]:
        await self._assert_access(auth_id, current)

        posts = await self.repo.get_all_by_auth_id(auth_id)
        return [PostRead.model_validate(p) for p in posts]

    async def update_post_put(
        self, id: int, data: PostWrite, current: CurrentAuth
    ) -> PostRead:
        post = await self.repo.get_by_id(id)

        if not post:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Post not found",
            )

        await self._assert_access(post.auth_id, current)

        if post.auth_id == current.id:
            exclude = {"auth_id", "comment", "mark"}
        else:
            exclude = {"auth_id", "name", "energy", "description"}

        post = await self.repo.update_by_id(id, data, exclude=exclude)
        return PostRead.model_validate(post)

    async def delete_post_delete(
        self, id: int, current: CurrentAuth
    ) -> None:
        post = await self.repo.get_by_id(id)

        if not post:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Post not found",
            )

        if post.auth_id != current.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can delete only your own posts",
            )

        await self.repo.delete_by_id(id)
