import unittest

from pydantic import ValidationError

from backend.app.schemas.task import TaskCreate


class TaskSchemaTests(unittest.TestCase):
    def test_task_create_requires_title(self):
        with self.assertRaises(ValidationError):
            TaskCreate(title="")

    def test_task_create_rejects_whitespace_only_title(self):
        with self.assertRaises(ValidationError):
            TaskCreate(title="   ")

    def test_task_create_rejects_too_long_title(self):
        with self.assertRaises(ValidationError):
            TaskCreate(title="x" * 201)

    def test_task_create_trims_title_before_length_check(self):
        task = TaskCreate(title="  Trimmed  ")
        self.assertEqual(task.title, "Trimmed")

    def test_task_create_rejects_non_string_title(self):
        with self.assertRaises(ValidationError):
            TaskCreate(title=123)


if __name__ == "__main__":
    unittest.main()
