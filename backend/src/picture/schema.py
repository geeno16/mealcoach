from pydantic import BaseModel, ConfigDict


class PictureWrite(BaseModel):
    data: bytes
    width: int
    height: int


class PictureRead(BaseModel):
    id: int
    width: int
    height: int

    model_config = ConfigDict(from_attributes=True)
