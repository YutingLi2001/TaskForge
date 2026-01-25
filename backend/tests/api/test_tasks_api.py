import asyncio
import os
import unittest
from datetime import datetime, timedelta, timezone

from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool, StaticPool

db = None
get_db = None


class TasksApiTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        os.environ.setdefault("DATABASE_URL", "sqlite+aiosqlite:///:memory:")
        database_url = os.environ["DATABASE_URL"]

        global db, get_db
        from backend.app import database as db
        from backend.app.database import get_db

        if database_url.startswith("sqlite"):
            cls.engine = create_async_engine(
                database_url,
                connect_args={"check_same_thread": False},
                poolclass=StaticPool,
            )
        else:
            cls.engine = create_async_engine(database_url, poolclass=NullPool)
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

        cls.Project = Project
        cls.Task = Task
        cls.User = User
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

    async def _create_project(self, session: AsyncSession, owner_id: int, name: str = "Project"):
        project = self.Project(name=name, user_id=owner_id)
        session.add(project)
        await session.commit()
        await session.refresh(project)
        return project

    async def _create_task(
        self, session: AsyncSession, project_id: int, title: str = "Task"
    ):
        task = self.Task(title=title, project_id=project_id)
        session.add(task)
        await session.commit()
        await session.refresh(task)
        return task

    def _auth_header_for(self, email: str):
        from backend.app.utils.auth import create_access_token

        token = create_access_token({"sub": email})
        return {"Authorization": f"Bearer {token}"}

    def test_list_tasks_returns_empty_for_project_with_no_tasks(self):
        async def setup():
            async with db.SessionLocal() as session:
                user = await self._create_user(session, "user@example.com", "secret123")
                project = await self._create_project(session, user.id, name="Empty Project")
                return user, project

        user, project = asyncio.run(setup())

        response = self.client.get(
            f"/api/projects/{project.id}/tasks",
            headers=self._auth_header_for(user.email),
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["data"], [])

    def test_create_task_defaults_is_complete_false(self):
        async def setup():
            async with db.SessionLocal() as session:
                user = await self._create_user(session, "user@example.com", "secret123")
                project = await self._create_project(session, user.id, name="Tasks Project")
                return user, project

        user, project = asyncio.run(setup())

        response = self.client.post(
            f"/api/projects/{project.id}/tasks",
            json={"title": "First Task"},
            headers=self._auth_header_for(user.email),
        )

        self.assertEqual(response.status_code, 201)
        body = response.json()["data"]
        self.assertEqual(body["title"], "First Task")
        self.assertEqual(body["is_complete"], False)
        self.assertEqual(body["project_id"], project.id)

    def test_list_tasks_returns_tasks_for_project(self):
        async def setup():
            async with db.SessionLocal() as session:
                user = await self._create_user(session, "user@example.com", "secret123")
                project = await self._create_project(session, user.id, name="Tasks Project")
                session.add(self.Task(title="Task A", project_id=project.id))
                session.add(self.Task(title="Task B", project_id=project.id))
                await session.commit()
                return user, project

        user, project = asyncio.run(setup())

        response = self.client.get(
            f"/api/projects/{project.id}/tasks",
            headers=self._auth_header_for(user.email),
        )

        self.assertEqual(response.status_code, 200)
        data = response.json()["data"]
        self.assertEqual(len(data), 2)
        titles = {task["title"] for task in data}
        self.assertEqual(titles, {"Task A", "Task B"})

    def test_list_tasks_returns_ordered_by_created_at(self):
        async def setup():
            async with db.SessionLocal() as session:
                user = await self._create_user(session, "user@example.com", "secret123")
                project = await self._create_project(session, user.id, name="Tasks Project")
                earlier = datetime.now(timezone.utc) - timedelta(days=1)
                later = datetime.now(timezone.utc)
                session.add(
                    self.Task(
                        title="Later Task",
                        project_id=project.id,
                        created_at=later,
                        updated_at=later,
                    )
                )
                session.add(
                    self.Task(
                        title="Earlier Task",
                        project_id=project.id,
                        created_at=earlier,
                        updated_at=earlier,
                    )
                )
                await session.commit()
                return user, project

        user, project = asyncio.run(setup())

        response = self.client.get(
            f"/api/projects/{project.id}/tasks",
            headers=self._auth_header_for(user.email),
        )

        self.assertEqual(response.status_code, 200)
        data = response.json()["data"]
        self.assertEqual([task["title"] for task in data], ["Earlier Task", "Later Task"])

    def test_create_task_empty_title_returns_422(self):
        async def setup():
            async with db.SessionLocal() as session:
                user = await self._create_user(session, "user@example.com", "secret123")
                project = await self._create_project(session, user.id, name="Tasks Project")
                return user, project

        user, project = asyncio.run(setup())

        response = self.client.post(
            f"/api/projects/{project.id}/tasks",
            json={"title": ""},
            headers=self._auth_header_for(user.email),
        )

        self.assertEqual(response.status_code, 422)

    def test_create_task_whitespace_title_returns_422(self):
        async def setup():
            async with db.SessionLocal() as session:
                user = await self._create_user(session, "user@example.com", "secret123")
                project = await self._create_project(session, user.id, name="Tasks Project")
                return user, project

        user, project = asyncio.run(setup())

        response = self.client.post(
            f"/api/projects/{project.id}/tasks",
            json={"title": "   "},
            headers=self._auth_header_for(user.email),
        )

        self.assertEqual(response.status_code, 422)

    def test_create_task_trims_title(self):
        async def setup():
            async with db.SessionLocal() as session:
                user = await self._create_user(session, "user@example.com", "secret123")
                project = await self._create_project(session, user.id, name="Tasks Project")
                return user, project

        user, project = asyncio.run(setup())

        response = self.client.post(
            f"/api/projects/{project.id}/tasks",
            json={"title": "  Trim Me  "},
            headers=self._auth_header_for(user.email),
        )

        self.assertEqual(response.status_code, 201)
        body = response.json()["data"]
        self.assertEqual(body["title"], "Trim Me")

    def test_create_task_title_too_long_returns_422(self):
        async def setup():
            async with db.SessionLocal() as session:
                user = await self._create_user(session, "user@example.com", "secret123")
                project = await self._create_project(session, user.id, name="Tasks Project")
                return user, project

        user, project = asyncio.run(setup())

        long_title = "x" * 201
        response = self.client.post(
            f"/api/projects/{project.id}/tasks",
            json={"title": long_title},
            headers=self._auth_header_for(user.email),
        )

        self.assertEqual(response.status_code, 422)

    def test_tasks_return_404_for_missing_project(self):
        async def setup():
            async with db.SessionLocal() as session:
                user = await self._create_user(session, "user@example.com", "secret123")
                return user

        user = asyncio.run(setup())

        response = self.client.get(
            "/api/projects/9999/tasks",
            headers=self._auth_header_for(user.email),
        )
        self.assertEqual(response.status_code, 404)

        response = self.client.post(
            "/api/projects/9999/tasks",
            json={"title": "Missing"},
            headers=self._auth_header_for(user.email),
        )
        self.assertEqual(response.status_code, 404)

    def test_tasks_return_403_for_non_owner(self):
        async def setup():
            async with db.SessionLocal() as session:
                owner = await self._create_user(session, "owner@example.com", "secret123")
                other = await self._create_user(session, "other@example.com", "secret123")
                project = await self._create_project(session, owner.id, name="Owner Project")
                return owner, other, project

        owner, other, project = asyncio.run(setup())

        response = self.client.get(
            f"/api/projects/{project.id}/tasks",
            headers=self._auth_header_for(other.email),
        )
        self.assertEqual(response.status_code, 403)

        response = self.client.post(
            f"/api/projects/{project.id}/tasks",
            json={"title": "Hack"},
            headers=self._auth_header_for(other.email),
        )
        self.assertEqual(response.status_code, 403)

    def test_tasks_return_401_for_unauthenticated(self):
        response = self.client.get("/api/projects/1/tasks")
        self.assertEqual(response.status_code, 401)

        response = self.client.post(
            "/api/projects/1/tasks",
            json={"title": "No Auth"},
        )
        self.assertEqual(response.status_code, 401)

    def test_update_task_updates_title_and_trims(self):
        async def setup():
            async with db.SessionLocal() as session:
                user = await self._create_user(session, "user@example.com", "secret123")
                project = await self._create_project(session, user.id, name="Tasks Project")
                task = await self._create_task(session, project.id, title="Original")
                return user, project, task

        user, project, task = asyncio.run(setup())

        response = self.client.put(
            f"/api/projects/{project.id}/tasks/{task.id}",
            json={"title": "  Updated  "},
            headers=self._auth_header_for(user.email),
        )

        self.assertEqual(response.status_code, 200)
        body = response.json()["data"]
        self.assertEqual(body["title"], "Updated")
        self.assertEqual(body["project_id"], project.id)

    def test_update_task_empty_title_returns_422(self):
        async def setup():
            async with db.SessionLocal() as session:
                user = await self._create_user(session, "user@example.com", "secret123")
                project = await self._create_project(session, user.id, name="Tasks Project")
                task = await self._create_task(session, project.id, title="Original")
                return user, project, task

        user, project, task = asyncio.run(setup())

        response = self.client.put(
            f"/api/projects/{project.id}/tasks/{task.id}",
            json={"title": ""},
            headers=self._auth_header_for(user.email),
        )

        self.assertEqual(response.status_code, 422)

    def test_update_task_whitespace_title_returns_422(self):
        async def setup():
            async with db.SessionLocal() as session:
                user = await self._create_user(session, "user@example.com", "secret123")
                project = await self._create_project(session, user.id, name="Tasks Project")
                task = await self._create_task(session, project.id, title="Original")
                return user, project, task

        user, project, task = asyncio.run(setup())

        response = self.client.put(
            f"/api/projects/{project.id}/tasks/{task.id}",
            json={"title": "   "},
            headers=self._auth_header_for(user.email),
        )

        self.assertEqual(response.status_code, 422)

    def test_update_task_returns_404_for_missing_task(self):
        async def setup():
            async with db.SessionLocal() as session:
                user = await self._create_user(session, "user@example.com", "secret123")
                project = await self._create_project(session, user.id, name="Tasks Project")
                return user, project

        user, project = asyncio.run(setup())

        response = self.client.put(
            f"/api/projects/{project.id}/tasks/9999",
            json={"title": "Update"},
            headers=self._auth_header_for(user.email),
        )

        self.assertEqual(response.status_code, 404)

    def test_update_task_returns_404_when_task_not_in_project(self):
        async def setup():
            async with db.SessionLocal() as session:
                user = await self._create_user(session, "user@example.com", "secret123")
                project = await self._create_project(session, user.id, name="Project A")
                other_project = await self._create_project(session, user.id, name="Project B")
                task = await self._create_task(session, other_project.id, title="Other task")
                return user, project, task

        user, project, task = asyncio.run(setup())

        response = self.client.put(
            f"/api/projects/{project.id}/tasks/{task.id}",
            json={"title": "Update"},
            headers=self._auth_header_for(user.email),
        )

        self.assertEqual(response.status_code, 404)

    def test_update_task_returns_404_for_missing_project(self):
        async def setup():
            async with db.SessionLocal() as session:
                user = await self._create_user(session, "user@example.com", "secret123")
                return user

        user = asyncio.run(setup())

        response = self.client.put(
            "/api/projects/9999/tasks/1",
            json={"title": "Update"},
            headers=self._auth_header_for(user.email),
        )

        self.assertEqual(response.status_code, 404)

    def test_update_task_returns_403_for_non_owner(self):
        async def setup():
            async with db.SessionLocal() as session:
                owner = await self._create_user(session, "owner@example.com", "secret123")
                other = await self._create_user(session, "other@example.com", "secret123")
                project = await self._create_project(session, owner.id, name="Owner Project")
                task = await self._create_task(session, project.id, title="Original")
                return owner, other, project, task

        owner, other, project, task = asyncio.run(setup())

        response = self.client.put(
            f"/api/projects/{project.id}/tasks/{task.id}",
            json={"title": "Update"},
            headers=self._auth_header_for(other.email),
        )

        self.assertEqual(response.status_code, 403)

    def test_update_task_returns_401_for_unauthenticated(self):
        response = self.client.put(
            "/api/projects/1/tasks/1",
            json={"title": "No Auth"},
        )

        self.assertEqual(response.status_code, 401)

    def test_toggle_task_status_from_incomplete_to_complete(self):
        async def setup():
            async with db.SessionLocal() as session:
                user = await self._create_user(session, "user@example.com", "secret123")
                project = await self._create_project(session, user.id, name="Tasks Project")
                task = await self._create_task(session, project.id, title="Task")
                return user, project, task

        user, project, task = asyncio.run(setup())

        response = self.client.patch(
            f"/api/projects/{project.id}/tasks/{task.id}",
            json={"is_complete": True},
            headers=self._auth_header_for(user.email),
        )

        self.assertEqual(response.status_code, 200)
        body = response.json()["data"]
        self.assertEqual(body["id"], task.id)
        self.assertEqual(body["is_complete"], True)

    def test_toggle_task_status_from_complete_to_incomplete(self):
        async def setup():
            async with db.SessionLocal() as session:
                user = await self._create_user(session, "user@example.com", "secret123")
                project = await self._create_project(session, user.id, name="Tasks Project")
                task = await self._create_task(session, project.id, title="Task")
                task.is_complete = True
                await session.commit()
                await session.refresh(task)
                return user, project, task

        user, project, task = asyncio.run(setup())

        response = self.client.patch(
            f"/api/projects/{project.id}/tasks/{task.id}",
            json={"is_complete": False},
            headers=self._auth_header_for(user.email),
        )

        self.assertEqual(response.status_code, 200)
        body = response.json()["data"]
        self.assertEqual(body["id"], task.id)
        self.assertEqual(body["is_complete"], False)

    def test_toggle_task_returns_404_for_missing_task(self):
        async def setup():
            async with db.SessionLocal() as session:
                user = await self._create_user(session, "user@example.com", "secret123")
                project = await self._create_project(session, user.id, name="Tasks Project")
                return user, project

        user, project = asyncio.run(setup())

        response = self.client.patch(
            f"/api/projects/{project.id}/tasks/9999",
            json={"is_complete": True},
            headers=self._auth_header_for(user.email),
        )

        self.assertEqual(response.status_code, 404)

    def test_toggle_task_returns_404_for_missing_project(self):
        async def setup():
            async with db.SessionLocal() as session:
                user = await self._create_user(session, "user@example.com", "secret123")
                return user

        user = asyncio.run(setup())

        response = self.client.patch(
            "/api/projects/9999/tasks/1",
            json={"is_complete": True},
            headers=self._auth_header_for(user.email),
        )

        self.assertEqual(response.status_code, 404)

    def test_toggle_task_returns_403_for_non_owner(self):
        async def setup():
            async with db.SessionLocal() as session:
                owner = await self._create_user(session, "owner@example.com", "secret123")
                other = await self._create_user(session, "other@example.com", "secret123")
                project = await self._create_project(session, owner.id, name="Owner Project")
                task = await self._create_task(session, project.id, title="Task")
                return owner, other, project, task

        owner, other, project, task = asyncio.run(setup())

        response = self.client.patch(
            f"/api/projects/{project.id}/tasks/{task.id}",
            json={"is_complete": True},
            headers=self._auth_header_for(other.email),
        )

        self.assertEqual(response.status_code, 403)

    def test_toggle_task_returns_401_for_unauthenticated(self):
        response = self.client.patch(
            "/api/projects/1/tasks/1",
            json={"is_complete": True},
        )

        self.assertEqual(response.status_code, 401)

    def test_toggle_task_returns_404_when_task_not_in_project(self):
        async def setup():
            async with db.SessionLocal() as session:
                user = await self._create_user(session, "user@example.com", "secret123")
                project = await self._create_project(session, user.id, name="Project A")
                other_project = await self._create_project(session, user.id, name="Project B")
                task = await self._create_task(session, other_project.id, title="Task")
                return user, project, task

        user, project, task = asyncio.run(setup())

        response = self.client.patch(
            f"/api/projects/{project.id}/tasks/{task.id}",
            json={"is_complete": True},
            headers=self._auth_header_for(user.email),
        )

        self.assertEqual(response.status_code, 404)

    def test_delete_task_returns_200_and_removes_task(self):
        async def setup():
            async with db.SessionLocal() as session:
                user = await self._create_user(session, "user@example.com", "secret123")
                project = await self._create_project(session, user.id, name="Tasks Project")
                task = await self._create_task(session, project.id, title="Delete Me")
                return user, project, task

        user, project, task = asyncio.run(setup())

        response = self.client.delete(
            f"/api/projects/{project.id}/tasks/{task.id}",
            headers=self._auth_header_for(user.email),
        )

        self.assertEqual(response.status_code, 200)
        body = response.json()["data"]
        self.assertEqual(body["id"], task.id)

        response = self.client.get(
            f"/api/projects/{project.id}/tasks",
            headers=self._auth_header_for(user.email),
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["data"], [])

    def test_delete_task_returns_404_for_nonexistent_task(self):
        async def setup():
            async with db.SessionLocal() as session:
                user = await self._create_user(session, "user@example.com", "secret123")
                project = await self._create_project(session, user.id, name="Tasks Project")
                return user, project

        user, project = asyncio.run(setup())

        response = self.client.delete(
            f"/api/projects/{project.id}/tasks/9999",
            headers=self._auth_header_for(user.email),
        )

        self.assertEqual(response.status_code, 404)

    def test_delete_task_returns_404_for_nonexistent_project(self):
        async def setup():
            async with db.SessionLocal() as session:
                user = await self._create_user(session, "user@example.com", "secret123")
                return user

        user = asyncio.run(setup())

        response = self.client.delete(
            "/api/projects/9999/tasks/1",
            headers=self._auth_header_for(user.email),
        )

        self.assertEqual(response.status_code, 404)

    def test_delete_task_returns_403_for_non_owner(self):
        async def setup():
            async with db.SessionLocal() as session:
                owner = await self._create_user(session, "owner@example.com", "secret123")
                other = await self._create_user(session, "other@example.com", "secret123")
                project = await self._create_project(session, owner.id, name="Owner Project")
                task = await self._create_task(session, project.id, title="Task")
                return owner, other, project, task

        owner, other, project, task = asyncio.run(setup())

        response = self.client.delete(
            f"/api/projects/{project.id}/tasks/{task.id}",
            headers=self._auth_header_for(other.email),
        )

        self.assertEqual(response.status_code, 403)

    def test_delete_task_returns_401_for_unauthenticated(self):
        response = self.client.delete("/api/projects/1/tasks/1")

        self.assertEqual(response.status_code, 401)

    def test_delete_task_returns_404_when_task_not_in_project(self):
        async def setup():
            async with db.SessionLocal() as session:
                user = await self._create_user(session, "user@example.com", "secret123")
                project = await self._create_project(session, user.id, name="Project A")
                other_project = await self._create_project(session, user.id, name="Project B")
                task = await self._create_task(session, other_project.id, title="Task")
                return user, project, task

        user, project, task = asyncio.run(setup())

        response = self.client.delete(
            f"/api/projects/{project.id}/tasks/{task.id}",
            headers=self._auth_header_for(user.email),
        )

        self.assertEqual(response.status_code, 404)

    def test_delete_task_returns_404_on_second_delete(self):
        async def setup():
            async with db.SessionLocal() as session:
                user = await self._create_user(session, "user@example.com", "secret123")
                project = await self._create_project(session, user.id, name="Tasks Project")
                task = await self._create_task(session, project.id, title="Delete Me")
                return user, project, task

        user, project, task = asyncio.run(setup())

        response = self.client.delete(
            f"/api/projects/{project.id}/tasks/{task.id}",
            headers=self._auth_header_for(user.email),
        )
        self.assertEqual(response.status_code, 200)

        response = self.client.delete(
            f"/api/projects/{project.id}/tasks/{task.id}",
            headers=self._auth_header_for(user.email),
        )
        self.assertEqual(response.status_code, 404)


if __name__ == "__main__":
    unittest.main()
