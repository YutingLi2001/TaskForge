import unittest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from pydantic import ValidationError
from fastapi import HTTPException

from backend.app.database import Base
from backend.app.models.user import User
from backend.app.routers.auth import register
from backend.app.schemas.user import UserCreate


class AuthRegistrationTests(unittest.TestCase):
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

    def test_register_success_hashes_password(self):
        payload = UserCreate(email="user@example.com", password="secret123")
        response = register(payload, db=self.db)

        self.assertEqual(response.data.email, "user@example.com")
        self.assertIsNotNone(response.data.id)
        self.assertIsNotNone(response.data.created_at)

        saved_user = self.db.query(User).filter(User.email == "user@example.com").first()
        self.assertIsNotNone(saved_user)
        self.assertNotEqual(saved_user.hashed_password, "secret123")

    def test_register_duplicate_email(self):
        payload = UserCreate(email="dup@example.com", password="secret123")
        register(payload, db=self.db)

        with self.assertRaises(HTTPException) as ctx:
            register(payload, db=self.db)

        self.assertEqual(ctx.exception.status_code, 400)

    def test_register_invalid_email(self):
        with self.assertRaises(ValidationError):
            UserCreate(email="not-an-email", password="secret123")

    def test_register_short_password(self):
        with self.assertRaises(ValidationError):
            UserCreate(email="short@example.com", password="123")

    def test_register_long_password(self):
        with self.assertRaises(ValidationError):
            UserCreate(email="long@example.com", password="a" * 65)

    def test_register_normalizes_email(self):
        payload = UserCreate(email="  User@Example.com  ", password="secret123")
        response = register(payload, db=self.db)
        self.assertEqual(response.data.email, "user@example.com")


if __name__ == "__main__":
    unittest.main()
