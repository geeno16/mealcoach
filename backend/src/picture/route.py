from typing import Annotated

from fastapi import APIRouter, Body, Response, status

from src.auth.dependency import CurrentAuthDependency
from src.picture.dependency import PictureServiceDependency
from src.picture.schema import PictureRead

picture_router = APIRouter(prefix="/api", tags=["Picture"])

JpegBody = Annotated[bytes, Body(media_type="image/jpeg")]


@picture_router.get(
    "/pictures/{id}",
    response_class=Response,
    responses={
        200: {
            "content": {
                "image/jpeg": {
                    "schema": {"type": "string", "format": "binary"}
                }
            }
        }
    },
)
async def get_picture_get(
    id: int,
    service: PictureServiceDependency,
    current: CurrentAuthDependency,
) -> Response:
    data = await service.get_picture_get(id, current)
    return Response(content=data, media_type="image/jpeg")


@picture_router.put(
    "/meals/{meal_id}/picture", response_model=PictureRead
)
async def set_meal_picture_put(
    meal_id: int,
    data: JpegBody,
    service: PictureServiceDependency,
    current: CurrentAuthDependency,
    response: Response,
) -> PictureRead:
    picture = await service.set_meal_picture(meal_id, data, current)
    response.headers["Location"] = f"/api/pictures/{picture.id}"
    return PictureRead.model_validate(picture)


@picture_router.put(
    "/users/{user_id}/avatar", response_model=PictureRead
)
async def set_avatar_put(
    user_id: int,
    data: JpegBody,
    service: PictureServiceDependency,
    current: CurrentAuthDependency,
    response: Response,
) -> PictureRead:
    picture = await service.set_avatar(user_id, data, current)
    response.headers["Location"] = f"/api/pictures/{picture.id}"
    return PictureRead.model_validate(picture)


@picture_router.delete(
    "/pictures/{id}", status_code=status.HTTP_204_NO_CONTENT
)
async def delete_picture_delete(
    id: int,
    service: PictureServiceDependency,
    current: CurrentAuthDependency,
) -> None:
    await service.delete_picture_delete(id, current)
