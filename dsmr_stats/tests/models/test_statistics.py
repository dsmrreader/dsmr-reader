from django.test import TestCase
from django.utils import timezone

from dsmr_stats.models.statistics import HourStatistics
import dsmr_stats.services


class TestStatistics(TestCase):
    def setUp(self):
        self.instance = HourStatistics.objects.create(
            # This should be stored with local timezone, so +1.
            hour_start=timezone.now(),
            electricity1=1,
            electricity2=1,
            electricity1_returned=1,
            electricity2_returned=1,
            # Gas MUST be omitted to trigger default.
        )

    def test_hour_statistics_average(self):
        """ #100: Empty gas readings mess up average. """
        average_consumption = dsmr_stats.services.average_consumption_by_hour()
        self.assertEqual(average_consumption[0]['avg_gas'], 0)  # Would have been 'None' before.
