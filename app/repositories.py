from typing import Annotated

from fastapi import Depends
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Post, User


class PostRepository:
    def __init__(self, db: Annotated[Session, Depends(get_db)]):
        self.db = db

    def get_post(self, post_id: int | None = None):
        if post_id is not None:
            return self.db.scalars(select(Post).where(Post.id == post_id)).one_or_none()
        return self.db.scalars(select(Post).order_by(Post.id)).all()

    def get_user(self, user_id: int):
        return self.db.get(User, user_id)

    def count_posts(self, user_id: int):
        return self.db.scalar(select(func.count()).select_from(Post).where(Post.user_id == user_id))

    def create_post(self, title: str, user_id: int):
        post = Post(title=title, user_id=user_id)
        self.db.add(post)
        self.db.commit()
        self.db.refresh(post)
        return post

    def update_post(self, post_id: int, title: str):
        post = self.get_post(post_id)
        if post is None:
            return None
        post.title = title
        self.db.commit()
        self.db.refresh(post)
        return post

    def delete_post(self, post_id: int):
        post = self.get_post(post_id)
        if post is None:
            return False
        self.db.delete(post)
        self.db.commit()
        return True
