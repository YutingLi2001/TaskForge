import os
import unittest

os.environ.setdefault("DATABASE_URL", "sqlite+pysqlite:///:memory:")

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from backend.app import database as db
from backend.app.database import get_db


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
            user = self.User(email=email, hashed_password=hash_password(password))
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


if __name__ == "__main__":
    unittest.main()
