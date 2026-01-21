import unittest

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from pydantic import ValidationError
from fastapi import HTTPException

from backend.app.database import Base
from backend.app.models.user import User
from backend.app.routers.auth import login
from backend.app.schemas.user import LoginRequest
from backend.app.utils.auth import hash_password


class AuthLoginTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.engine = create_engine(
            "sqlite+pysqlite:///:memory:",
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
        )
        cls.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=cls.engine)
        Base.metadata.create_all(bind=cls.engine)

    @classmethod
    def tearDownClass(cls):
        cls.engine.dispose()

    def setUp(self):
        Base.metadata.drop_all(bind=self.engine)
        Base.metadata.create_all(bind=self.engine)
        self.db = self.SessionLocal()

    def tearDown(self):
        self.db.close()

    def _create_user(self, email: str, password: str) -> User:
        user = User(email=email, hashed_password=hash_password(password))
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    def test_login_success_returns_token(self):
        self._create_user("user@example.com", "secret123")
        payload = LoginRequest(email="user@example.com", password="secret123")

        response = login(payload, db=self.db)

        self.assertEqual(response.data.user.email, "user@example.com")
        self.assertEqual(response.data.token_type, "bearer")
        self.assertTrue(response.data.access_token)

    def test_login_invalid_password(self):
        self._create_user("user@example.com", "secret123")
        payload = LoginRequest(email="user@example.com", password="wrongpass")

        with self.assertRaises(HTTPException) as ctx:
            login(payload, db=self.db)

        self.assertEqual(ctx.exception.status_code, 401)

    def test_login_invalid_email(self):
        payload = LoginRequest(email="nope@example.com", password="secret123")

        with self.assertRaises(HTTPException) as ctx:
            login(payload, db=self.db)

        self.assertEqual(ctx.exception.status_code, 401)

    def test_login_invalid_email_format(self):
        with self.assertRaises(ValidationError):
            LoginRequest(email="not-an-email", password="secret123")

    def test_login_short_password(self):
        with self.assertRaises(ValidationError):
            LoginRequest(email="short@example.com", password="123")


if __name__ == "__main__":
    unittest.main()
