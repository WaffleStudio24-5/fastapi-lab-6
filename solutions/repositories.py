from typing import Annotated

from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Post
from async_lab.database import get_db


class PostRepository:
    def __init__(self, db: Annotated[AsyncSession, Depends(get_db)]):
        self.db = db

    async def get_post(self, post_id: int):
        result = await self.db.scalars(select(Post).where(Post.id == post_id))
        return result.one_or_none()
