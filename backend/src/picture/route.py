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
                "image/jpeg": {"schema": {"type": "string", "format": "binary"}}
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


@picture_router.get("/posts/{post_id}/pictures", response_model=list[int])
async def get_post_pictures_get(
    post_id: int,
    service: PictureServiceDependency,
    current: CurrentAuthDependency,
) -> list[int]:
    return await service.get_post_pictures_get(post_id, current)


@picture_router.post(
    "/posts/{post_id}/pictures",
    status_code=status.HTTP_201_CREATED,
    response_model=PictureRead,
)
async def create_post_picture_post(
    post_id: int,
    data: JpegBody,
    service: PictureServiceDependency,
    current: CurrentAuthDependency,
    response: Response,
) -> PictureRead:
    picture = await service.create_post_picture(post_id, data, current)
    response.headers["Location"] = f"/api/pictures/{picture.id}"
    return PictureRead.model_validate(picture)


@picture_router.put("/users/{user_id}/avatar", response_model=PictureRead)
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


@picture_router.put(
    "/pictures/{id}", status_code=status.HTTP_204_NO_CONTENT
)
async def update_picture_put(
    id: int,
    data: JpegBody,
    service: PictureServiceDependency,
    current: CurrentAuthDependency,
) -> None:
    await service.update_picture_put(id, data, current)


@picture_router.delete(
    "/pictures/{id}", status_code=status.HTTP_204_NO_CONTENT
)
async def delete_picture_delete(
    id: int,
    service: PictureServiceDependency,
    current: CurrentAuthDependency,
) -> None:
    await service.delete_picture_delete(id, current)
