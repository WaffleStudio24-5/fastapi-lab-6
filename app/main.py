from contextlib import asynccontextmanager
from typing import Annotated

from fastapi import Depends, FastAPI
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import Engine, get_db
from app.routers import post_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    Engine.dispose()


app = FastAPI(title="6주차 실습 — 완성된 동기 CRUD", lifespan=lifespan)
app.include_router(post_router)


@app.get("/health", tags=["연결 확인"])
def health(db: Annotated[Session, Depends(get_db)]):
    db.scalar(select(1))
    return {"status": "ok"}
