import os
import unittest
from datetime import datetime, timedelta, timezone

os.environ.setdefault("DATABASE_URL", "sqlite+pysqlite:///:memory:")

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from backend.app import database as db
from backend.app.database import get_db
from backend.app import config


class AuthLoginApiTests(unittest.TestCase):
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
        from backend.app.models.user import User
        cls.User = User
        cls.auth_router = __import__("backend.app.routers.auth", fromlist=["auth"])
        main.app.dependency_overrides[get_db] = override_get_db
        cls.client = TestClient(main.app)

    @classmethod
    def tearDownClass(cls):
        cls.engine.dispose()

    def setUp(self):
        db.Base.metadata.drop_all(bind=self.engine)
        db.Base.metadata.create_all(bind=self.engine)
        self.auth_router._login_rate_limit.clear()

    def _create_user(self, email: str, password: str, *, is_verified: bool = True, is_active: bool = True):
        from backend.app.utils.auth import hash_password

        session = db.SessionLocal()
        try:
            user = self.User(
                email=email,
                hashed_password=hash_password(password),
                is_verified=is_verified,
                is_active=is_active,
            )
            session.add(user)
            session.commit()
        finally:
            session.close()

    def test_login_success(self):
        self._create_user("user@example.com", "secret123")
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
        self._create_user("user@example.com", "secret123")
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
        self._create_user("user@example.com", "secret123")
        response = self.client.post(
            "/api/auth/login",
            json={"email": "  User@Example.com  ", "password": "secret123"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["data"]["user"]["email"], "user@example.com")

    def test_login_disabled_account(self):
        self._create_user("user@example.com", "secret123", is_active=False)
        response = self.client.post(
            "/api/auth/login",
            json={"email": "user@example.com", "password": "secret123"},
        )

        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.json().get("detail"), "Account is disabled.")

    def test_login_unverified_account_allows_login(self):
        self._create_user("user@example.com", "secret123", is_verified=False)
        response = self.client.post(
            "/api/auth/login",
            json={"email": "user@example.com", "password": "secret123"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.json()["data"]["user"]["is_verified"])

    def test_login_locked_account(self):
        session = db.SessionLocal()
        try:
            user = self.User(
                email="user@example.com",
                hashed_password=__import__("backend.app.utils.auth", fromlist=["hash_password"]).hash_password("secret123"),
                is_verified=True,
                is_active=True,
                locked_until=datetime.now(timezone.utc).replace(tzinfo=None) + timedelta(minutes=5),
            )
            session.add(user)
            session.commit()
        finally:
            session.close()

        response = self.client.post(
            "/api/auth/login",
            json={"email": "user@example.com", "password": "secret123"},
        )

        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.json().get("detail"), "Account is temporarily locked. Try again later.")

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
        self.assertEqual(response.json().get("detail"), "Too many login attempts. Try again later.")

    def test_refresh_token_rotation_and_logout(self):
        self._create_user("user@example.com", "secret123")
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
        self._create_user("user@example.com", "secret123")
        response = self.client.post(
            "/api/auth/login",
            json={"email": "user@example.com", "password": "secret123", "remember_me": True},
        )
        self.assertEqual(response.status_code, 200)

        session = db.SessionLocal()
        try:
            user = session.query(self.User).filter(self.User.email == "user@example.com").first()
            self.assertIsNotNone(user)
            self.assertIsNotNone(user.refresh_token_expires_at)
            delta = user.refresh_token_expires_at - datetime.now(timezone.utc).replace(tzinfo=None)
            self.assertGreater(delta, timedelta(days=config.REMEMBER_ME_REFRESH_DAYS - 1))
        finally:
            session.close()


if __name__ == "__main__":
    unittest.main()
