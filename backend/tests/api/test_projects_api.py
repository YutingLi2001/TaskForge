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

    def test_get_project_returns_project_for_owner(self):
        user = self._create_user("owner@example.com", "secret123")
        session = db.SessionLocal()
        try:
            project = self.Project(name="Owner Project", user_id=user.id)
            session.add(project)
            session.commit()
            session.refresh(project)
        finally:
            session.close()

        response = self.client.get(
            f"/api/projects/{project.id}",
            headers=self._auth_header_for(user.email),
        )

        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertEqual(body["data"]["id"], project.id)
        self.assertEqual(body["data"]["name"], "Owner Project")
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

    def test_get_project_returns_404_for_missing_project(self):
        user = self._create_user("user@example.com", "secret123")
        response = self.client.get(
            "/api/projects/9999",
            headers=self._auth_header_for(user.email),
        )

        self.assertEqual(response.status_code, 404)

    def test_get_project_returns_403_for_non_owner(self):
        owner = self._create_user("owner@example.com", "secret123")
        other = self._create_user("other@example.com", "secret123")
        session = db.SessionLocal()
        try:
            project = self.Project(name="Owner Project", user_id=owner.id)
            session.add(project)
            session.commit()
            session.refresh(project)
        finally:
            session.close()

        response = self.client.get(
            f"/api/projects/{project.id}",
            headers=self._auth_header_for(other.email),
        )

        self.assertEqual(response.status_code, 403)

    def test_unauthenticated_requests_return_401(self):
        response = self.client.get("/api/projects")
        self.assertEqual(response.status_code, 401)

        response = self.client.post("/api/projects", json={"name": "Test"})
        self.assertEqual(response.status_code, 401)

        response = self.client.get("/api/projects/1")
        self.assertEqual(response.status_code, 401)

        response = self.client.put("/api/projects/1", json={"name": "Updated"})
        self.assertEqual(response.status_code, 401)

    # Story 2.3: Edit Project tests

    def test_update_project_returns_updated_project(self):
        user = self._create_user("user@example.com", "secret123")
        session = db.SessionLocal()
        try:
            project = self.Project(name="Original Name", user_id=user.id)
            session.add(project)
            session.commit()
            session.refresh(project)
            project_id = project.id
            original_updated_at = project.updated_at
        finally:
            session.close()

        response = self.client.put(
            f"/api/projects/{project_id}",
            json={"name": "Updated Name"},
            headers=self._auth_header_for(user.email),
        )

        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertEqual(body["data"]["id"], project_id)
        self.assertEqual(body["data"]["name"], "Updated Name")
        self.assertEqual(body["data"]["user_id"], user.id)

    def test_update_project_empty_name_returns_422(self):
        user = self._create_user("user@example.com", "secret123")
        session = db.SessionLocal()
        try:
            project = self.Project(name="Original Name", user_id=user.id)
            session.add(project)
            session.commit()
            session.refresh(project)
            project_id = project.id
        finally:
            session.close()

        response = self.client.put(
            f"/api/projects/{project_id}",
            json={"name": ""},
            headers=self._auth_header_for(user.email),
        )

        self.assertEqual(response.status_code, 422)

    def test_update_project_whitespace_name_returns_422(self):
        user = self._create_user("user@example.com", "secret123")
        session = db.SessionLocal()
        try:
            project = self.Project(name="Original Name", user_id=user.id)
            session.add(project)
            session.commit()
            session.refresh(project)
            project_id = project.id
        finally:
            session.close()

        response = self.client.put(
            f"/api/projects/{project_id}",
            json={"name": "   "},
            headers=self._auth_header_for(user.email),
        )

        self.assertEqual(response.status_code, 422)

    def test_update_project_returns_404_for_missing_project(self):
        user = self._create_user("user@example.com", "secret123")
        response = self.client.put(
            "/api/projects/9999",
            json={"name": "Updated Name"},
            headers=self._auth_header_for(user.email),
        )

        self.assertEqual(response.status_code, 404)

    def test_update_project_returns_403_for_non_owner(self):
        owner = self._create_user("owner@example.com", "secret123")
        other = self._create_user("other@example.com", "secret123")
        session = db.SessionLocal()
        try:
            project = self.Project(name="Owner Project", user_id=owner.id)
            session.add(project)
            session.commit()
            session.refresh(project)
            project_id = project.id
        finally:
            session.close()

        response = self.client.put(
            f"/api/projects/{project_id}",
            json={"name": "Hacked Name"},
            headers=self._auth_header_for(other.email),
        )

        self.assertEqual(response.status_code, 403)

    def test_update_project_trims_whitespace(self):
        user = self._create_user("user@example.com", "secret123")
        session = db.SessionLocal()
        try:
            project = self.Project(name="Original Name", user_id=user.id)
            session.add(project)
            session.commit()
            session.refresh(project)
            project_id = project.id
        finally:
            session.close()

        response = self.client.put(
            f"/api/projects/{project_id}",
            json={"name": "  Trimmed Name  "},
            headers=self._auth_header_for(user.email),
        )

        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertEqual(body["data"]["name"], "Trimmed Name")


if __name__ == "__main__":
    unittest.main()
