from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Path

from app.schemas import PostResponse
from async_lab.services import PostService

post_router = APIRouter()


@post_router.get(
    "/posts/{post_id}",
    response_model=PostResponse,
    tags=["게시글"],
    responses={404: {"description": "게시글을 찾을 수 없음"}},
)
async def get_post(
    post_id: Annotated[int, Path(gt=0)],
    service: Annotated[PostService, Depends()],
):
    post = await service.get_post(post_id)
    if post is None:
        raise HTTPException(status_code=404, detail="게시글을 찾을 수 없습니다.")
    return post
