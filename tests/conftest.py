import os

# 앱 import 전 테스트 프로세스의 접속 주소를 고정한다.
# 쿼리는 아래 get_db override로 만든 임시 SQLite에만 실행된다.
os.environ["DATABASE_URL"] = "mysql+pymysql://seminar:lab6-local-only@127.0.0.1:3308/seminar_lab6"

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.main import app
from app.models import Post, User


@pytest.fixture
def session_factory():
    engine = create_engine(
        "sqlite+pysqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    @event.listens_for(engine, "connect")
    def enable_foreign_keys(connection, _):
        connection.execute("PRAGMA foreign_keys=ON")

    Base.metadata.create_all(engine)
    factory = sessionmaker(bind=engine, expire_on_commit=False)
    with factory.begin() as db:
        db.add(User(id=1, name="민수", age=23))
        db.flush()
        db.add(Post(id=1, title="첫 번째 글", user_id=1))
    try:
        yield factory
    finally:
        engine.dispose()


@pytest.fixture
def client(session_factory):
    def override_get_db():
        with session_factory() as db:
            yield db

    previous = app.dependency_overrides.copy()
    app.dependency_overrides[get_db] = override_get_db
    try:
        with TestClient(app) as test_client:
            yield test_client
    finally:
        app.dependency_overrides.clear()
        app.dependency_overrides.update(previous)
