import asyncio
import os
import unittest

DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite+aiosqlite:///:memory:")
os.environ["DATABASE_URL"] = DATABASE_URL

from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool

from backend.app import database as db
from backend.app.database import get_db


class ProjectsApiTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if DATABASE_URL.startswith("sqlite"):
            cls.engine = create_async_engine(
                DATABASE_URL,
                connect_args={"check_same_thread": False},
                poolclass=StaticPool,
            )
        else:
            cls.engine = create_async_engine(DATABASE_URL)
        db.engine = cls.engine
        db.SessionLocal = async_sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=cls.engine,
            class_=AsyncSession,
            expire_on_commit=False,
        )
        asyncio.run(cls._create_tables())

        async def override_get_db():
            async with db.SessionLocal() as session:
                yield session

        from backend.app import main
        from backend.app.models.project import Project
        from backend.app.models.task import Task
        from backend.app.models.user import User

        cls.User = User
        cls.Project = Project
        cls.Task = Task
        main.app.dependency_overrides[get_db] = override_get_db
        cls.client = TestClient(main.app)

    @classmethod
    async def _create_tables(cls):
        async with cls.engine.begin() as conn:
            await conn.run_sync(db.Base.metadata.create_all)

    @classmethod
    async def _drop_tables(cls):
        async with cls.engine.begin() as conn:
            await conn.run_sync(db.Base.metadata.drop_all)

    @classmethod
    def tearDownClass(cls):
        asyncio.run(cls.engine.dispose())

    def setUp(self):
        asyncio.run(self._reset_db())

    async def _reset_db(self):
        await self._drop_tables()
        await self._create_tables()

    async def _create_user(self, session: AsyncSession, email: str, password: str):
        from backend.app.utils.auth import hash_password

        user = self.User(
            email=email,
            hashed_password=hash_password(password),
            is_verified=True,
            is_active=True,
        )
        session.add(user)
        await session.commit()
        await session.refresh(user)
        return user

    async def _create_project(self, session: AsyncSession, user_id: int, name: str):
        project = self.Project(name=name, user_id=user_id)
        session.add(project)
        await session.commit()
        await session.refresh(project)
        return project

    async def _create_task(self, session: AsyncSession, project_id: int, title: str):
        task = self.Task(title=title, project_id=project_id)
        session.add(task)
        await session.commit()
        await session.refresh(task)
        return task

    def _auth_header_for(self, email: str):
        from backend.app.utils.auth import create_access_token

        token = create_access_token({"sub": email})
        return {"Authorization": f"Bearer {token}"}

    def test_list_projects_empty_for_new_user(self):
        async def setup():
            async with db.SessionLocal() as session:
                return await self._create_user(session, "user@example.com", "secret123")

        user = asyncio.run(setup())
        response = self.client.get(
            "/api/projects",
            headers=self._auth_header_for(user.email),
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["data"], [])

    def test_create_project_returns_project(self):
        async def setup():
            async with db.SessionLocal() as session:
                return await self._create_user(session, "user@example.com", "secret123")

        user = asyncio.run(setup())
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
        async def setup():
            async with db.SessionLocal() as session:
                user = await self._create_user(session, "owner@example.com", "secret123")
                project = await self._create_project(session, user.id, "Owner Project")
                return user, project

        user, project = asyncio.run(setup())

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
        async def setup():
            async with db.SessionLocal() as session:
                user_a = await self._create_user(session, "a@example.com", "secret123")
                user_b = await self._create_user(session, "b@example.com", "secret123")
                session.add(self.Project(name="A project", user_id=user_a.id))
                session.add(self.Project(name="B project", user_id=user_b.id))
                await session.commit()
                return user_a

        user_a = asyncio.run(setup())

        response = self.client.get(
            "/api/projects",
            headers=self._auth_header_for(user_a.email),
        )

        self.assertEqual(response.status_code, 200)
        data = response.json()["data"]
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["name"], "A project")

    def test_create_project_empty_name_returns_422(self):
        async def setup():
            async with db.SessionLocal() as session:
                return await self._create_user(session, "user@example.com", "secret123")

        user = asyncio.run(setup())
        response = self.client.post(
            "/api/projects",
            json={"name": ""},
            headers=self._auth_header_for(user.email),
        )

        self.assertEqual(response.status_code, 422)

    def test_get_project_returns_404_for_missing_project(self):
        async def setup():
            async with db.SessionLocal() as session:
                return await self._create_user(session, "user@example.com", "secret123")

        user = asyncio.run(setup())
        response = self.client.get(
            "/api/projects/9999",
            headers=self._auth_header_for(user.email),
        )

        self.assertEqual(response.status_code, 404)

    def test_get_project_returns_403_for_non_owner(self):
        async def setup():
            async with db.SessionLocal() as session:
                owner = await self._create_user(session, "owner@example.com", "secret123")
                other = await self._create_user(session, "other@example.com", "secret123")
                project = await self._create_project(session, owner.id, "Owner Project")
                return other, project

        other, project = asyncio.run(setup())

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
        async def setup():
            async with db.SessionLocal() as session:
                user = await self._create_user(session, "user@example.com", "secret123")
                project = await self._create_project(session, user.id, "Original Name")
                return user, project

        user, project = asyncio.run(setup())

        response = self.client.put(
            f"/api/projects/{project.id}",
            json={"name": "Updated Name"},
            headers=self._auth_header_for(user.email),
        )

        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertEqual(body["data"]["id"], project.id)
        self.assertEqual(body["data"]["name"], "Updated Name")
        self.assertEqual(body["data"]["user_id"], user.id)

    def test_update_project_empty_name_returns_422(self):
        async def setup():
            async with db.SessionLocal() as session:
                user = await self._create_user(session, "user@example.com", "secret123")
                project = await self._create_project(session, user.id, "Original Name")
                return user, project

        user, project = asyncio.run(setup())

        response = self.client.put(
            f"/api/projects/{project.id}",
            json={"name": ""},
            headers=self._auth_header_for(user.email),
        )

        self.assertEqual(response.status_code, 422)

    def test_update_project_whitespace_name_returns_422(self):
        async def setup():
            async with db.SessionLocal() as session:
                user = await self._create_user(session, "user@example.com", "secret123")
                project = await self._create_project(session, user.id, "Original Name")
                return user, project

        user, project = asyncio.run(setup())

        response = self.client.put(
            f"/api/projects/{project.id}",
            json={"name": "   "},
            headers=self._auth_header_for(user.email),
        )

        self.assertEqual(response.status_code, 422)

    def test_update_project_returns_404_for_missing_project(self):
        async def setup():
            async with db.SessionLocal() as session:
                return await self._create_user(session, "user@example.com", "secret123")

        user = asyncio.run(setup())
        response = self.client.put(
            "/api/projects/9999",
            json={"name": "Updated Name"},
            headers=self._auth_header_for(user.email),
        )

        self.assertEqual(response.status_code, 404)

    def test_update_project_returns_403_for_non_owner(self):
        async def setup():
            async with db.SessionLocal() as session:
                owner = await self._create_user(session, "owner@example.com", "secret123")
                other = await self._create_user(session, "other@example.com", "secret123")
                project = await self._create_project(session, owner.id, "Owner Project")
                return other, project

        other, project = asyncio.run(setup())

        response = self.client.put(
            f"/api/projects/{project.id}",
            json={"name": "Hacked Name"},
            headers=self._auth_header_for(other.email),
        )

        self.assertEqual(response.status_code, 403)

    def test_update_project_trims_whitespace(self):
        async def setup():
            async with db.SessionLocal() as session:
                user = await self._create_user(session, "user@example.com", "secret123")
                project = await self._create_project(session, user.id, "Original Name")
                return user, project

        user, project = asyncio.run(setup())

        response = self.client.put(
            f"/api/projects/{project.id}",
            json={"name": "  Trimmed Name  "},
            headers=self._auth_header_for(user.email),
        )

        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertEqual(body["data"]["name"], "Trimmed Name")

    # Tech Debt Fix: Project name max length constraint
    def test_create_project_name_too_long_returns_422(self):
        async def setup():
            async with db.SessionLocal() as session:
                return await self._create_user(session, "user@example.com", "secret123")

        user = asyncio.run(setup())
        long_name = "x" * 101  # exceeds 100 char limit
        response = self.client.post(
            "/api/projects",
            json={"name": long_name},
            headers=self._auth_header_for(user.email),
        )

        self.assertEqual(response.status_code, 422)

    def test_update_project_name_too_long_returns_422(self):
        async def setup():
            async with db.SessionLocal() as session:
                user = await self._create_user(session, "user@example.com", "secret123")
                project = await self._create_project(session, user.id, "Original Name")
                return user, project

        user, project = asyncio.run(setup())

        long_name = "x" * 101  # exceeds 100 char limit
        response = self.client.put(
            f"/api/projects/{project.id}",
            json={"name": long_name},
            headers=self._auth_header_for(user.email),
        )

        self.assertEqual(response.status_code, 422)

    # Story 2.4: Delete Project tests
    def test_delete_project_removes_project_for_owner(self):
        async def setup():
            async with db.SessionLocal() as session:
                user = await self._create_user(session, "user@example.com", "secret123")
                project = await self._create_project(session, user.id, "Delete Me")
                return user, project

        user, project = asyncio.run(setup())

        response = self.client.delete(
            f"/api/projects/{project.id}",
            headers=self._auth_header_for(user.email),
        )

        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertEqual(body["data"]["id"], project.id)
        self.assertEqual(body["data"]["name"], "Delete Me")
        self.assertEqual(body["data"]["user_id"], user.id)
        self.assertIn("created_at", body["data"])
        self.assertIn("updated_at", body["data"])

        async def fetch_remaining():
            async with db.SessionLocal() as session:
                return await session.scalar(
                    select(self.Project).where(self.Project.id == project.id)
                )

        remaining = asyncio.run(fetch_remaining())
        self.assertIsNone(remaining)

    def test_delete_project_returns_404_for_missing_project(self):
        async def setup():
            async with db.SessionLocal() as session:
                return await self._create_user(session, "user@example.com", "secret123")

        user = asyncio.run(setup())
        response = self.client.delete(
            "/api/projects/9999",
            headers=self._auth_header_for(user.email),
        )

        self.assertEqual(response.status_code, 404)

    def test_delete_project_returns_404_when_already_deleted_ac8(self):
        async def setup():
            async with db.SessionLocal() as session:
                user = await self._create_user(session, "user@example.com", "secret123")
                project = await self._create_project(session, user.id, "Delete Twice")
                return user, project

        user, project = asyncio.run(setup())

        response = self.client.delete(
            f"/api/projects/{project.id}",
            headers=self._auth_header_for(user.email),
        )
        self.assertEqual(response.status_code, 200)

        response = self.client.delete(
            f"/api/projects/{project.id}",
            headers=self._auth_header_for(user.email),
        )
        self.assertEqual(response.status_code, 404)

    def test_delete_project_returns_403_for_non_owner(self):
        async def setup():
            async with db.SessionLocal() as session:
                owner = await self._create_user(session, "owner@example.com", "secret123")
                other = await self._create_user(session, "other@example.com", "secret123")
                project = await self._create_project(session, owner.id, "Owner Project")
                return other, project

        other, project = asyncio.run(setup())

        response = self.client.delete(
            f"/api/projects/{project.id}",
            headers=self._auth_header_for(other.email),
        )

        self.assertEqual(response.status_code, 403)

    def test_delete_project_returns_401_for_unauthenticated_request(self):
        response = self.client.delete("/api/projects/1")
        self.assertEqual(response.status_code, 401)

    def test_delete_project_cascades_to_tasks(self):
        """Verify that deleting a project also deletes its associated tasks."""
        async def setup():
            async with db.SessionLocal() as session:
                user = await self._create_user(session, "user@example.com", "secret123")
                project = await self._create_project(session, user.id, "Project with Tasks")
                task1 = await self._create_task(session, project.id, "Task 1")
                task2 = await self._create_task(session, project.id, "Task 2")
                return user, project, task1.id, task2.id

        user, project, task1_id, task2_id = asyncio.run(setup())

        # Verify tasks exist before delete
        async def fetch_tasks_before():
            async with db.SessionLocal() as session:
                t1 = await session.scalar(select(self.Task).where(self.Task.id == task1_id))
                t2 = await session.scalar(select(self.Task).where(self.Task.id == task2_id))
                return t1, t2

        t1_before, t2_before = asyncio.run(fetch_tasks_before())
        self.assertIsNotNone(t1_before)
        self.assertIsNotNone(t2_before)

        # Delete the project
        response = self.client.delete(
            f"/api/projects/{project.id}",
            headers=self._auth_header_for(user.email),
        )
        self.assertEqual(response.status_code, 200)

        # Verify tasks are also deleted (cascade)
        async def fetch_tasks_after():
            async with db.SessionLocal() as session:
                t1 = await session.scalar(select(self.Task).where(self.Task.id == task1_id))
                t2 = await session.scalar(select(self.Task).where(self.Task.id == task2_id))
                return t1, t2

        t1_after, t2_after = asyncio.run(fetch_tasks_after())
        self.assertIsNone(t1_after, "Task 1 should be deleted when project is deleted")
        self.assertIsNone(t2_after, "Task 2 should be deleted when project is deleted")


if __name__ == "__main__":
    unittest.main()
