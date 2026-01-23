from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import declarative_base
from sqlalchemy.pool import StaticPool

from .config import DATABASE_URL

engine_kwargs: dict[str, object] = {}
if DATABASE_URL.startswith("sqlite"):
    engine_kwargs["connect_args"] = {"check_same_thread": False}
    if ":memory:" in DATABASE_URL:
        engine_kwargs["poolclass"] = StaticPool

engine = create_async_engine(DATABASE_URL, **engine_kwargs)
SessionLocal = async_sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

Base = declarative_base()


async def get_db():
    """Dependency for getting database sessions."""
    async with SessionLocal() as db:
        yield db
