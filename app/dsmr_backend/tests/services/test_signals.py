from django.test import TestCase

from dsmr_backend.models.settings import BackendSettings
from dsmr_backend.signals import backend_restart_required


class TestCases(TestCase):
    def test_backend_restart_required_signal(self):
        self.assertFalse(BackendSettings.get_solo().restart_required)

        backend_restart_required.send_robust(None)

        self.assertTrue(BackendSettings.get_solo().restart_required)
