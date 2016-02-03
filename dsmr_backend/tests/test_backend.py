from unittest import mock

from django.test import TestCase
from django.core.management import call_command


class TestBackend(TestCase):
    @mock.patch('dsmr_backend.signals.backend_called.send_robust')
    def test_consumption_creation_signal(self, signal_mock):
        """ Test dsmr_backend signal trigger. """
        self.assertFalse(signal_mock.called)
        call_command('dsmr_backend')
        self.assertTrue(signal_mock.called)
