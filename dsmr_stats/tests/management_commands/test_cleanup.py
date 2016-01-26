from django.conf import settings
from django.test import TestCase
from django.utils import timezone

from dsmr_stats.tests.mixins import CallCommandStdoutMixin
from dsmr_datalogger.models.reading import DsmrReading


class TestDsmrStatsCleanup(CallCommandStdoutMixin, TestCase):
    """ Test 'dsmr_stats_cleanup' management command. """
    fixtures = ['dsmr_stats/test_dsmrreading.json']

    def setUp(self):
        self.assertEqual(DsmrReading.objects.all().count(), 3)

        # Check fixture date, as we keep moving forward every day.
        now = timezone.now().astimezone(settings.LOCAL_TIME_ZONE).date()
        self.days_diff = (now - DsmrReading.objects.get(pk=1).timestamp.date()).days

    def test_ignore_range(self):
        self._call_command_stdout('dsmr_stats_cleanup', no_input=True, days=self.days_diff + 1)
        self.assertEqual(DsmrReading.objects.all().count(), 3)

    def test_cleanup(self):
        self._call_command_stdout('dsmr_stats_cleanup', no_input=True, days=self.days_diff - 1)
        self.assertEqual(DsmrReading.objects.all().count(), 0)
