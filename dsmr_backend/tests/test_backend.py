from unittest import mock

from django.core.management import call_command, CommandError
from django.test import TestCase
from django.conf import settings

import dsmr_backend.signals


class TestBackend(TestCase):
    @mock.patch('dsmr_backend.signals.backend_called.send_robust')
    def test_backend_creation_signal(self, signal_mock):
        """ Test outgoing signal. """
        self.assertFalse(signal_mock.called)
        call_command('dsmr_backend')
        self.assertTrue(signal_mock.called)

    def test_robust_signal(self):
        """ Test whether the signal is robust, handling any exceptions. """

        def _trouble_making_callback(*args, **kwargs):
            raise BrokenPipeError("Signal receiver crashed for some reason...")

        dsmr_backend.signals.backend_called.connect(receiver=_trouble_making_callback)

        with self.assertRaises(CommandError):
            # Signal should crashs, rasing a command error.
            call_command('dsmr_backend')

    def test_supported_vendors(self):
        """ Check whether supported vendors is as expected. """
        self.assertEqual(
            settings.DSMR_SUPPORTED_DB_VENDORS,
            ('postgresql', 'mysql')
        )
