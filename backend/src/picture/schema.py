from pydantic import BaseModel, ConfigDict


class PictureWrite(BaseModel):
    data: bytes
    post_id: int | None = None


class PictureRead(BaseModel):
    id: int
    post_id: int | None = None

    model_config = ConfigDict(from_attributes=True)
