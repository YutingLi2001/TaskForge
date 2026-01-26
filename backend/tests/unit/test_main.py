import asyncio
import unittest

from fastapi import HTTPException
from sqlalchemy.exc import OperationalError
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool

from backend.app import database as db
from backend.app import main


class MainTests(unittest.TestCase):
    def setUp(self):
        self._original_engine = db.engine
        self._original_sessionlocal = db.SessionLocal
        self._engine = None

    def tearDown(self):
        db.engine = self._original_engine
        db.SessionLocal = self._original_sessionlocal
        if self._engine is not None:
            asyncio.run(self._engine.dispose())

    def _setup_sqlite(self):
        engine = create_async_engine(
            "sqlite+aiosqlite:///:memory:",
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
        )
        db.engine = engine
        db.SessionLocal = async_sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=engine,
            class_=AsyncSession,
            expire_on_commit=False,
        )
        self._engine = engine

    def test_health_check_success(self):
        self._setup_sqlite()
        result = asyncio.run(main.health_check())
        self.assertEqual(result, {"status": "healthy"})

    def test_health_check_database_unavailable(self):
        class FailingSession:
            async def __aenter__(self):
                return self

            async def __aexit__(self, exc_type, exc, tb):
                return False

            async def execute(self, *args, **kwargs):
                raise OperationalError("SELECT 1", {}, OSError("boom"))

        db.SessionLocal = lambda: FailingSession()

        with self.assertRaises(HTTPException) as ctx:
            asyncio.run(main.health_check())

        self.assertEqual(ctx.exception.status_code, 503)

    def test_lifespan_initializes_database(self):
        self._setup_sqlite()

        async def run():
            async with main.lifespan(main.app):
                return True

        self.assertTrue(asyncio.run(run()))

    def test_init_db_retries_and_raises(self):
        class FailingConnection:
            async def __aenter__(self):
                raise OperationalError("SELECT 1", {}, OSError("boom"))

            async def __aexit__(self, exc_type, exc, tb):
                return False

        class FailingEngine:
            def begin(self):
                return FailingConnection()

        db.engine = FailingEngine()

        with self.assertRaises(OperationalError):
            asyncio.run(main.init_db(max_attempts=1, delay_seconds=0))


if __name__ == "__main__":
    unittest.main()
