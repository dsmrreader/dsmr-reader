from django.test import TestCase, Client
from django.urls import reverse


class TestAbout(TestCase):
    def setUp(self):
        self.client = Client()

    def test_unauthenticated(self):
        response = self.client.get(reverse("frontend:about"))
        self.assertEqual(response.status_code, 200, response.content)
        self.assertIn("monitoring_issues", response.context)


class TestAboutXhrUpdateCheck(TestCase):
    def setUp(self):
        self.client = Client()

    def test_unauthenticated(self):
        response = self.client.get(reverse("frontend:about-xhr-update-check"))
        self.assertEqual(response.status_code, 200, response.content)
