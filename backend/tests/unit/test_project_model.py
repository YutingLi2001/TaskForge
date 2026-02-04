import os
import unittest

from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import sessionmaker

from backend.tests.utils.migrations import build_test_db_url, reset_database


class ProjectModelTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.database_url = build_test_db_url("project_model_unit", async_driver=False)
        os.environ["DATABASE_URL"] = cls.database_url
        cls.engine = create_engine(
            cls.database_url,
            connect_args={"check_same_thread": False},
        )
        cls.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=cls.engine)

    @classmethod
    def tearDownClass(cls):
        cls.engine.dispose()

    def setUp(self):
        reset_database(self.database_url)
        self.db = self.SessionLocal()

    def tearDown(self):
        self.db.close()

    def test_project_table_exists(self):
        inspector = inspect(self.engine)
        self.assertIn("projects", inspector.get_table_names())

    def test_project_columns_exist(self):
        inspector = inspect(self.engine)
        columns = {col["name"] for col in inspector.get_columns("projects")}
        self.assertIn("id", columns)
        self.assertIn("name", columns)
        self.assertIn("user_id", columns)
        self.assertIn("created_at", columns)
        self.assertIn("updated_at", columns)


if __name__ == "__main__":
    unittest.main()
