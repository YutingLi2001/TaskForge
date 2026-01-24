import unittest

from pydantic import ValidationError

from backend.app.schemas.task import TaskCreate, TaskStatusUpdate, TaskUpdate


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

    def test_task_update_requires_title(self):
        with self.assertRaises(ValidationError):
            TaskUpdate(title="")

    def test_task_update_rejects_whitespace_only_title(self):
        with self.assertRaises(ValidationError):
            TaskUpdate(title="   ")

    def test_task_update_rejects_too_long_title(self):
        with self.assertRaises(ValidationError):
            TaskUpdate(title="x" * 201)

    def test_task_update_trims_title_before_length_check(self):
        task = TaskUpdate(title="  Trimmed  ")
        self.assertEqual(task.title, "Trimmed")

    def test_task_update_rejects_non_string_title(self):
        with self.assertRaises(ValidationError):
            TaskUpdate(title=123)

    def test_task_status_update_requires_is_complete(self):
        with self.assertRaises(ValidationError):
            TaskStatusUpdate()

    def test_task_status_update_accepts_boolean(self):
        payload = TaskStatusUpdate(is_complete=True)
        self.assertTrue(payload.is_complete)


if __name__ == "__main__":
    unittest.main()
