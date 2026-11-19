from sqlalchemy import create_engine
from sqlalchemy.engine import make_url
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from app.settings import settings

Engine = create_engine(settings.database_url, echo=True)
SessionLocal = sessionmaker(
    bind=Engine,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False,
)
Base = declarative_base()

url = make_url(settings.database_url)
async_url = url.set(
    drivername={"mysql": "mysql+asyncmy", "sqlite": "sqlite+aiosqlite"}[url.get_backend_name()]
)
AsyncEngine = create_async_engine(async_url, echo=True)
AsyncSessionLocal = async_sessionmaker(
    bind=AsyncEngine, autoflush=False, expire_on_commit=False
)


async def get_db():
    async with AsyncSessionLocal() as db:
        yield db