"""Regression checks for the API documentation contract."""

import unittest

from fastapi.testclient import TestClient

from app.main import app


class OpenApiDocumentationTests(unittest.TestCase):
    def test_openapi_and_interactive_documentation_are_available(self) -> None:
        client = TestClient(app)
        self.assertEqual(client.get("/openapi.json").status_code, 200)
        self.assertEqual(client.get("/docs").status_code, 200)
        self.assertEqual(client.get("/redoc").status_code, 200)

    def test_every_operation_has_unique_id_summary_and_description(self) -> None:
        schema = app.openapi()
        operations = [
            operation
            for path_item in schema["paths"].values()
            for method, operation in path_item.items()
            if method in {"get", "post", "put", "patch", "delete"}
        ]
        self.assertTrue(operations)
        self.assertTrue(all(operation.get("summary") for operation in operations))
        self.assertTrue(all(operation.get("description") for operation in operations))
        operation_ids = [operation["operationId"] for operation in operations]
        self.assertEqual(len(operation_ids), len(set(operation_ids)))

    def test_only_login_and_registration_are_public(self) -> None:
        schema = app.openapi()
        public_operations = {
            (method.upper(), path)
            for path, path_item in schema["paths"].items()
            for method, operation in path_item.items()
            if method in {"get", "post", "put", "patch", "delete"}
            and not operation.get("security")
        }
        self.assertEqual(
            public_operations,
            {("POST", "/login"), ("POST", "/cadastro")},
        )


if __name__ == "__main__":
    unittest.main()
