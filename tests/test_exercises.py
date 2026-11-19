"""skip 줄을 지우고 직접 작성한다."""
import pytest
from app.models import Post
from sqlalchemy import func, select



def test_missing_post(client):
    response = client.get("/posts/999")
    
    assert response.status_code == 404
    assert response.json() == {"detail": "게시글을 찾을 수 없습니다."}


@pytest.mark.parametrize("post_id", ["abc", "0", "-1"])
def test_invalid_post_id(client, post_id):
    response = client.get(f"/posts/{post_id}")
    assert response.status_code == 422


def test_create_then_read(client):
    create = client.post("/posts", json={"title": "새 글", "user_id": 1})
    assert create.status_code == 201
    post_id = create.json()["id"]
    response = client.get(f"/posts/{post_id}")
    assert response.status_code == 200
    assert response.json() == {"id": post_id, "title": "새 글", "user_id": 1}



def test_post_limit(client, session_factory):
    # 준비: user_id=1의 글을 3개로 만든다
    with session_factory.begin() as db:
        db.add(Post(title="두 번째 글", user_id=1))
        db.add(Post(title="세 번째 글", user_id=1))

    # 실행: 네 번째 글 작성 요청
    response = client.post("/posts", json={"title": "네 번째 글", "user_id": 1})

    # 검증 1: 409와 오류 본문
    assert response.status_code == 409
    assert response.json() == {
        "detail": {"message": "사용자는 최대 3개까지 글을 작성할 수 있습니다."}
    }

    # 검증 2: DB에 저장된 글 수가 여전히 3개
    with session_factory() as db:
        count = db.scalar(
            select(func.count()).select_from(Post).where(Post.user_id == 1)
        )
    assert count == 3
