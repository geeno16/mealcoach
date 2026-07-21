from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.schema import CurrentAuth
from src.picture.model import Picture
from src.picture.repository import PictureRepository
from src.picture.schema import PictureWrite
from src.post.repository import MealRepository, PostRepository
from src.user.access import assert_can_view
from src.user.repository import UserRepository
from src.user.schema import UserWrite


class PictureService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.repo = PictureRepository(session)
        self.user_repo = UserRepository(session)
        self.post_repo = PostRepository(session)
        self.meal_repo = MealRepository(session)

    def _forbidden(self) -> HTTPException:
        return HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied",
        )

    async def _get_picture_or_404(self, id: int) -> Picture:
        picture = await self.repo.get_by_id(id)
        if not picture:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Picture not found",
            )
        return picture

    async def _resolve_owner_auth_id(
        self, picture_id: int
    ) -> int | None:
        owner = await self.user_repo.get_by_picture_id(picture_id)
        if owner:
            return owner.auth_id

        meal = await self.meal_repo.get_by_picture_id(picture_id)
        if meal:
            post = await self.post_repo.get_by_id(meal.post_id)
            if post:
                return post.auth_id

        return None

    async def get_picture_get(
        self, id: int, current: CurrentAuth
    ) -> Picture:
        picture = await self._get_picture_or_404(id)
        owner_auth_id = await self._resolve_owner_auth_id(id)
        if owner_auth_id is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Picture not found",
            )
        await assert_can_view(self.user_repo, owner_auth_id, current)
        return picture

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
            UserWrite.model_validate(
                current_user, from_attributes=True
            ),
        )
        if old_picture_id is not None:
            await self.repo.delete_by_id(old_picture_id)
        return picture

    async def set_meal_picture(
        self, meal_id: int, data: bytes, current: CurrentAuth
    ) -> Picture:
        meal = await self.meal_repo.get_by_id(meal_id)
        if not meal:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Meal not found",
            )
        post = await self.post_repo.get_by_id(meal.post_id)
        if not post:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Post not found",
            )
        if post.auth_id != current.id:
            raise self._forbidden()

        if meal.picture_id is not None:
            await self.repo.update_by_id(
                meal.picture_id, PictureWrite(data=data)
            )
            picture = await self.repo.get_by_id(meal.picture_id)
            assert picture is not None
            return picture

        picture = await self.repo.create(PictureWrite(data=data))
        meal.picture_id = picture.id
        await self.session.commit()
        return picture

    async def delete_picture_delete(
        self, id: int, current: CurrentAuth
    ) -> None:
        await self._get_picture_or_404(id)

        owner = await self.user_repo.get_by_picture_id(id)
        if owner:
            if owner.auth_id != current.id:
                raise self._forbidden()
            owner.picture_id = None
            await self.user_repo.update_by_id(
                owner.auth_id,
                UserWrite.model_validate(owner, from_attributes=True),
            )
            await self.repo.delete_by_id(id)
            return

        meal = await self.meal_repo.get_by_picture_id(id)
        if meal:
            post = await self.post_repo.get_by_id(meal.post_id)
            if not post or post.auth_id != current.id:
                raise self._forbidden()
            meal.picture_id = None
            await self.session.commit()
            await self.repo.delete_by_id(id)
            return

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Picture not found",
        )
