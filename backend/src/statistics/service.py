from collections import defaultdict
from datetime import UTC, date, datetime

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.schema import CurrentAuth
from src.post.model import Post
from src.post.repository import PostRepository
from src.statistics.schema import (
    DailyPoint,
    MacroRatio,
    MarkStats,
    MealStats,
    NutritionStats,
    PostStats,
    ProfileStats,
    StatisticsRead,
)
from src.user.access import assert_can_view
from src.user.model import User
from src.user.repository import UserRepository


def _round(value: float) -> float:
    return round(value, 2)


def _avg(total: int, count: int) -> float | None:
    return _round(total / count) if count else None


def _bmi(
    weight: int | None, height: int | None
) -> tuple[float | None, str | None]:
    if not weight or not height:
        return None, None
    meters = height / 100
    bmi = round(weight / (meters * meters), 1)
    if bmi < 18.5:
        category = "underweight"
    elif bmi < 25:
        category = "normal"
    elif bmi < 30:
        category = "overweight"
    else:
        category = "obese"
    return bmi, category


def _longest_streak(days: set[date]) -> int:
    if not days:
        return 0
    ordered = sorted(days)
    longest = current = 1
    for prev, cur in zip(ordered, ordered[1:], strict=False):
        if (cur - prev).days == 1:
            current += 1
            longest = max(longest, current)
        else:
            current = 1
    return longest


def _build_profile(user: User) -> ProfileStats:
    bmi, category = _bmi(user.weight, user.height)
    return ProfileStats(
        age=user.age,
        weight=user.weight,
        height=user.height,
        bmi=bmi,
        bmi_category=category,
    )


def _build_marks(marks: list[int]) -> MarkStats:
    if not marks:
        return MarkStats()
    distribution: dict[int, int] = defaultdict(int)
    for mark in marks:
        distribution[mark] += 1
    return MarkStats(
        average=_avg(sum(marks), len(marks)),
        best=max(marks),
        worst=min(marks),
        distribution=dict(sorted(distribution.items())),
    )


def _build_nutrition(
    posts: list[Post], meal_count: int
) -> NutritionStats:
    total_cal = sum(m.cal or 0 for p in posts for m in p.meals)
    total_protein = sum(m.protein or 0 for p in posts for m in p.meals)
    total_fat = sum(m.fat or 0 for p in posts for m in p.meals)
    total_carb = sum(
        m.carbohydrate or 0 for p in posts for m in p.meals
    )

    grams = total_protein + total_fat + total_carb
    macro = MacroRatio()
    if grams:
        macro = MacroRatio(
            protein=round(100 * total_protein / grams, 1),
            fat=round(100 * total_fat / grams, 1),
            carbohydrate=round(100 * total_carb / grams, 1),
        )

    return NutritionStats(
        total_calories=total_cal,
        total_protein=total_protein,
        total_fat=total_fat,
        total_carbohydrate=total_carb,
        avg_calories_per_post=_avg(total_cal, len(posts)),
        avg_calories_per_meal=_avg(total_cal, meal_count),
        avg_protein_per_meal=_avg(total_protein, meal_count),
        avg_fat_per_meal=_avg(total_fat, meal_count),
        avg_carbohydrate_per_meal=_avg(total_carb, meal_count),
        macro_ratio=macro,
    )


def _build_timeline(posts: list[Post]) -> list[DailyPoint]:
    buckets: dict[date, dict] = defaultdict(
        lambda: {"posts": 0, "calories": 0, "marks": []}
    )
    for post in posts:
        day = post.created_at.date()
        buckets[day]["posts"] += 1
        buckets[day]["calories"] += sum(m.cal or 0 for m in post.meals)
        if post.mark is not None:
            buckets[day]["marks"].append(post.mark)

    return [
        DailyPoint(
            date=day,
            posts=bucket["posts"],
            calories=bucket["calories"],
            avg_mark=_avg(sum(bucket["marks"]), len(bucket["marks"])),
        )
        for day, bucket in sorted(buckets.items())
    ]


def build_statistics(
    user_id: int, user: User, posts: list[Post]
) -> StatisticsRead:
    marks = [p.mark for p in posts if p.mark is not None]
    meals = [meal for post in posts for meal in post.meals]
    days = {post.created_at.date() for post in posts}
    created_dates = [post.created_at for post in posts]

    post_stats = PostStats(
        total=len(posts),
        graded=len(marks),
        ungraded=len(posts) - len(marks),
        with_comment=sum(1 for p in posts if p.comment is not None),
        active_days=len(days),
        longest_streak=_longest_streak(days),
        first_post_at=min(created_dates) if created_dates else None,
        last_post_at=max(created_dates) if created_dates else None,
    )

    meal_stats = MealStats(
        total=len(meals),
        avg_per_post=_avg(len(meals), len(posts)),
        with_picture=sum(1 for m in meals if m.picture_id is not None),
    )

    return StatisticsRead(
        user_id=user_id,
        generated_at=datetime.now(UTC),
        profile=_build_profile(user),
        posts=post_stats,
        marks=_build_marks(marks),
        nutrition=_build_nutrition(posts, len(meals)),
        meals=meal_stats,
        timeline=_build_timeline(posts),
    )


class StatisticsService:
    def __init__(self, session: AsyncSession):
        self.user_repo = UserRepository(session)
        self.post_repo = PostRepository(session)

    async def get_user_statistics(
        self, id: int, current: CurrentAuth
    ) -> StatisticsRead:
        user = await self.user_repo.get_by_id(id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found",
            )

        await assert_can_view(self.user_repo, id, current)

        posts = await self.post_repo.get_all_by_auth_id(id)
        return build_statistics(id, user, posts)
