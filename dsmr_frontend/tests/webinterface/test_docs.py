from django.test import TestCase, Client
from django.urls import reverse


class TestViews(TestCase):
    def test_docs(self):
        response = Client().get(
            reverse('frontend:redoc-api-docs')
        )
        self.assertEqual(response.status_code, 200, response.content)

    def test_openapi_schema(self):
        response = Client().get(
            reverse('v2-api-openapi-schema')
        )
        self.assertEqual(response.status_code, 200, response.content)
