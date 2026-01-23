import asyncio
import unittest
from datetime import timedelta

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool

from backend.app.database import Base
from backend.app.models.user import User
from backend.app.utils.auth import create_access_token, get_current_user, hash_password


class AuthDependencyTests(unittest.TestCase):
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

    async def _create_user(
        self,
        session: AsyncSession,
        email: str,
        password: str,
        *,
        is_active: bool = True,
    ) -> User:
        user = User(
            email=email,
            hashed_password=hash_password(password),
            is_verified=True,
            is_active=is_active,
        )
        session.add(user)
        await session.commit()
        await session.refresh(user)
        return user

    def test_get_current_user_with_valid_token(self):
        async def run():
            async with self.SessionLocal() as session:
                user = await self._create_user(session, "user@example.com", "secret123")
                token = create_access_token({"sub": user.email})
                return await get_current_user(token=token, db=session)

        resolved = asyncio.run(run())

        self.assertEqual(resolved.email, "user@example.com")

    def test_get_current_user_with_expired_token_raises_401(self):
        async def run():
            async with self.SessionLocal() as session:
                await self._create_user(session, "user@example.com", "secret123")
                token = create_access_token(
                    {"sub": "user@example.com"},
                    expires_delta=timedelta(minutes=-1),
                )
                return await get_current_user(token=token, db=session)

        with self.assertRaises(HTTPException) as ctx:
            asyncio.run(run())

        self.assertEqual(ctx.exception.status_code, 401)

    def test_get_current_user_with_inactive_user_raises_403(self):
        async def run():
            async with self.SessionLocal() as session:
                user = await self._create_user(
                    session, "inactive@example.com", "secret123", is_active=False
                )
                token = create_access_token({"sub": user.email})
                return await get_current_user(token=token, db=session)

        with self.assertRaises(HTTPException) as ctx:
            asyncio.run(run())

        self.assertEqual(ctx.exception.status_code, 403)


if __name__ == "__main__":
    unittest.main()
