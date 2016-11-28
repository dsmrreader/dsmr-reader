from unittest import mock

from django.test.testcases import TestCase
from django.core.management.base import CommandError

from dsmr_backend.tests.mixins import InterceptStdoutMixin


class TestManagementCommand(InterceptStdoutMixin, TestCase):
    def test_dsmr_stats_clear_statistics(self):
        expected_error = 'Intended usage is NOT production! Force by using --ack-to-delete-my-data'

        with self.assertRaisesMessage(CommandError, expected_error):
            self._intercept_command_stdout('dsmr_stats_clear_statistics')

        with mock.patch('dsmr_stats.services.clear_statistics') as service_mock:
            self.assertFalse(service_mock.called)
            self._intercept_command_stdout('dsmr_stats_clear_statistics', acked_warning=True)
            self.assertTrue(service_mock.called)
