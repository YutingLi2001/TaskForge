import asyncio
import unittest
from datetime import timedelta

from fastapi import HTTPException
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from backend.app.database import Base
from backend.app.models.user import User
from backend.app.utils.auth import create_access_token, hash_password


class AuthDependencyTests(unittest.TestCase):
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

    def _create_user(self, email: str, password: str, *, is_active: bool = True) -> User:
        user = User(
            email=email,
            hashed_password=hash_password(password),
            is_verified=True,
            is_active=is_active,
        )
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    def test_get_current_user_with_valid_token(self):
        from backend.app.utils.auth import get_current_user

        user = self._create_user("user@example.com", "secret123")
        token = create_access_token({"sub": user.email})

        resolved = asyncio.run(get_current_user(token=token, db=self.db))

        self.assertEqual(resolved.email, "user@example.com")

    def test_get_current_user_with_expired_token_raises_401(self):
        from backend.app.utils.auth import get_current_user

        self._create_user("user@example.com", "secret123")
        token = create_access_token({"sub": "user@example.com"}, expires_delta=timedelta(minutes=-1))

        with self.assertRaises(HTTPException) as ctx:
            asyncio.run(get_current_user(token=token, db=self.db))

        self.assertEqual(ctx.exception.status_code, 401)

    def test_get_current_user_with_inactive_user_raises_403(self):
        from backend.app.utils.auth import get_current_user

        user = self._create_user("inactive@example.com", "secret123", is_active=False)
        token = create_access_token({"sub": user.email})

        with self.assertRaises(HTTPException) as ctx:
            asyncio.run(get_current_user(token=token, db=self.db))

        self.assertEqual(ctx.exception.status_code, 403)


if __name__ == "__main__":
    unittest.main()
