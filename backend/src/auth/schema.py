from dataclasses import dataclass
from datetime import datetime

from pydantic import (
    BaseModel,
    ConfigDict,
    EmailStr,
    Field,
    field_validator,
)


def _validate_password_strength(v: str) -> str:
    if v.isdigit() or v.isalpha():
        raise ValueError(
            "Password must contain both letters and numbers"
        )
    return v


class AuthBase(BaseModel):
    email: EmailStr


class AuthWrite(AuthBase):
    password: str = Field(min_length=8, max_length=128)

    @field_validator("password")
    @classmethod
    def validate_password_strength(cls, v: str) -> str:
        return _validate_password_strength(v)


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


class PasswordForgot(AuthBase):
    pass


class PasswordReset(AuthBase):
    code: str = Field(min_length=6, max_length=6)
    password: str = Field(min_length=8, max_length=128)

    @field_validator("password")
    @classmethod
    def validate_password_strength(cls, v: str) -> str:
        return _validate_password_strength(v)


@dataclass(frozen=True)
class CurrentAuth:
    id: int
