from sqlalchemy import func, select

from app.models import Post, User


def test_third_post_allowed_fourth_rejected(client, session_factory):
    for title in ("두 번째 글", "세 번째 글"):
        assert client.post("/posts", json={"title": title, "user_id": 1}).status_code == 201
    response = client.post("/posts", json={"title": "네 번째 글", "user_id": 1})
    assert response.status_code == 409
    assert response.json() == {
        "detail": {"message": "사용자는 최대 3개까지 글을 작성할 수 있습니다."}
    }
    with session_factory() as db:
        assert db.scalar(select(func.count()).select_from(Post).where(Post.user_id == 1)) == 3


def test_other_users_posts_do_not_count(client, session_factory):
    with session_factory.begin() as db:
        db.add(User(id=2, name="지연", age=19))
        db.flush()
        db.add_all([Post(title=f"다른 글 {i}", user_id=2) for i in range(3)])
    response = client.post("/posts", json={"title": "내 글", "user_id": 1})
    assert response.status_code == 201


def test_health_and_error_documentation(client):
    assert client.get("/health").json() == {"status": "ok"}
    schema = client.get("/openapi.json").json()
    assert "409" in schema["paths"]["/posts"]["post"]["responses"]
