from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Path, Response, status

from app.schemas import PostCreate, PostResponse, PostUpdate
from app.services import PostService

post_router = APIRouter()


@post_router.get("/posts", response_model=list[PostResponse], tags=["게시글"])
def get_posts(service: Annotated[PostService, Depends()]):
    return service.get_post()


@post_router.get("/posts/{post_id}", response_model=PostResponse, tags=["게시글"])
def get_post(
    post_id: Annotated[int, Path(gt=0)],
    service: Annotated[PostService, Depends()],
):
    post = service.get_post(post_id)
    if post is None:
        raise HTTPException(status_code=404, detail="게시글을 찾을 수 없습니다.")
    return post


@post_router.post(
    "/posts",
    response_model=PostResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["게시글"],
    description="글을 작성합니다. 사용자당 최대 3개까지 작성할 수 있습니다.",
    responses={409: {"description": "이미 게시글이 3개인 사용자의 추가 작성은 거절합니다."}},
)
def create_post(body: PostCreate, service: Annotated[PostService, Depends()]):
    try:
        return service.create_post(title=body.title, user_id=body.user_id)
    except ValueError as exc:
        raise HTTPException(
            status_code=409,
            detail={"message": "사용자는 최대 3개까지 글을 작성할 수 있습니다."},
        ) from exc


@post_router.patch("/posts/{post_id}", response_model=PostResponse, tags=["게시글"])
def update_post(
    post_id: Annotated[int, Path(gt=0)],
    body: PostUpdate,
    service: Annotated[PostService, Depends()],
):
    post = service.update_post(post_id, body.title)
    if post is None:
        raise HTTPException(status_code=404, detail="게시글을 찾을 수 없습니다.")
    return post


@post_router.delete("/posts/{post_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["게시글"])
def delete_post(
    post_id: Annotated[int, Path(gt=0)],
    service: Annotated[PostService, Depends()],
):
    if not service.delete_post(post_id):
        raise HTTPException(status_code=404, detail="게시글을 찾을 수 없습니다.")
    return Response(status_code=status.HTTP_204_NO_CONTENT)
