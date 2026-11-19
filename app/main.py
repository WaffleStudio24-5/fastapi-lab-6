from contextlib import asynccontextmanager
from typing import Annotated

from fastapi import Depends, FastAPI
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import AsyncEngine, get_db
from app.routers import post_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        yield
    finally:
        await AsyncEngine.dispose()


app = FastAPI(title="6주차 실습", lifespan=lifespan)
app.include_router(post_router, tags=["Posts"])


@app.get("/health", tags=["연결 확인"])
async def health(db: Annotated[AsyncSession, Depends(get_db)]):
    await db.scalar(select(1))
    return {"status": "ok"}