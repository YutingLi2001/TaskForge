import os
import unittest

os.environ.setdefault("DATABASE_URL", "sqlite+pysqlite:///:memory:")

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from backend.app import database as db
from backend.app.database import get_db


class ProjectsApiTests(unittest.TestCase):
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
        from backend.app.models.project import Project
        cls.User = User
        cls.Project = Project
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

    def _auth_header_for(self, email: str):
        from backend.app.utils.auth import create_access_token

        token = create_access_token({"sub": email})
        return {"Authorization": f"Bearer {token}"}

    def test_list_projects_empty_for_new_user(self):
        user = self._create_user("user@example.com", "secret123")
        response = self.client.get(
            "/api/projects",
            headers=self._auth_header_for(user.email),
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["data"], [])

    def test_create_project_returns_project(self):
        user = self._create_user("user@example.com", "secret123")
        response = self.client.post(
            "/api/projects",
            json={"name": "My Project"},
            headers=self._auth_header_for(user.email),
        )

        self.assertEqual(response.status_code, 201)
        body = response.json()
        self.assertEqual(body["data"]["name"], "My Project")
        self.assertEqual(body["data"]["user_id"], user.id)

    def test_list_projects_only_returns_current_user(self):
        user_a = self._create_user("a@example.com", "secret123")
        user_b = self._create_user("b@example.com", "secret123")

        session = db.SessionLocal()
        try:
            session.add(self.Project(name="A project", user_id=user_a.id))
            session.add(self.Project(name="B project", user_id=user_b.id))
            session.commit()
        finally:
            session.close()

        response = self.client.get(
            "/api/projects",
            headers=self._auth_header_for(user_a.email),
        )

        self.assertEqual(response.status_code, 200)
        data = response.json()["data"]
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["name"], "A project")

    def test_create_project_empty_name_returns_422(self):
        user = self._create_user("user@example.com", "secret123")
        response = self.client.post(
            "/api/projects",
            json={"name": ""},
            headers=self._auth_header_for(user.email),
        )

        self.assertEqual(response.status_code, 422)

    def test_unauthenticated_requests_return_401(self):
        response = self.client.get("/api/projects")
        self.assertEqual(response.status_code, 401)

        response = self.client.post("/api/projects", json={"name": "Test"})
        self.assertEqual(response.status_code, 401)


if __name__ == "__main__":
    unittest.main()
