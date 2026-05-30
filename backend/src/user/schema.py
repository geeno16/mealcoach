from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
)

from src.user.model import UserRole


class UserBase(BaseModel):
    auth_id: int
    role: UserRole
    name: str = Field(min_length=1, max_length=50)

    surname: str | None = Field(
        default=None, min_length=1, max_length=50
    )
    age: int | None = Field(default=None, gt=1, lt=120)
    weight: int | None = Field(default=None, gt=1, lt=200)
    height: int | None = Field(default=None, gt=1, lt=300)
    coach_id: int | None = Field(default=None)
    picture_id: int | None = Field(default=None)


class UserWrite(UserBase):
    pass


class UserRead(UserBase):
    model_config = ConfigDict(from_attributes=True)
