from unittest import mock

from django.test import TestCase
from django.utils import timezone

from dsmr_backend.models.schedule import ScheduledProcess
from dsmr_backend.models.settings import BackendSettings
from dsmr_backend.tests.mixins import InterceptCommandStdoutMixin
import dsmr_backend.services.schedule
import dsmr_backend.signals


class TestCases(InterceptCommandStdoutMixin, TestCase):
    @mock.patch('dsmr_backend.signals.backend_called.send_robust')
    @mock.patch('dsmr_backend.services.schedule.execute_scheduled_processes')
    @mock.patch('dsmr_backend.services.persistent_clients.initialize')
    @mock.patch('dsmr_backend.services.persistent_clients.run')
    @mock.patch('dsmr_backend.services.persistent_clients.terminate')
    def test_backend_creation_signal(self, *mocks):
        """ Test outgoing signal and execute_scheduled_processes() being called. """
        for current in mocks:
            self.assertFalse(current.called)

        self._intercept_command_stdout('dsmr_backend', run_once=True)

        for current in mocks:
            self.assertTrue(current.called)

    @mock.patch('dsmr_backend.signals.backend_called.send_robust')
    @mock.patch('dsmr_backend.services.schedule.execute_scheduled_processes')
    @mock.patch('dsmr_backend.services.persistent_clients.initialize')
    @mock.patch('dsmr_backend.services.persistent_clients.run')
    @mock.patch('dsmr_backend.services.persistent_clients.terminate')
    def test_backend_restart_required(self, *mocks):
        """ Test restart flag check. """
        BackendSettings.get_solo().update(restart_required=True)
        self.assertTrue(BackendSettings.get_solo().restart_required)

        # When not implemented correctly this should loop forever, without run_once=True, timing out the tests...
        self._intercept_command_stdout('dsmr_backend')

        self.assertFalse(BackendSettings.get_solo().restart_required)

    @mock.patch('dsmr_notification.services.notify')
    def test_backend_creation_signal_receivers(self, *mocks):
        """ Test whether outgoing signal is received. """
        for current in mocks:
            self.assertFalse(current.called)

        self._intercept_command_stdout('dsmr_backend', run_once=True)

        for current in mocks:
            self.assertTrue(current.called)

    def test_robust_signal(self):
        """ Test whether the signal is robust, handling any exceptions. """

        def _fake_signal_troublemaker(*args, **kwargs):
            raise BrokenPipeError("Signal receiver crashed for some reason...")

        dsmr_backend.signals.backend_called.connect(receiver=_fake_signal_troublemaker)

        # We must disconnect to prevent other tests from failing, since this is no database action.
        dsmr_backend.signals.backend_called.disconnect(receiver=_fake_signal_troublemaker)

    @mock.patch('logging.Logger.error')
    def test_signal_exception_handling(self, logging_mock):
        """ Tests signal exception handling. """
        def _fake_signal_troublemaker(*args, **kwargs):
            raise AssertionError("Crash")

        dsmr_backend.signals.backend_called.connect(receiver=_fake_signal_troublemaker)
        self.assertFalse(logging_mock.called)

        self._intercept_command_stdout('dsmr_backend', run_once=True)
        self.assertTrue(logging_mock.called)

    @mock.patch('dsmr_backend.signals.backend_called.send_robust')
    @mock.patch('logging.Logger.error')
    @mock.patch('dsmr_backend.models.schedule.ScheduledProcess.execute')
    def test_execute_scheduled_processes_error(self, execute_mock, logging_mock, signal_mock):
        """ Test execute_scheduled_processes()'s exception handling. """
        ScheduledProcess.objects.create(name='test', module='fake.module')

        self.assertFalse(execute_mock.called)
        self.assertFalse(logging_mock.called)

        # OK.
        self._intercept_command_stdout('dsmr_backend', run_once=True)

        self.assertTrue(execute_mock.called)
        self.assertFalse(logging_mock.called)

        execute_mock.reset_mock()
        logging_mock.reset_mock()

        # Exception.
        execute_mock.side_effect = Exception("Chaos monkey")
        self._intercept_command_stdout('dsmr_backend', run_once=True)

        self.assertTrue(execute_mock.called)
        self.assertTrue(logging_mock.called)

    @mock.patch('dsmr_backup.services.email.run')
    @mock.patch('dsmr_backend.services.update_checker.run')
    @mock.patch('dsmr_weather.services.run')
    @mock.patch('dsmr_stats.services.run')
    @mock.patch('dsmr_mindergas.services.run')
    @mock.patch('dsmr_consumption.services.run')
    @mock.patch('dsmr_datalogger.services.retention.run')
    @mock.patch('dsmr_backup.services.backup.run')
    @mock.patch('dsmr_dropbox.services.run')
    @mock.patch('dsmr_pvoutput.services.run')
    def test_scheduled_processes_modules(self, *mocks):
        """ Verify the number of processes and that their module is called. """
        ScheduledProcess.objects.all().update(active=True, planned=timezone.now())
        self.assertEqual(ScheduledProcess.objects.all().count(), 10)
        self.assertFalse(any([x.called for x in mocks]))

        dsmr_backend.services.schedule.execute_scheduled_processes()
        self.assertTrue(all([x.called for x in mocks]))
