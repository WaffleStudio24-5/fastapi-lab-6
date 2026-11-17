from typing import Annotated

from fastapi import Depends, HTTPException

from app.repositories import PostRepository


class PostService:
    def __init__(self, repository: Annotated[PostRepository, Depends()]):
        self.repository = repository

    def get_post(self, post_id: int | None = None):
        return self.repository.get_post(post_id)

    def create_post(self, title: str, user_id: int):
        if self.repository.get_user(user_id) is None:
            raise HTTPException(status_code=404, detail="사용자를 찾을 수 없습니다.")
        # shortcut: 순차 요청의 한도 검사, 동시 작성을 보장하려면 잠금·트랜잭션 설계 필요.
        if self.repository.count_posts(user_id) >= 3:
            raise ValueError("사용자는 최대 3개까지 글을 작성할 수 있습니다.")
        return self.repository.create_post(title, user_id)

    def update_post(self, post_id: int, title: str):
        return self.repository.update_post(post_id, title)

    def delete_post(self, post_id: int):
        return self.repository.delete_post(post_id)
