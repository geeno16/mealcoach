from typing import Annotated

from fastapi import Depends

from src.common.database import SessionDependency
from src.picture.service import PictureService


async def get_picture_service(
    session: SessionDependency,
) -> PictureService:
    return PictureService(session)


PictureServiceDependency = Annotated[
    PictureService, Depends(get_picture_service)
]
