import unittest

from pydantic import ValidationError

from backend.app.schemas.project import ProjectCreate


class ProjectSchemaTests(unittest.TestCase):
    def test_project_create_requires_name(self):
        with self.assertRaises(ValidationError):
            ProjectCreate(name="")

    def test_project_create_rejects_whitespace_only_name(self):
        with self.assertRaises(ValidationError):
            ProjectCreate(name="   ")


if __name__ == "__main__":
    unittest.main()
