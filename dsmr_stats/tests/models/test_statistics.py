from django.test import TestCase
from django.utils import timezone

from dsmr_stats.models.statistics import HourStatistics, DayStatistics
import dsmr_stats.services


class TestHourStatistics(TestCase):
    def setUp(self):
        self.instance = HourStatistics.objects.create(
            hour_start=timezone.now(),
            electricity1=1,
            electricity2=1,
            electricity1_returned=2,
            electricity2_returned=2,
            # Gas MUST be omitted to trigger default.
        )

    def test_str(self):
        """ Model should override string formatting. """
        self.assertNotEqual(str(self.instance), 'HourStatistics')

    def test_attributes(self):
        self.assertEqual(self.instance.electricity_merged, 2)
        self.assertEqual(self.instance.electricity_returned_merged, 4)

    def test_hour_statistics_average(self):
        """ #100: Empty gas readings mess up average. """
        average_consumption = dsmr_stats.services.average_consumption_by_hour(max_weeks_ago=4)
        self.assertEqual(average_consumption[0]['avg_gas'], 0)  # Would have been 'None' before.


class TestDayStatistics(TestCase):
    def setUp(self):
        self.instance = DayStatistics.objects.create(
            day=timezone.now().date(),
            total_cost=100,
            electricity1=1,
            electricity2=1,
            electricity1_cost=40,
            electricity2_cost=60,
            electricity1_returned=3,
            electricity2_returned=3,
            # Gas MUST be omitted to trigger default.
        )

    def test_str(self):
        """ Model should override string formatting. """
        self.assertNotEqual(str(self.instance), 'DayStatistics')

    def test_attributes(self):
        self.assertEqual(self.instance.electricity_merged, 2)
        self.assertEqual(self.instance.electricity_returned_merged, 6)
