from unittest import mock

from django.test import TestCase
from django.utils import timezone

from dsmr_stats.apps import check_day_statistics_generation
from dsmr_backend.dto import MonitoringStatusIssue
from dsmr_stats.models.statistics import DayStatistics


class TestStatus(TestCase):
    def setUp(self):
        DayStatistics.objects.create(
            day=timezone.make_aware(timezone.datetime(2000, 1, 1)),
            total_cost=0,
            electricity1=0,
            electricity2=0,
            electricity1_cost=0,
            electricity2_cost=0,
            gas=0,
            gas_cost=0,
            electricity1_returned=0,
            electricity2_returned=0,
        )

    def test_check_day_statistics_generation_no_data(self):
        DayStatistics.objects.all().delete()
        self.assertIsInstance(check_day_statistics_generation(), MonitoringStatusIssue)

    @mock.patch('django.utils.timezone.now')
    def test_check_day_statistics_generation_okay(self, now_mock):
        now_mock.return_value = timezone.make_aware(timezone.datetime(2000, 1, 2))
        self.assertEqual(check_day_statistics_generation(), None)

    @mock.patch('django.utils.timezone.now')
    def test_check_day_statistics_generation_fail(self, now_mock):
        now_mock.return_value = timezone.make_aware(timezone.datetime(2000, 1, 3))
        self.assertIsInstance(check_day_statistics_generation(), MonitoringStatusIssue)
