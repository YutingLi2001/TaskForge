import unittest


class ProjectsRouterTests(unittest.TestCase):
    def test_projects_router_has_routes(self):
        from backend.app.routers.projects import router

        paths = {route.path for route in router.routes}
        self.assertIn("/projects", paths)


if __name__ == "__main__":
    unittest.main()
