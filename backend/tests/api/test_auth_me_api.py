import asyncio
import os
import unittest
from datetime import timedelta

DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite+aiosqlite:///:memory:")
os.environ["DATABASE_URL"] = DATABASE_URL

from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool

from backend.app import database as db
from backend.app.database import get_db


class AuthMeApiTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if DATABASE_URL.startswith("sqlite"):
            cls.engine = create_async_engine(
                DATABASE_URL,
                connect_args={"check_same_thread": False},
                poolclass=StaticPool,
            )
        else:
            cls.engine = create_async_engine(DATABASE_URL)
        db.engine = cls.engine
        db.SessionLocal = async_sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=cls.engine,
            class_=AsyncSession,
            expire_on_commit=False,
        )
        asyncio.run(cls._create_tables())

        async def override_get_db():
            async with db.SessionLocal() as session:
                yield session

        from backend.app import main
        from backend.app.models.user import User

        cls.User = User
        main.app.dependency_overrides[get_db] = override_get_db
        cls.client = TestClient(main.app)

    @classmethod
    async def _create_tables(cls):
        async with cls.engine.begin() as conn:
            await conn.run_sync(db.Base.metadata.create_all)

    @classmethod
    async def _drop_tables(cls):
        async with cls.engine.begin() as conn:
            await conn.run_sync(db.Base.metadata.drop_all)

    @classmethod
    def tearDownClass(cls):
        asyncio.run(cls.engine.dispose())

    def setUp(self):
        asyncio.run(self._reset_db())

    async def _reset_db(self):
        await self._drop_tables()
        await self._create_tables()

    async def _create_user(self, session: AsyncSession, email: str, password: str):
        from backend.app.utils.auth import hash_password

        user = self.User(
            email=email,
            hashed_password=hash_password(password),
            is_verified=True,
            is_active=True,
        )
        session.add(user)
        await session.commit()
        await session.refresh(user)
        return user

    def test_me_with_valid_token_returns_user(self):
        async def setup():
            async with db.SessionLocal() as session:
                return await self._create_user(session, "user@example.com", "secret123")

        user = asyncio.run(setup())
        from backend.app.utils.auth import create_access_token

        token = create_access_token({"sub": user.email})
        response = self.client.get(
            "/api/auth/me",
            headers={"Authorization": f"Bearer {token}"},
        )

        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertEqual(body["data"]["email"], "user@example.com")
        self.assertNotIn("is_active", body["data"])
        self.assertNotIn("is_verified", body["data"])

    def test_me_missing_token_returns_401(self):
        response = self.client.get("/api/auth/me")

        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json().get("detail"), "Not authenticated")

    def test_me_invalid_token_returns_401(self):
        response = self.client.get(
            "/api/auth/me",
            headers={"Authorization": "Bearer invalid.token.value"},
        )

        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json().get("detail"), "Could not validate credentials")

    def test_me_expired_token_returns_401(self):
        async def setup():
            async with db.SessionLocal() as session:
                await self._create_user(session, "user@example.com", "secret123")

        asyncio.run(setup())
        from backend.app.utils.auth import create_access_token

        token = create_access_token(
            {"sub": "user@example.com"},
            expires_delta=timedelta(minutes=-1),
        )
        response = self.client.get(
            "/api/auth/me",
            headers={"Authorization": f"Bearer {token}"},
        )

        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json().get("detail"), "Could not validate credentials")


if __name__ == "__main__":
    unittest.main()
