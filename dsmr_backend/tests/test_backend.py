from unittest import mock

from django.test import TestCase

from dsmr_backend.tests.mixins import InterceptStdoutMixin
import dsmr_backend.services


class TestBackend(InterceptStdoutMixin, TestCase):
    @mock.patch('dsmr_backend.services.process_scheduled_calls')
    def test_process_scheduled_calls_called(self, service_mock):
        """ Test whether the backend commands calls the global service. """
        self.assertFalse(service_mock.called)
        self._intercept_command_stdout('dsmr_backend', run_once=True)
        self.assertTrue(service_mock.called)

    @mock.patch('traceback.format_tb')
    @mock.patch('dsmr_backend.models.ScheduledCall.execute')
    def test_exception_handling(self, execute_mock, format_tb_mock):
        """ Tests signal exception handling. """
        execute_mock.side_effect = AssertionError("Crash")

        self.assertFalse(format_tb_mock.called)
        dsmr_backend.services.process_scheduled_calls()
        self.assertTrue(format_tb_mock.called)
