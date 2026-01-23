import unittest

from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from backend.app.database import Base
from backend.app.models.project import Project
from backend.app.models.task import Task


class TaskModelTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.engine = create_engine(
            "sqlite+pysqlite:///:memory:",
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
        )
        cls.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=cls.engine)

    @classmethod
    def tearDownClass(cls):
        cls.engine.dispose()

    def setUp(self):
        Base.metadata.drop_all(bind=self.engine)
        Base.metadata.create_all(bind=self.engine)
        self.db = self.SessionLocal()

    def tearDown(self):
        self.db.close()

    def test_task_table_exists(self):
        inspector = inspect(self.engine)
        self.assertIn("tasks", inspector.get_table_names())

    def test_task_columns_exist(self):
        inspector = inspect(self.engine)
        columns = {col["name"] for col in inspector.get_columns("tasks")}
        self.assertIn("id", columns)
        self.assertIn("title", columns)
        self.assertIn("is_complete", columns)
        self.assertIn("project_id", columns)
        self.assertIn("created_at", columns)
        self.assertIn("updated_at", columns)

    def test_task_relationships_exist(self):
        self.assertTrue(hasattr(Task, "project"))
        self.assertTrue(hasattr(Project, "tasks"))


if __name__ == "__main__":
    unittest.main()
