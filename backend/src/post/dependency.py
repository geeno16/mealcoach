from typing import Annotated

from fastapi import Depends

from src.common.database import SessionDependency
from src.post.service import PostService


async def get_post_service(session: SessionDependency) -> PostService:
    return PostService(session)


PostServiceDependency = Annotated[
    PostService, Depends(get_post_service)
]
