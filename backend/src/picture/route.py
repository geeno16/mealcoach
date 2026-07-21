from datetime import UTC
from email.utils import format_datetime
from typing import Annotated

from fastapi import APIRouter, Body, Header, Response, status

from src.auth.dependency import CurrentAuthDependency
from src.picture.dependency import PictureServiceDependency
from src.picture.schema import PictureRead

picture_router = APIRouter(prefix="/api", tags=["Picture"])

JpegBody = Annotated[bytes, Body(media_type="image/jpeg")]

PICTURE_CACHE_MAX_AGE_SECONDS = 3600


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
    if_none_match: Annotated[str | None, Header()] = None,
) -> Response:
    picture = await service.get_picture_get(id, current)
    etag = f'"{picture.id}-{picture.updated_at.isoformat()}"'
    headers = {
        "Cache-Control": (
            f"private, max-age={PICTURE_CACHE_MAX_AGE_SECONDS}, "
            "must-revalidate"
        ),
        "ETag": etag,
        "Last-Modified": format_datetime(
            picture.updated_at.replace(tzinfo=UTC),
            usegmt=True,
        ),
    }

    if if_none_match == etag:
        return Response(
            status_code=status.HTTP_304_NOT_MODIFIED, headers=headers
        )

    return Response(
        content=picture.data, media_type="image/jpeg", headers=headers
    )


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
