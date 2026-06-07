from fastapi import APIRouter, Form, Response, UploadFile, status

from src.auth.dependency import CurrentAuthDependency
from src.picture.dependency import PictureServiceDependency
from src.picture.schema import PictureWrite

picture_router = APIRouter(prefix="/api/picture", tags=["Picture"])


@picture_router.get("/all/{post_id}", response_model=list[int])
async def get_all_pictures_get(
    post_id: int,
    service: PictureServiceDependency,
    current: CurrentAuthDependency,
) -> list[int]:
    return await service.get_all_pictures_get(post_id, current)


@picture_router.get("/{id}")
async def get_picture_get(
    id: int,
    service: PictureServiceDependency,
    current: CurrentAuthDependency,
) -> Response:
    data = await service.get_picture_get(id, current)
    return Response(content=data, media_type="image/jpeg")


@picture_router.post(
    "", status_code=status.HTTP_201_CREATED, response_model=int
)
async def create_picture_post(
    file: UploadFile,
    service: PictureServiceDependency,
    current: CurrentAuthDependency,
    post_id: int | None = Form(None),
) -> int:
    data = PictureWrite(data=await file.read(), post_id=post_id)
    return await service.create_picture_post(data, current)


@picture_router.put("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def update_picture_put(
    id: int,
    file: UploadFile,
    service: PictureServiceDependency,
    current: CurrentAuthDependency,
) -> None:
    data = PictureWrite(data=await file.read())
    await service.update_picture_put(id, data, current)


@picture_router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_picture_delete(
    id: int,
    service: PictureServiceDependency,
    current: CurrentAuthDependency,
) -> None:
    await service.delete_picture_delete(id, current)
