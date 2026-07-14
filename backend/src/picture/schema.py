from pydantic import BaseModel, ConfigDict


class PictureWrite(BaseModel):
    data: bytes


class PictureRead(BaseModel):
    id: int

    model_config = ConfigDict(from_attributes=True)
