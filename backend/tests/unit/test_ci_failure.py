import unittest


class TestCIFailure(unittest.TestCase):
    def test_ci_failure_marker(self):
        self.fail("Intentional CI failure for pipeline validation")
