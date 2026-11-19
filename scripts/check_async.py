"""비동기 함수와 요청별 AsyncSession 구성을 확인한다. DB 접속은 하지 않는다."""

import asyncio
import inspect
import sys
from pathlib import Path

from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from app.database import get_db
from app.main import health
from app.repositories import PostRepository
from app.routers import post_router
from app.services import PostService


async def check_session():
    dependency = get_db()
    try:
        db = await anext(dependency)
        assert isinstance(db, AsyncSession), "get_db가 AsyncSession을 제공해야 합니다."
        assert isinstance(db.bind, AsyncEngine), "AsyncEngine에 연결해야 합니다."
    finally:
        await dependency.aclose()


def main():
    errors = []
    endpoints = [("GET /health", health)] + [
        (f"{'/'.join(sorted(route.methods))} {route.path}", route.endpoint)
        for route in post_router.routes
    ]
    for label, endpoint in endpoints:
        if not inspect.iscoroutinefunction(endpoint):
            errors.append(f"{label}: async def로 전환하세요.")
    for cls in (PostRepository, PostService):
        for name, method in vars(cls).items():
            if not name.startswith("_") and inspect.isfunction(method):
                if not inspect.iscoroutinefunction(method):
                    errors.append(f"{cls.__name__}.{name}: 비동기 DB 호출을 연결하세요.")
    if not inspect.isasyncgenfunction(get_db):
        errors.append("get_db: async def / async with / yield로 전환하세요.")
    if errors:
        raise SystemExit("\n".join(errors))
    asyncio.run(check_session())
    print(f"PASS: 엔드포인트 {len(endpoints)}개와 DB 의존성의 비동기 구조를 확인했습니다.")
    print("실제 DB 호출의 await와 API 응답은 pytest 및 MySQL에서도 확인하세요.")


if __name__ == "__main__":
    main()
