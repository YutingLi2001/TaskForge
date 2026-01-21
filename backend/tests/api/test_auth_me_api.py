import os
import unittest
from datetime import timedelta

os.environ.setdefault("DATABASE_URL", "sqlite+pysqlite:///:memory:")

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from backend.app import database as db
from backend.app.database import get_db


class AuthMeApiTests(unittest.TestCase):
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
        main.app.dependency_overrides[get_db] = override_get_db
        cls.client = TestClient(main.app)

    @classmethod
    def tearDownClass(cls):
        cls.engine.dispose()

    def setUp(self):
        db.Base.metadata.drop_all(bind=self.engine)
        db.Base.metadata.create_all(bind=self.engine)

    def _create_user(self, email: str, password: str):
        from backend.app.utils.auth import hash_password

        session = db.SessionLocal()
        try:
            user = self.User(
                email=email,
                hashed_password=hash_password(password),
                is_verified=True,
                is_active=True,
            )
            session.add(user)
            session.commit()
            session.refresh(user)
            return user
        finally:
            session.close()

    def test_me_with_valid_token_returns_user(self):
        user = self._create_user("user@example.com", "secret123")
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
        self._create_user("user@example.com", "secret123")
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
