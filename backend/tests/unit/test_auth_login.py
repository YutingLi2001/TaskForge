import asyncio
import os
import unittest

from fastapi import HTTPException
from pydantic import ValidationError
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool
from starlette.requests import Request

from backend.app.models.user import User
from backend.app.routers.auth import login
from backend.app.schemas.user import LoginRequest
from backend.app.utils.auth import hash_password
from backend.tests.utils.migrations import build_test_db_url, reset_database


class AuthLoginTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.database_url = build_test_db_url("auth_login_unit", async_driver=True)
        os.environ["DATABASE_URL"] = cls.database_url
        cls.engine = create_async_engine(
            cls.database_url,
            connect_args={"check_same_thread": False},
            poolclass=NullPool,
        )
        cls.SessionLocal = async_sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=cls.engine,
            class_=AsyncSession,
            expire_on_commit=False,
        )
        reset_database(cls.database_url)

    @classmethod
    def tearDownClass(cls):
        asyncio.run(cls.engine.dispose())

    def setUp(self):
        asyncio.run(self._reset_db())

    async def _reset_db(self):
        await asyncio.to_thread(reset_database, self.database_url)

    async def _create_user(self, session: AsyncSession, email: str, password: str) -> User:
        user = User(
            email=email,
            hashed_password=hash_password(password),
            is_verified=True,
            is_active=True,
        )
        session.add(user)
        await session.commit()
        await session.refresh(user)
        return user

    def _request(self) -> Request:
        return Request({"type": "http", "client": ("127.0.0.1", 12345)})

    def test_login_success_returns_token(self):
        async def run():
            async with self.SessionLocal() as session:
                await self._create_user(session, "user@example.com", "secret123")
                payload = LoginRequest(email="user@example.com", password="secret123")
                return await login(payload, request=self._request(), db=session)

        response = asyncio.run(run())

        self.assertEqual(response.data.user.email, "user@example.com")
        self.assertEqual(response.data.token_type, "bearer")
        self.assertTrue(response.data.access_token)
        self.assertTrue(response.data.refresh_token)

    def test_login_invalid_password(self):
        async def run():
            async with self.SessionLocal() as session:
                await self._create_user(session, "user@example.com", "secret123")
                payload = LoginRequest(email="user@example.com", password="wrongpass")
                return await login(payload, request=self._request(), db=session)

        with self.assertRaises(HTTPException) as ctx:
            asyncio.run(run())

        self.assertEqual(ctx.exception.status_code, 401)

    def test_login_invalid_email(self):
        async def run():
            async with self.SessionLocal() as session:
                payload = LoginRequest(email="nope@example.com", password="secret123")
                return await login(payload, request=self._request(), db=session)

        with self.assertRaises(HTTPException) as ctx:
            asyncio.run(run())

        self.assertEqual(ctx.exception.status_code, 401)

    def test_login_invalid_email_format(self):
        with self.assertRaises(ValidationError):
            LoginRequest(email="not-an-email", password="secret123")

    def test_login_short_password(self):
        with self.assertRaises(ValidationError):
            LoginRequest(email="short@example.com", password="123")

    def test_login_long_password(self):
        with self.assertRaises(ValidationError):
            LoginRequest(email="long@example.com", password="a" * 65)


if __name__ == "__main__":
    unittest.main()
