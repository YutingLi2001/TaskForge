import os
import unittest

os.environ.setdefault("DATABASE_URL", "sqlite+pysqlite:///:memory:")

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from backend.app import database as db
from backend.app.database import get_db
from backend.app.models.user import User


class AuthRegistrationApiTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.engine = create_engine(
            "sqlite+pysqlite:///:memory:",
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
        )
        db.engine = cls.engine
        db.SessionLocal = sessionmaker(
            autocommit=False, autoflush=False, bind=cls.engine
        )
        db.Base.metadata.create_all(bind=cls.engine)

        def override_get_db():
            session = db.SessionLocal()
            try:
                yield session
            finally:
                session.close()

        from backend.app import main

        main.app.dependency_overrides[get_db] = override_get_db
        cls.client = TestClient(main.app)

    def setUp(self):
        db.Base.metadata.drop_all(bind=self.engine)
        db.Base.metadata.create_all(bind=self.engine)

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

        session = db.SessionLocal()
        try:
            saved_user = (
                session.query(User)
                .filter(User.email == "user@example.com")
                .first()
            )
            self.assertIsNotNone(saved_user)
            self.assertNotEqual(saved_user.hashed_password, "secret123")
        finally:
            session.close()

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
