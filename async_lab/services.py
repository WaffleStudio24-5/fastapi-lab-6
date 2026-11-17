from typing import Annotated

from fastapi import Depends

from async_lab.repositories import PostRepository


class PostService:
    def __init__(self, repository: Annotated[PostRepository, Depends()]):
        self.repository = repository

    def get_post(self, post_id: int):
        # TODO 2: 코루틴으로 바꾸고 Repository의 결과를 기다린다.
        raise NotImplementedError("TODO 2: Repository 호출")
