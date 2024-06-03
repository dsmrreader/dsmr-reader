from django.contrib.auth.models import User
from django.test import TestCase, Client
from django.urls.base import reverse
from django.conf import settings

from dsmr_backend.models.schedule import ScheduledProcess
from dsmr_pvoutput.models.settings import PVOutputAddStatusSettings


class TestAdmin(TestCase):
    def setUp(self):
        username = "testuser"
        password = "passwd"
        User.objects.create_superuser(username, "unknown@localhost", password)

        self.client = Client()
        self.client.login(username=username, password=password)

    def test_pvoutput_settings_hook(self):
        API_URL = reverse("admin:dsmr_pvoutput_pvoutputapisettings_changelist")
        STATUS_URL = reverse("admin:dsmr_pvoutput_pvoutputaddstatussettings_changelist")

        self.assertFalse(
            ScheduledProcess.objects.filter(
                module=settings.DSMRREADER_MODULE_PVOUTPUT_EXPORT, active=True
            ).exists()
        )

        response = self.client.post(
            API_URL,
            dict(
                auth_token="test",
                system_identifier="12345",
            ),
        )
        self.assertEqual(response.status_code, 302)
        # Unchanged
        self.assertFalse(
            ScheduledProcess.objects.filter(
                module=settings.DSMRREADER_MODULE_PVOUTPUT_EXPORT, active=True
            ).exists()
        )

        # Pt. II
        response = self.client.post(
            STATUS_URL,
            dict(
                export=True,
                upload_interval=PVOutputAddStatusSettings.INTERVAL_5_MINUTES,
                upload_delay=0,
            ),
        )
        self.assertEqual(response.status_code, 302)
        # Affected
        self.assertTrue(
            ScheduledProcess.objects.filter(
                module=settings.DSMRREADER_MODULE_PVOUTPUT_EXPORT, active=True
            ).exists()
        )
