from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.schema import CurrentAuth
from src.notification.model import NotificationType
from src.notification.repository import NotificationRepository
from src.notification.schema import NotificationWrite
from src.picture.repository import PictureRepository
from src.post.model import Meal
from src.post.repository import PostRepository
from src.post.schema import (
    MAX_POST_MEALS,
    MIN_POST_MEALS,
    PostRead,
    PostWrite,
)
from src.user.access import assert_can_view
from src.user.model import UserRole
from src.user.repository import UserRepository


class PostService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.repo = PostRepository(session)
        self.user_repo = UserRepository(session)
        self.picture_repo = PictureRepository(session)
        self.notif_repo = NotificationRepository(session)

    async def create_post_post(
        self, data: PostWrite, current: CurrentAuth
    ) -> PostRead:
        if data.auth_id != current.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can create posts only for yourself",
            )

        if not MIN_POST_MEALS <= len(data.meals) <= MAX_POST_MEALS:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    f"A post must contain between {MIN_POST_MEALS} "
                    f"and {MAX_POST_MEALS} meals"
                ),
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

        if current_user.coach_id is not None:
            await self.notif_repo.create(
                NotificationWrite(
                    recipient_id=current_user.coach_id,
                    actor_id=current.id,
                    post_id=post.id,
                    type=NotificationType.post_created,
                )
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

        await assert_can_view(self.user_repo, post.auth_id, current)

        return PostRead.model_validate(post)

    async def get_all_posts_get(
        self, auth_id: int, current: CurrentAuth
    ) -> list[PostRead]:
        await assert_can_view(self.user_repo, auth_id, current)

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

        await assert_can_view(self.user_repo, post.auth_id, current)

        if not MIN_POST_MEALS <= len(data.meals) <= MAX_POST_MEALS:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    f"A post must contain between {MIN_POST_MEALS} "
                    f"and {MAX_POST_MEALS} meals"
                ),
            )

        owner_id = post.auth_id
        graded_by_coach = owner_id != current.id

        post = await self.repo.update_by_id(
            id, data, exclude={"auth_id"}
        )
        assert post is not None

        if not graded_by_coach:
            existing_by_id = {meal.id: meal for meal in post.meals}
            kept_ids: set[int] = set()

            for meal_data in data.meals:
                fields = meal_data.model_dump(exclude={"id"})
                meal_id = meal_data.id
                if meal_id is not None and meal_id in existing_by_id:
                    existing = existing_by_id[meal_id]
                    for key, value in fields.items():
                        setattr(existing, key, value)
                    kept_ids.add(meal_id)
                else:
                    post.meals.append(Meal(**fields))

            removed_meals = [
                meal
                for meal in existing_by_id.values()
                if meal.id not in kept_ids
            ]
            removed_picture_ids = [
                meal.picture_id
                for meal in removed_meals
                if meal.picture_id is not None
            ]
            for meal in removed_meals:
                post.meals.remove(meal)

            await self.session.commit()

            for picture_id in removed_picture_ids:
                await self.picture_repo.delete_by_id(picture_id)

        if graded_by_coach:
            await self.notif_repo.create(
                NotificationWrite(
                    recipient_id=owner_id,
                    actor_id=current.id,
                    post_id=id,
                    type=NotificationType.post_graded,
                )
            )

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

        picture_ids = [
            meal.picture_id
            for meal in post.meals
            if meal.picture_id is not None
        ]

        await self.repo.delete_by_id(id)

        for picture_id in picture_ids:
            await self.picture_repo.delete_by_id(picture_id)
