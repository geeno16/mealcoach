from datetime import datetime

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
)


class PostBase(BaseModel):
    auth_id: int
    name: str = Field(min_length=1, max_length=50)
    energy: int | None = Field(default=None)
    description: str | None = Field(
        default=None, min_length=1, max_length=200
    )

    comment: str | None = Field(
        default=None, min_length=1, max_length=200
    )
    mark: int | None = Field(default=None, gt=0, lt=6)


class PostWrite(PostBase):
    pass


class PostRead(PostBase):
    id: int

    updated_at: datetime
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
