import asyncio

import httpx
import pytest
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.database import Base
from app.models import Post, User
from async_lab.database import get_db
from async_lab.main import app


@pytest.mark.skip(reason="TODO 1~3 완료 후 이 줄을 삭제하세요.")
def test_async_post_lookup():
    async def check():
        engine = create_async_engine("sqlite+aiosqlite:///:memory:")
        factory = async_sessionmaker(engine, expire_on_commit=False)
        async with engine.begin() as connection:
            await connection.run_sync(Base.metadata.create_all)
        async with factory.begin() as db:
            db.add(User(id=1, name="민수", age=23))
            await db.flush()
            db.add(Post(id=1, title="첫 번째 글", user_id=1))

        async def override_get_db():
            async with factory() as db:
                yield db

        previous = app.dependency_overrides.copy()
        app.dependency_overrides[get_db] = override_get_db
        try:
            async with httpx.AsyncClient(
                transport=httpx.ASGITransport(app=app),
                base_url="http://test",
            ) as client:
                response = await client.get("/posts/1")
                assert response.status_code == 200
                assert response.json() == {"id": 1, "title": "첫 번째 글", "user_id": 1}
                response = await client.get("/posts/999999999")
                assert response.status_code == 404
                assert response.json() == {"detail": "게시글을 찾을 수 없습니다."}
                for value in ("abc", "0", "-1"):
                    response = await client.get(f"/posts/{value}")
                    assert response.status_code == 422
        finally:
            app.dependency_overrides.clear()
            app.dependency_overrides.update(previous)
            await engine.dispose()

    asyncio.run(check())
