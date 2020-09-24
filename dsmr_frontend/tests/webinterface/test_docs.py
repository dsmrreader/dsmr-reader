from django.test import TestCase, Client
from django.urls import reverse


class TestViews(TestCase):
    def test_docs(self):
        response = Client().get(
            reverse('frontend:redoc-api-docs')
        )
        self.assertEqual(response.status_code, 200, response.content)
