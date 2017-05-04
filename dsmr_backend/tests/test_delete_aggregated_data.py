from unittest import mock

from django.test.testcases import TestCase
from django.core.management.base import CommandError

from dsmr_backend.tests.mixins import InterceptStdoutMixin
from dsmr_datalogger.models.reading import DsmrReading


class TestManagementCommand(InterceptStdoutMixin, TestCase):
    fixtures = ['dsmr_backend/test_dsmrreading.json']

    @mock.patch('dsmr_consumption.services.clear_consumption')
    @mock.patch('dsmr_stats.services.clear_statistics')
    def test_dsmr_stats_clear_statistics(self, *mocks):
        expected_error = 'Intended usage is NOT production! Force by using --ack-to-delete-my-data'

        self.assertTrue(DsmrReading.objects.filter(processed=True).exists())

        with self.assertRaisesMessage(CommandError, expected_error):
            self._intercept_command_stdout('dsmr_backend_delete_aggregated_data')

        self.assertFalse(all([x.called for x in mocks]))
        self._intercept_command_stdout('dsmr_backend_delete_aggregated_data', acked_warning=True)
        self.assertTrue(all([x.called for x in mocks]))

        self.assertFalse(DsmrReading.objects.filter(processed=True).exists())
