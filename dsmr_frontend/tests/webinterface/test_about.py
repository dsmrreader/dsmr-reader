from unittest import mock

from django.test import TestCase, Client
from django.urls import reverse


class TestAbout(TestCase):
    def setUp(self):
        self.client = Client()

    def test_okay(self):
        response = self.client.get(reverse("frontend:about"))
        self.assertEqual(response.status_code, 200, response.content)
        self.assertIn("monitoring_issues", response.context)


class TestAboutXhrUpdateCheck(TestCase):
    def setUp(self):
        self.client = Client()

    @mock.patch("dsmr_backend.services.backend.is_latest_version")
    def test_okay(self, is_latest_version_mock):
        is_latest_version_mock.return_value = True

        response = self.client.get(reverse("frontend:about-xhr-update-check"))
        self.assertEqual(response.status_code, 200, response.content)
