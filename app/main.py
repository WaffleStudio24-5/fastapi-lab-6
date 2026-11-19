from typing import Annotated

from fastapi import Depends, FastAPI
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.routers import post_router

app = FastAPI(title="5주차 실습")

app.include_router(post_router, tags=["Posts"])


@app.get("/health", tags=["연결 확인"])
def health(db: Annotated[Session, Depends(get_db)]):
    db.scalar(select(1))
    return {"status": "ok"}