from datetime import datetime

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
)

MIN_POST_MEALS = 1
MAX_POST_MEALS = 3


class MealBase(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=50)
    cal: int | None = Field(default=None, ge=0)
    protein: int | None = Field(default=None, ge=0)
    fat: int | None = Field(default=None, ge=0)
    carbohydrate: int | None = Field(default=None, ge=0)


class MealWrite(MealBase):
    id: int | None = Field(default=None)


class MealRead(MealBase):
    id: int
    picture_id: int | None = None

    model_config = ConfigDict(from_attributes=True)


class PostBase(BaseModel):
    auth_id: int
    name: str = Field(min_length=1, max_length=50)
    description: str | None = Field(
        default=None, min_length=1, max_length=200
    )

    comment: str | None = Field(
        default=None, min_length=1, max_length=200
    )
    mark: int | None = Field(default=None, gt=0, lt=6)


class PostWrite(PostBase):
    meals: list[MealWrite] = Field(default_factory=list)


class PostRead(PostBase):
    id: int

    meals: list[MealRead] = Field(default_factory=list)

    updated_at: datetime
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
