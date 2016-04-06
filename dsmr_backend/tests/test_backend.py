from unittest import mock

from django.core.management import CommandError
from django.test import TestCase
from django.conf import settings

from dsmr_backend.tests.mixins import InterceptStdoutMixin
import dsmr_backend.signals


class TestBackend(InterceptStdoutMixin, TestCase):
    @mock.patch('dsmr_backend.signals.backend_called.send_robust')
    def test_backend_creation_signal(self, signal_mock):
        """ Test outgoing signal. """
        self.assertFalse(signal_mock.called)
        self._intercept_command_stdout('dsmr_backend')
        self.assertTrue(signal_mock.called)

    def test_robust_signal(self):
        """ Test whether the signal is robust, handling any exceptions. """

        def _fake_signal_troublemaker(*args, **kwargs):
            raise BrokenPipeError("Signal receiver crashed for some reason...")

        dsmr_backend.signals.backend_called.connect(receiver=_fake_signal_troublemaker)

        with self.assertRaises(CommandError):
            # Signal should crash, rasing a command error.
            self._intercept_command_stdout('dsmr_backend')

        # We must disconnect to prevent other tests from failing, since this is no database action.
        dsmr_backend.signals.backend_called.disconnect(receiver=_fake_signal_troublemaker)

    def test_supported_vendors(self):
        """ Check whether supported vendors is as expected. """
        self.assertEqual(
            settings.DSMR_SUPPORTED_DB_VENDORS,
            ('postgresql', 'mysql')
        )

    def test_timezone(self):
        """ Verify timezone setting, as it should never be altered. """
        self.assertEqual(settings.TIME_ZONE, 'Europe/Amsterdam')

    def test_version(self):
        """ Verify version setting. """
        self.assertIsNotNone(settings.DSMR_VERSION)

    def test_pending_migrations(self):
        """ Tests whether there are any model changes, which are not reflected in migrations. """
        self.assertEqual(
            self._intercept_command_stdout('makemigrations', dry_run=True),
            'No changes detected\n',
            'Pending model changes found, missing in migrations!'
        )
