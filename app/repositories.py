from typing import Annotated

from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models import Post, User


class PostRepository:
    def __init__(self, db: Annotated[AsyncSession, Depends(get_db)]):
        self.db = db

    async def get_post(self, post_id: int | None = None):
        if post_id is not None:
            return await self.db.scalar(select(Post).where(Post.id == post_id))
        return (await self.db.scalars(select(Post).order_by(Post.id))).all()

    async def get_user(self, user_id: int):
        return await self.db.get(User, user_id)

    async def create_post(self, title: str, user_id: int):
        post = Post(title=title, user_id=user_id)
        self.db.add(post)
        await self.db.commit()
        await self.db.refresh(post)
        return post

    async def update_post(self, post_id: int, title: str):
        post = await self.get_post(post_id)
        if post is None:
            return None
        post.title = title
        await self.db.commit()
        await self.db.refresh(post)
        return post

    async def delete_post(self, post_id: int):
        post = await self.get_post(post_id)
        if post is None:
            return False
        await self.db.delete(post)
        await self.db.commit()
        return True