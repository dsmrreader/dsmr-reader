from django.test import TestCase, Client
from django.urls import reverse


class TestViews(TestCase):
    def test_docs(self):
        response = Client().get(reverse("frontend:redoc-api-docs"))
        self.assertEqual(response.status_code, 200, response.content)

    def test_openapi_schema(self):
        response = Client().get(reverse("v2-api-openapi-schema"), data=dict(format="json"))
        self.assertEqual(response.status_code, 200, response.content)

    def test_docs_redoc_script_is_pinned(self):
        response = Client().get(reverse("frontend:redoc-api-docs"))
        self.assertContains(response, "https://cdn.redoc.ly/redoc/v2.5.1/bundles/redoc.standalone.js")
        self.assertNotContains(response, "redoc/latest")
