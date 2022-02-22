from unittest import mock

from django.test.testcases import TestCase
from django.utils import timezone

from dsmr_backend.tests.mixins import InterceptCommandStdoutMixin
from dsmr_stats.models.statistics import DayStatistics


@mock.patch('dsmr_notification.services.send_notification')
class TestManagementCommand(InterceptCommandStdoutMixin, TestCase):
    def test_dsmr_notification_test(self, service_mock):
        self.assertFalse(service_mock.called)
        self._intercept_command_stdout('dsmr_notification_test')
        self.assertTrue(service_mock.called)

    def test_dsmr_notification_test_with_statistics(self, service_mock):
        DayStatistics.objects.create(
            day=timezone.make_aware(timezone.datetime(2022, 1, 1)).date(),
            total_cost=12345,
            electricity1=1,
            electricity2=2,
            electricity1_returned=3,
            electricity2_returned=4,
            gas=5,
            electricity1_cost=0,
            electricity2_cost=0,
            gas_cost=0,
        )

        self.assertFalse(service_mock.called)
        self._intercept_command_stdout('dsmr_notification_test')
        self.assertTrue(service_mock.called)
