from typing import Annotated

from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Post
from async_lab.database import get_db


class PostRepository:
    def __init__(self, db: Annotated[AsyncSession, Depends(get_db)]):
        self.db = db

    def get_post(self, post_id: int):
        # TODO 1: async def와 await로 조회한 뒤 Post 또는 None을 반환한다.
        raise NotImplementedError("TODO 1: 비동기 게시글 조회")
