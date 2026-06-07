from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.schema import CurrentAuth
from src.picture.model import Picture
from src.picture.repository import PictureRepository
from src.picture.schema import PictureWrite
from src.post.repository import PostRepository
from src.user.model import UserRole
from src.user.repository import UserRepository
from src.user.schema import UserWrite

MAX_POST_PICTURES = 3


class PictureService:
    def __init__(self, session: AsyncSession):
        self.repo = PictureRepository(session)
        self.user_repo = UserRepository(session)
        self.post_repo = PostRepository(session)

    async def _get_picture_or_404(self, id: int) -> Picture:
        picture = await self.repo.get_by_id(id)
        if not picture:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Picture not found",
            )
        return picture

    async def _assert_avatar_read_access(
        self, picture_id: int, current: CurrentAuth
    ) -> None:
        owner = await self.user_repo.get_by_picture_id(picture_id)
        if not owner:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Picture owner not found",
            )
        if owner.auth_id == current.id:
            return
        current_user = await self.user_repo.get_by_id(current.id)
        if (
            current_user
            and current_user.role == UserRole.coach
            and owner.coach_id == current.id
        ):
            return
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied",
        )

    async def _assert_post_picture_read_access(
        self, post_auth_id: int, current: CurrentAuth
    ) -> None:
        if post_auth_id == current.id:
            return
        current_user = await self.user_repo.get_by_id(current.id)
        if current_user and current_user.role == UserRole.coach:
            owner = await self.user_repo.get_by_id(post_auth_id)
            if owner and owner.coach_id == current.id:
                return
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied",
        )

    async def create_picture_post(
        self, data: PictureWrite, current: CurrentAuth
    ) -> int:
        current_user = await self.user_repo.get_by_id(current.id)
        if not current_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found",
            )

        if data.post_id is None:
            picture = await self.repo.create(data)
            current_user.picture_id = picture.id
            await self.user_repo.update_by_id(
                current.id, UserWrite.model_validate(current_user)
            )
            return picture.id

        if current_user.role != UserRole.trainee:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only trainees can upload post pictures",
            )
        post = await self.post_repo.get_by_id(data.post_id)
        if not post:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Post not found",
            )
        if post.auth_id != current.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only upload pictures for your own posts",
            )
        count = await self.repo.count_by_post_id(data.post_id)
        if count >= MAX_POST_PICTURES:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"A post cannot have more than {MAX_POST_PICTURES} pictures",
            )
        picture = await self.repo.create(data)
        return picture.id

    async def get_picture_get(
        self, id: int, current: CurrentAuth
    ) -> bytes:
        picture = await self._get_picture_or_404(id)
        if picture.post_id is None:
            await self._assert_avatar_read_access(id, current)
        else:
            post = await self.post_repo.get_by_id(picture.post_id)
            if not post:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Post not found",
                )
            await self._assert_post_picture_read_access(
                post.auth_id, current
            )
        return picture.data

    async def get_all_pictures_get(
        self, post_id: int, current: CurrentAuth
    ) -> list[int]:
        post = await self.post_repo.get_by_id(post_id)
        if not post:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Post not found",
            )
        await self._assert_post_picture_read_access(
            post.auth_id, current
        )
        pictures = await self.repo.get_all_by_post_id(post_id)
        return [p.id for p in pictures]

    async def update_picture_put(
        self, id: int, data: PictureWrite, current: CurrentAuth
    ) -> None:
        picture = await self._get_picture_or_404(id)
        if picture.post_id is None:
            owner = await self.user_repo.get_by_picture_id(id)
            if not owner or owner.auth_id != current.id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="You can only update your own avatar",
                )
        else:
            current_user = await self.user_repo.get_by_id(current.id)
            if not current_user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User not found",
                )
            if current_user.role != UserRole.trainee:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Only trainees can update post pictures",
                )
            post = await self.post_repo.get_by_id(picture.post_id)
            if not post or post.auth_id != current.id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="You can only update pictures for your own posts",
                )
        await self.repo.update_by_id(id, data)

    async def delete_picture_delete(
        self, id: int, current: CurrentAuth
    ) -> None:
        picture = await self._get_picture_or_404(id)
        if picture.post_id is None:
            owner = await self.user_repo.get_by_picture_id(id)
            if not owner or owner.auth_id != current.id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="You can only delete your own avatar",
                )
            owner.picture_id = None
            await self.user_repo.update_by_id(
                owner.auth_id, UserWrite.model_validate(owner)
            )
        else:
            current_user = await self.user_repo.get_by_id(current.id)
            if not current_user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User not found",
                )
            if current_user.role != UserRole.trainee:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Only trainees can delete post pictures",
                )
            post = await self.post_repo.get_by_id(picture.post_id)
            if not post or post.auth_id != current.id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="You can only delete pictures for your own posts",
                )
        await self.repo.delete_by_id(id)
