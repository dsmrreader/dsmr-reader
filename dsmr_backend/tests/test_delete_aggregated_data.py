from unittest import mock

from django.test.testcases import TestCase

from dsmr_backend.tests.mixins import InterceptStdoutMixin
from dsmr_datalogger.models.reading import DsmrReading


@mock.patch('dsmr_consumption.services.clear_consumption')
@mock.patch('dsmr_stats.services.clear_statistics')
class TestManagementCommand(InterceptStdoutMixin, TestCase):
    fixtures = ['dsmr_backend/test_dsmrreading.json']

    def test_clear_consumption(self, statistics_mock, consumption_mock):
        self.assertFalse(statistics_mock.called)
        self.assertFalse(consumption_mock.called)
        self.assertTrue(DsmrReading.objects.processed().exists())
        self._intercept_command_stdout('dsmr_backend_delete_aggregated_data', consumption=True)
        self.assertFalse(statistics_mock.called)
        self.assertTrue(consumption_mock.called)
        self.assertTrue(DsmrReading.objects.processed().exists())

    def test_clear_statistics(self, statistics_mock, consumption_mock):
        self.assertFalse(statistics_mock.called)
        self.assertFalse(consumption_mock.called)
        self.assertTrue(DsmrReading.objects.processed().exists())
        self._intercept_command_stdout('dsmr_backend_delete_aggregated_data', statistics=True)
        self.assertTrue(statistics_mock.called)
        self.assertFalse(consumption_mock.called)
        self.assertTrue(DsmrReading.objects.processed().exists())

    def test_clear_readings(self, statistics_mock, consumption_mock):
        self.assertFalse(statistics_mock.called)
        self.assertFalse(consumption_mock.called)
        self.assertTrue(DsmrReading.objects.processed().exists())
        self._intercept_command_stdout('dsmr_backend_delete_aggregated_data', readings=True)
        self.assertFalse(statistics_mock.called)
        self.assertFalse(consumption_mock.called)
        self.assertFalse(DsmrReading.objects.processed().exists())
