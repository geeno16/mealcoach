from datetime import date, datetime

from pydantic import BaseModel


class ProfileStats(BaseModel):
    age: int | None = None
    weight: int | None = None
    height: int | None = None
    bmi: float | None = None
    bmi_category: str | None = None


class PostStats(BaseModel):
    total: int = 0
    graded: int = 0
    ungraded: int = 0
    with_comment: int = 0
    active_days: int = 0
    longest_streak: int = 0
    first_post_at: datetime | None = None
    last_post_at: datetime | None = None


class MarkStats(BaseModel):
    average: float | None = None
    best: int | None = None
    worst: int | None = None
    distribution: dict[int, int] = {}


class MacroRatio(BaseModel):
    protein: float | None = None
    fat: float | None = None
    carbohydrate: float | None = None


class NutritionStats(BaseModel):
    total_calories: int = 0
    total_protein: int = 0
    total_fat: int = 0
    total_carbohydrate: int = 0
    avg_calories_per_post: float | None = None
    avg_calories_per_meal: float | None = None
    avg_protein_per_meal: float | None = None
    avg_fat_per_meal: float | None = None
    avg_carbohydrate_per_meal: float | None = None
    macro_ratio: MacroRatio = MacroRatio()


class MealStats(BaseModel):
    total: int = 0
    avg_per_post: float | None = None
    with_picture: int = 0


class DailyPoint(BaseModel):
    date: date
    posts: int
    calories: int
    avg_mark: float | None = None


class StatisticsRead(BaseModel):
    user_id: int
    generated_at: datetime

    profile: ProfileStats
    posts: PostStats
    marks: MarkStats
    nutrition: NutritionStats
    meals: MealStats
    timeline: list[DailyPoint]
