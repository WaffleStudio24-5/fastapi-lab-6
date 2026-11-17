from contextlib import asynccontextmanager

from fastapi import FastAPI

from async_lab.database import engine
from async_lab.routers import post_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    await engine.dispose()


app = FastAPI(title="6주차 — 비동기 게시글 조회", lifespan=lifespan)
app.include_router(post_router)
