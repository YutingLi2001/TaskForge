import asyncio
import os
import unittest

from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool

from backend.tests.utils.migrations import build_test_db_url, reset_database

db = None
get_db = None
User = None


class AuthRegistrationApiTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.database_url = build_test_db_url("auth_registration_api", async_driver=True)
        os.environ["DATABASE_URL"] = cls.database_url
        database_url = cls.database_url

        global db, get_db, User
        from backend.app import database as db
        from backend.app.database import get_db
        from backend.app.models.user import User

        if database_url.startswith("sqlite"):
            cls.engine = create_async_engine(
                database_url,
                connect_args={"check_same_thread": False},
                poolclass=NullPool,
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
        reset_database(cls.database_url)

        async def override_get_db():
            async with db.SessionLocal() as session:
                yield session

        from backend.app import main

        main.app.dependency_overrides[get_db] = override_get_db
        cls.client = TestClient(main.app)

    def setUp(self):
        asyncio.run(self._reset_db())

    async def _reset_db(self):
        await asyncio.to_thread(reset_database, self.database_url)

    def test_register_success(self):
        response = self.client.post(
            "/api/auth/register",
            json={"email": "user@example.com", "password": "secret123"},
        )

        self.assertEqual(response.status_code, 201)
        body = response.json()
        self.assertEqual(body["data"]["email"], "user@example.com")
        self.assertIn("id", body["data"])
        self.assertIn("created_at", body["data"])

        async def fetch_user():
            async with db.SessionLocal() as session:
                return await session.scalar(
                    select(User).where(User.email == "user@example.com")
                )

        saved_user = asyncio.run(fetch_user())
        self.assertIsNotNone(saved_user)
        self.assertNotEqual(saved_user.hashed_password, "secret123")

    def test_register_duplicate_email_returns_400(self):
        self.client.post(
            "/api/auth/register",
            json={"email": "dup@example.com", "password": "secret123"},
        )
        response = self.client.post(
            "/api/auth/register",
            json={"email": "dup@example.com", "password": "secret123"},
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json().get("detail"), "Email already registered")

    def test_register_invalid_email_returns_422(self):
        response = self.client.post(
            "/api/auth/register",
            json={"email": "not-an-email", "password": "secret123"},
        )

        self.assertEqual(response.status_code, 422)

    def test_register_short_password_returns_422(self):
        response = self.client.post(
            "/api/auth/register",
            json={"email": "short@example.com", "password": "123"},
        )

        self.assertEqual(response.status_code, 422)

    def test_register_long_password_returns_422(self):
        response = self.client.post(
            "/api/auth/register",
            json={"email": "long@example.com", "password": "a" * 65},
        )

        self.assertEqual(response.status_code, 422)

    def test_register_normalizes_email(self):
        response = self.client.post(
            "/api/auth/register",
            json={"email": "  User@Example.com  ", "password": "secret123"},
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json()["data"]["email"], "user@example.com")

    def test_register_duplicate_email_case_insensitive(self):
        self.client.post(
            "/api/auth/register",
            json={"email": "User@Example.com", "password": "secret123"},
        )
        response = self.client.post(
            "/api/auth/register",
            json={"email": "user@example.com", "password": "secret123"},
        )

        self.assertEqual(response.status_code, 400)


if __name__ == "__main__":
    unittest.main()
