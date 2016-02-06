from unittest import mock

from django.core.management import call_command
from django.test import TestCase
from django.conf import settings


class TestBackend(TestCase):
    @mock.patch('dsmr_backend.signals.backend_called.send_robust')
    def test_consumption_creation_signal(self, signal_mock):
        """ Test outgoing signal. """
        self.assertFalse(signal_mock.called)
        call_command('dsmr_backend')
        self.assertTrue(signal_mock.called)

    def test_supported_vendors(self):
        """ Check whether supported vendors is as expected. """
        self.assertEqual(
            settings.DSMR_SUPPORTED_DB_VENDORS,
            ('postgresql', 'mysql')
        )
