from django.contrib.auth.models import User
from django.test import TestCase, Client
from django.urls import reverse


class TestViews(TestCase):
    namespace = "frontend"

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user("testuser", "unknown@localhost", "passwd")

    def test_configuration(self):
        """Basically the same view (context vars) as the archive view."""
        view_url = reverse("{}:configuration".format(self.namespace))
        # Check login required.
        response = self.client.get(view_url)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response["Location"], "/admin/login/?next={}".format(view_url))

        # Login and retest
        self.client.login(username="testuser", password="passwd")
        response = self.client.get(view_url)
        self.assertEqual(response.status_code, 200, response.content)
        self.assertIn("api_settings", response.context)
        self.assertIn("backend_settings", response.context)
        self.assertIn("backup_settings", response.context)
        self.assertIn("consumption_settings", response.context)
        self.assertIn("datalogger_settings", response.context)
        self.assertIn("dropbox_settings", response.context)
        self.assertIn("email_settings", response.context)
        self.assertIn("frontend_settings", response.context)
        self.assertIn("mindergas_settings", response.context)
        self.assertIn("mqtt_broker_settings", response.context)
        self.assertIn("mqtt_jsondaytotals_settings", response.context)
        self.assertIn("mqtt_splittopicdaytotals_settings", response.context)
        self.assertIn("mqtt_splittopicmeterstatistics_settings", response.context)
        self.assertIn("mqtt_jsontelegram_settings", response.context)
        self.assertIn("mqtt_rawtelegram_settings", response.context)
        self.assertIn("mqtt_splittopictelegram_settings", response.context)
        self.assertIn("retention_settings", response.context)
        self.assertIn("weather_settings", response.context)
