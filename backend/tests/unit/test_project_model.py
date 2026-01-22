import unittest

from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from backend.app.database import Base
from backend.app.models.project import Project


class ProjectModelTests(unittest.TestCase):
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
