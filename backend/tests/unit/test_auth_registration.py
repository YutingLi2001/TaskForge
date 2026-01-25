import asyncio
import unittest

from fastapi import HTTPException
from pydantic import ValidationError
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool

from backend.app.database import Base
from backend.app.models.user import User
from backend.app.routers.auth import register
from backend.app.schemas.user import UserCreate


class AuthRegistrationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.engine = create_async_engine(
            "sqlite+aiosqlite:///:memory:",
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
        )
        cls.SessionLocal = async_sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=cls.engine,
            class_=AsyncSession,
            expire_on_commit=False,
        )
        asyncio.run(cls._create_tables())

    @classmethod
    async def _create_tables(cls):
        async with cls.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    @classmethod
    async def _drop_tables(cls):
        async with cls.engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)

    @classmethod
    def tearDownClass(cls):
        asyncio.run(cls.engine.dispose())

    def setUp(self):
        asyncio.run(self._reset_db())

    async def _reset_db(self):
        await self._drop_tables()
        await self._create_tables()

    def test_register_success_hashes_password(self):
        async def run():
            async with self.SessionLocal() as session:
                payload = UserCreate(email="user@example.com", password="secret123")
                response = await register(payload, db=session)
                user = await session.scalar(
                    select(User).where(User.email == "user@example.com")
                )
                return response, user

        response, user = asyncio.run(run())

        self.assertEqual(response.data.email, "user@example.com")
        self.assertIsNotNone(response.data.id)
        self.assertIsNotNone(response.data.created_at)
        self.assertIsNotNone(user)
        self.assertNotEqual(user.hashed_password, "secret123")

    def test_register_duplicate_email(self):
        async def run():
            async with self.SessionLocal() as session:
                payload = UserCreate(email="dup@example.com", password="secret123")
                await register(payload, db=session)

        asyncio.run(run())

        async def run_duplicate():
            async with self.SessionLocal() as dup_session:
                payload = UserCreate(email="dup@example.com", password="secret123")
                return await register(payload, db=dup_session)

        with self.assertRaises(HTTPException) as ctx:
            asyncio.run(run_duplicate())

        self.assertEqual(ctx.exception.status_code, 400)

    def test_register_invalid_email(self):
        with self.assertRaises(ValidationError):
            UserCreate(email="not-an-email", password="secret123")

    def test_register_short_password(self):
        with self.assertRaises(ValidationError):
            UserCreate(email="short@example.com", password="123")

    def test_register_long_password(self):
        with self.assertRaises(ValidationError):
            UserCreate(email="long@example.com", password="a" * 65)

    def test_register_normalizes_email(self):
        async def run():
            async with self.SessionLocal() as session:
                payload = UserCreate(email="  User@Example.com  ", password="secret123")
                return await register(payload, db=session)

        response = asyncio.run(run())
        self.assertEqual(response.data.email, "user@example.com")


if __name__ == "__main__":
    unittest.main()
