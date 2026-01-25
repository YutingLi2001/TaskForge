import asyncio
import os
import unittest
from datetime import datetime, timedelta, timezone

from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool, StaticPool

config = None
db = None
get_db = None


class AuthLoginApiTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        os.environ.setdefault("DATABASE_URL", "sqlite+aiosqlite:///:memory:")
        database_url = os.environ["DATABASE_URL"]

        global config, db, get_db
        from backend.app import config as config
        from backend.app import database as db
        from backend.app.database import get_db

        if database_url.startswith("sqlite"):
            cls.engine = create_async_engine(
                database_url,
                connect_args={"check_same_thread": False},
                poolclass=StaticPool,
            )
        else:
            cls.engine = create_async_engine(database_url, poolclass=NullPool)
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
        cls.auth_router = __import__("backend.app.routers.auth", fromlist=["auth"])
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
        self.auth_router._login_rate_limit.clear()

    async def _reset_db(self):
        await self._drop_tables()
        await self._create_tables()

    async def _create_user(
        self,
        session: AsyncSession,
        email: str,
        password: str,
        *,
        is_verified: bool = True,
        is_active: bool = True,
        locked_until: datetime | None = None,
    ):
        from backend.app.utils.auth import hash_password

        user = self.User(
            email=email,
            hashed_password=hash_password(password),
            is_verified=is_verified,
            is_active=is_active,
            locked_until=locked_until,
        )
        session.add(user)
        await session.commit()

    def test_login_success(self):
        async def setup():
            async with db.SessionLocal() as session:
                await self._create_user(session, "user@example.com", "secret123")

        asyncio.run(setup())
        response = self.client.post(
            "/api/auth/login",
            json={"email": "user@example.com", "password": "secret123"},
        )

        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertEqual(body["data"]["user"]["email"], "user@example.com")
        self.assertIn("access_token", body["data"])
        self.assertIn("refresh_token", body["data"])
        self.assertEqual(body["data"]["token_type"], "bearer")

    def test_login_invalid_credentials_returns_401(self):
        async def setup():
            async with db.SessionLocal() as session:
                await self._create_user(session, "user@example.com", "secret123")

        asyncio.run(setup())
        response = self.client.post(
            "/api/auth/login",
            json={"email": "user@example.com", "password": "wrongpass"},
        )

        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json().get("detail"), "Invalid email or password")

    def test_login_invalid_email_returns_422(self):
        response = self.client.post(
            "/api/auth/login",
            json={"email": "not-an-email", "password": "secret123"},
        )

        self.assertEqual(response.status_code, 422)

    def test_login_case_insensitive_and_trimmed_email(self):
        async def setup():
            async with db.SessionLocal() as session:
                await self._create_user(session, "user@example.com", "secret123")

        asyncio.run(setup())
        response = self.client.post(
            "/api/auth/login",
            json={"email": "  User@Example.com  ", "password": "secret123"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["data"]["user"]["email"], "user@example.com")

    def test_login_disabled_account(self):
        async def setup():
            async with db.SessionLocal() as session:
                await self._create_user(
                    session, "user@example.com", "secret123", is_active=False
                )

        asyncio.run(setup())
        response = self.client.post(
            "/api/auth/login",
            json={"email": "user@example.com", "password": "secret123"},
        )

        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.json().get("detail"), "Account is disabled.")

    def test_login_unverified_account_allows_login(self):
        async def setup():
            async with db.SessionLocal() as session:
                await self._create_user(
                    session, "user@example.com", "secret123", is_verified=False
                )

        asyncio.run(setup())
        response = self.client.post(
            "/api/auth/login",
            json={"email": "user@example.com", "password": "secret123"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.json()["data"]["user"]["is_verified"])

    def test_login_locked_account(self):
        async def setup():
            async with db.SessionLocal() as session:
                locked_until = datetime.now(timezone.utc).replace(tzinfo=None) + timedelta(minutes=5)
                await self._create_user(
                    session,
                    "user@example.com",
                    "secret123",
                    locked_until=locked_until,
                )

        asyncio.run(setup())

        response = self.client.post(
            "/api/auth/login",
            json={"email": "user@example.com", "password": "secret123"},
        )

        self.assertEqual(response.status_code, 403)
        self.assertEqual(
            response.json().get("detail"),
            "Account is temporarily locked. Try again later.",
        )

    def test_login_rate_limited(self):
        original_max = config.LOGIN_RATE_LIMIT_MAX_ATTEMPTS
        try:
            config.LOGIN_RATE_LIMIT_MAX_ATTEMPTS = 2
            for _ in range(2):
                self.client.post(
                    "/api/auth/login",
                    json={"email": "missing@example.com", "password": "secret123"},
                )
            response = self.client.post(
                "/api/auth/login",
                json={"email": "missing@example.com", "password": "secret123"},
            )
        finally:
            config.LOGIN_RATE_LIMIT_MAX_ATTEMPTS = original_max

        self.assertEqual(response.status_code, 429)
        self.assertEqual(
            response.json().get("detail"),
            "Too many login attempts. Try again later.",
        )

    def test_refresh_token_rotation_and_logout(self):
        async def setup():
            async with db.SessionLocal() as session:
                await self._create_user(session, "user@example.com", "secret123")

        asyncio.run(setup())
        login_response = self.client.post(
            "/api/auth/login",
            json={"email": "user@example.com", "password": "secret123"},
        )
        refresh_token = login_response.json()["data"]["refresh_token"]

        refresh_response = self.client.post(
            "/api/auth/refresh",
            json={"refresh_token": refresh_token},
        )
        self.assertEqual(refresh_response.status_code, 200)
        self.assertIn("access_token", refresh_response.json()["data"])
        self.assertIn("refresh_token", refresh_response.json()["data"])

        logout_response = self.client.post(
            "/api/auth/logout",
            json={"refresh_token": refresh_token},
        )
        self.assertEqual(logout_response.status_code, 204)

        refresh_after_logout = self.client.post(
            "/api/auth/refresh",
            json={"refresh_token": refresh_token},
        )
        self.assertEqual(refresh_after_logout.status_code, 401)

    def test_remember_me_extends_refresh_expiry(self):
        async def setup():
            async with db.SessionLocal() as session:
                await self._create_user(session, "user@example.com", "secret123")

        asyncio.run(setup())
        response = self.client.post(
            "/api/auth/login",
            json={"email": "user@example.com", "password": "secret123", "remember_me": True},
        )
        self.assertEqual(response.status_code, 200)

        async def fetch_user():
            async with db.SessionLocal() as session:
                return await session.scalar(
                    select(self.User).where(self.User.email == "user@example.com")
                )

        user = asyncio.run(fetch_user())
        self.assertIsNotNone(user)
        self.assertIsNotNone(user.refresh_token_expires_at)
        delta = user.refresh_token_expires_at - datetime.now(timezone.utc).replace(tzinfo=None)
        self.assertGreater(delta, timedelta(days=config.REMEMBER_ME_REFRESH_DAYS - 1))


if __name__ == "__main__":
    unittest.main()
