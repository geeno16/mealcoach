from fastapi import APIRouter, status

from src.auth.dependency import CurrentAuthDependency
from src.post.dependency import PostServiceDependency
from src.post.schema import PostRead, PostWrite

post_router = APIRouter(prefix="/api/posts", tags=["Posts"])


@post_router.get("/all/{auth_id}", response_model=list[PostRead])
async def get_all_posts_get(
    auth_id: int,
    service: PostServiceDependency,
    current: CurrentAuthDependency,
) -> list[PostRead]:
    return await service.get_all_posts_get(auth_id, current)


@post_router.get("/{id}", response_model=PostRead)
async def get_post_get(
    id: int,
    service: PostServiceDependency,
    current: CurrentAuthDependency,
) -> PostRead:
    return await service.get_post_get(id, current)


@post_router.post(
    "", status_code=status.HTTP_201_CREATED, response_model=PostRead
)
async def create_post_post(
    data: PostWrite,
    service: PostServiceDependency,
    current: CurrentAuthDependency,
) -> PostRead:
    return await service.create_post_post(data, current)


@post_router.put("/{id}", response_model=PostRead)
async def update_post_put(
    id: int,
    data: PostWrite,
    service: PostServiceDependency,
    current: CurrentAuthDependency,
) -> PostRead:
    return await service.update_post_put(id, data, current)


@post_router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_post_delete(
    id: int,
    service: PostServiceDependency,
    current: CurrentAuthDependency,
) -> None:
    await service.delete_post_delete(id, current)
