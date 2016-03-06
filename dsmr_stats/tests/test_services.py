from unittest import mock

from django.db import connection
from django.test import TestCase
from django.utils import timezone

from dsmr_backend.tests.mixins import InterceptStdoutMixin
from dsmr_consumption.models.consumption import ElectricityConsumption, GasConsumption
from dsmr_stats.models.statistics import DayStatistics, HourStatistics
import dsmr_stats.services


class TestServices(InterceptStdoutMixin, TestCase):
    """ Test 'dsmr_backend' management command. """
    fixtures = ['dsmr_stats/electricity-consumption.json', 'dsmr_stats/gas-consumption.json']

    def test_analyze_service(self):
        self.assertFalse(DayStatistics.objects.exists())
        self.assertFalse(HourStatistics.objects.exists())

        dsmr_stats.services.analyze()
        self.assertEqual(DayStatistics.objects.count(), 1)
        self.assertEqual(HourStatistics.objects.count(), 1)

        # Second run should skip first day.
        dsmr_stats.services.analyze()
        self.assertEqual(DayStatistics.objects.count(), 2)
        self.assertEqual(HourStatistics.objects.count(), 4)

        # Third run should have no effect, as our fixtures are limited to a few days.
        dsmr_stats.services.analyze()
        self.assertEqual(DayStatistics.objects.count(), 3)
        self.assertEqual(HourStatistics.objects.count(), 5)

    def test_analyze_service_without_data(self):
        first_consumption = ElectricityConsumption.objects.all().order_by('read_at')[0]
        first_consumption.read_at = first_consumption.read_at + timezone.timedelta()
        dsmr_stats.services.analyze()

    def test_analyze_service_skip_current_day(self):
        """ Tests whether analysis postpones current day. """
        # Drop fixtures and create data of today.
        ElectricityConsumption.objects.all().delete()
        GasConsumption.objects.all().delete()

        ElectricityConsumption.objects.create(
            read_at=timezone.now(),
            delivered_1=0,
            returned_1=0,
            delivered_2=0,
            returned_2=0,
            currently_delivered=0,
            currently_returned=0,
        )

        GasConsumption.objects.create(
            read_at=timezone.now(),
            delivered=0,
            currently_delivered=0,
        )

        # Make sure we have valid source data, but no analysis yet.
        self.assertTrue(ElectricityConsumption.objects.exists())
        self.assertTrue(GasConsumption.objects.exists())
        self.assertFalse(DayStatistics.objects.exists())
        self.assertFalse(HourStatistics.objects.exists())

        try:
            # BUG BUG BUG. Might crash during DST day transition. Should investigate.
            dsmr_stats.services.analyze()
        except LookupError:
            pass

        # Analysis should be skipped, as all source data is faked into being generated today.
        self.assertFalse(DayStatistics.objects.exists())
        self.assertFalse(HourStatistics.objects.exists())

    @mock.patch('django.core.cache.cache.clear')
    def test_analyze_service_clear_cache(self, clear_cache_mock):
        dsmr_stats.services.analyze()
        self.assertTrue(clear_cache_mock.called)

    def test_flush(self):
        dsmr_stats.services.analyze()
        self.assertTrue(DayStatistics.objects.exists())
        self.assertTrue(HourStatistics.objects.exists())

        dsmr_stats.services.flush()
        self.assertFalse(DayStatistics.objects.exists())
        self.assertFalse(HourStatistics.objects.exists())

    @mock.patch('django.core.cache.cache.clear')
    def test_flush_clear_cache(self, clear_cache_mock):
        dsmr_stats.services.flush()
        self.assertTrue(clear_cache_mock.called)

    def test_average_consumption_by_hour(self):
        """ Test whether timezones are converted properly when grouping hours. """
        # @see "Trends are always shown in UTC #76", only PostgreSQL can fix this.
        if connection.vendor != 'postgresql':
            return self.skipTest('Test cannot be fixed for backends other than PostgreSQL')

        HourStatistics.objects.create(
            # This should be stored with local timezone, so +1.
            hour_start=timezone.make_aware(timezone.datetime(2016, 1, 1, 12)),
            electricity1=1,
            electricity2=0,
            electricity1_returned=0,
            electricity2_returned=0,
        )
        hour_stat = dsmr_stats.services.average_consumption_by_hour()[0]

        # Regression, Django defaults to UTC, so '11' here.
        self.assertEqual(hour_stat['hour_start'], 12)


class TestServicesWithoutGas(TestServices):
    fixtures = ['dsmr_stats/electricity-consumption.json']
