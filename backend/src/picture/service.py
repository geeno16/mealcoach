from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.schema import CurrentAuth
from src.picture.model import Picture
from src.picture.repository import PictureRepository
from src.picture.schema import PictureWrite
from src.post.model import Post
from src.post.repository import PostRepository
from src.user.model import User, UserRole
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

    async def _get_post_or_404(self, post_id: int) -> Post:
        post = await self.post_repo.get_by_id(post_id)
        if not post:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Post not found",
            )
        return post

    async def _get_avatar_owner_or_404(self, picture_id: int) -> User:
        owner = await self.user_repo.get_by_picture_id(picture_id)
        if not owner:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Picture owner not found",
            )
        return owner

    def _forbidden(self) -> HTTPException:
        return HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied",
        )

    async def _assert_avatar_read_access(
        self, owner: User, current: CurrentAuth
    ) -> None:
        if owner.auth_id == current.id:
            return
        current_user = await self.user_repo.get_by_id(current.id)
        if (
            current_user
            and current_user.role == UserRole.coach
            and owner.coach_id == current.id
        ):
            return
        raise self._forbidden()

    async def _assert_post_read_access(
        self, post: Post, current: CurrentAuth
    ) -> None:
        if post.auth_id == current.id:
            return
        current_user = await self.user_repo.get_by_id(current.id)
        if current_user and current_user.role == UserRole.coach:
            owner = await self.user_repo.get_by_id(post.auth_id)
            if owner and owner.coach_id == current.id:
                return
        raise self._forbidden()

    async def get_picture_get(
        self, id: int, current: CurrentAuth
    ) -> bytes:
        picture = await self._get_picture_or_404(id)
        if picture.post_id is None:
            owner = await self._get_avatar_owner_or_404(id)
            await self._assert_avatar_read_access(owner, current)
        else:
            post = await self._get_post_or_404(picture.post_id)
            await self._assert_post_read_access(post, current)
        return picture.data

    async def get_post_pictures_get(
        self, post_id: int, current: CurrentAuth
    ) -> list[int]:
        post = await self._get_post_or_404(post_id)
        await self._assert_post_read_access(post, current)
        pictures = await self.repo.get_all_by_post_id(post_id)
        return [p.id for p in pictures]

    async def set_avatar(
        self, user_id: int, data: bytes, current: CurrentAuth
    ) -> Picture:
        if user_id != current.id:
            raise self._forbidden()
        current_user = await self.user_repo.get_by_id(current.id)
        if not current_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found",
            )
        old_picture_id = current_user.picture_id
        picture = await self.repo.create(PictureWrite(data=data))
        current_user.picture_id = picture.id
        await self.user_repo.update_by_id(
            current.id,
            UserWrite.model_validate(current_user, from_attributes=True),
        )
        if old_picture_id is not None:
            await self.repo.delete_by_id(old_picture_id)
        return picture

    async def create_post_picture(
        self, post_id: int, data: bytes, current: CurrentAuth
    ) -> Picture:
        post = await self._get_post_or_404(post_id)
        if post.auth_id != current.id:
            raise self._forbidden()
        count = await self.repo.count_by_post_id(post_id)
        if count >= MAX_POST_PICTURES:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"A post cannot have more than {MAX_POST_PICTURES} pictures",
            )
        picture = await self.repo.create(
            PictureWrite(data=data, post_id=post_id)
        )
        return picture

    async def _assert_write_access(
        self, picture: Picture, current: CurrentAuth
    ) -> None:
        if picture.post_id is None:
            owner = await self._get_avatar_owner_or_404(picture.id)
            if owner.auth_id != current.id:
                raise self._forbidden()
        else:
            post = await self._get_post_or_404(picture.post_id)
            if post.auth_id != current.id:
                raise self._forbidden()

    async def update_picture_put(
        self, id: int, data: bytes, current: CurrentAuth
    ) -> None:
        picture = await self._get_picture_or_404(id)
        await self._assert_write_access(picture, current)
        await self.repo.update_by_id(id, PictureWrite(data=data))

    async def delete_picture_delete(
        self, id: int, current: CurrentAuth
    ) -> None:
        picture = await self._get_picture_or_404(id)
        await self._assert_write_access(picture, current)
        if picture.post_id is None:
            owner = await self._get_avatar_owner_or_404(id)
            owner.picture_id = None
            await self.user_repo.update_by_id(
                owner.auth_id,
                UserWrite.model_validate(owner, from_attributes=True),
            )
        await self.repo.delete_by_id(id)
