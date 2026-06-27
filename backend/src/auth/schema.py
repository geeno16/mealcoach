from dataclasses import dataclass
from datetime import datetime

from pydantic import (
    BaseModel,
    ConfigDict,
    EmailStr,
    Field,
    field_validator,
)


class AuthBase(BaseModel):
    email: EmailStr


class AuthWrite(AuthBase):
    password: str = Field(min_length=8, max_length=128)

    @field_validator("password")
    @classmethod
    def validate_password_strength(cls, v: str) -> str:
        if v.isdigit() or v.isalpha():
            raise ValueError(
                "Password must contain both letters and numbers"
            )
        return v


class AuthRead(AuthBase):
    id: int
    is_verified: bool
    updated_at: datetime
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class MessageResponse(BaseModel):
    message: str


class EmailVerify(AuthBase):
    code: str = Field(min_length=6, max_length=6)


@dataclass(frozen=True)
class CurrentAuth:
    id: int
