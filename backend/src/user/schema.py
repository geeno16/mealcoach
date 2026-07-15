from pydantic import (
    BaseModel,
    ConfigDict,
    EmailStr,
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
    coach_request_id: int | None = Field(default=None)
    picture_id: int | None = Field(default=None)


class UserWrite(UserBase):
    coach_email: EmailStr | None = Field(default=None)


class UserRead(UserBase):
    model_config = ConfigDict(from_attributes=True)


class CoachRequest(BaseModel):
    coach_email: EmailStr
