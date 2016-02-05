from unittest import mock

from django.test import TestCase

from dsmr_backend.tests.mixins import CallCommandStdoutMixin
from dsmr_stats.models.settings import StatsSettings
from dsmr_stats.models.statistics import DayStatistics
import dsmr_stats.services


class TestServices(CallCommandStdoutMixin, TestCase):
    """ Test 'dsmr_backend' management command. """
    fixtures = ['dsmr_stats/electricity-consumption.json', 'dsmr_stats/gas-consumption.json']

    @mock.patch('dsmr_stats.services.analyze')
    def test_analyze_service_signal_trigger(self, analyze_mock):
        """ Test incoming signal communication. """
        self.assertFalse(analyze_mock.called)
        self._call_command_stdout('dsmr_backend')
        self.assertTrue(analyze_mock.called)

    @mock.patch('dsmr_stats.services.create_daily_statistics')
    def test_analyze_service_track_setting(self, create_daily_statistics_mock):
        """ Test whether we respect the statistics tracking setting. """
        stats_settings = StatsSettings.get_solo()
        stats_settings.track = False
        stats_settings.save()

        self.assertFalse(create_daily_statistics_mock.called)
        dsmr_stats.services.analyze()
        self.assertFalse(create_daily_statistics_mock.called)

    def test_analyze_service(self):
        self.assertFalse(DayStatistics.objects.exists())

        dsmr_stats.services.analyze()
        self.assertEqual(DayStatistics.objects.count(), 1)

        # Second run should skip first day.
        dsmr_stats.services.analyze()
        self.assertEqual(DayStatistics.objects.count(), 2)

        # Third run should have no effect, as our fixtures are limited to two days.
        dsmr_stats.services.analyze()
        self.assertEqual(DayStatistics.objects.count(), 2)

    def test_flush(self):
        dsmr_stats.services.analyze()
        self.assertTrue(DayStatistics.objects.exists())

        dsmr_stats.services.flush()
        self.assertFalse(DayStatistics.objects.exists())
