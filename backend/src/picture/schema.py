from pydantic import BaseModel


class PictureWrite(BaseModel):
    data: bytes
    post_id: int | None = None
