from typing import Annotated

from fastapi import Depends

from async_lab.repositories import PostRepository


class PostService:
    def __init__(self, repository: Annotated[PostRepository, Depends()]):
        self.repository = repository

    async def get_post(self, post_id: int):
        return await self.repository.get_post(post_id)
