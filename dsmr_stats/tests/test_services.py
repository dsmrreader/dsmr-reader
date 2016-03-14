from unittest import mock

from django.db import connection
from django.test import TestCase
from django.utils import timezone

from dsmr_backend.tests.mixins import InterceptStdoutMixin
from dsmr_consumption.models.consumption import ElectricityConsumption, GasConsumption
from dsmr_stats.models.statistics import DayStatistics, HourStatistics
import dsmr_backend.services
import dsmr_stats.services


class TestServices(InterceptStdoutMixin, TestCase):
    """ Test 'dsmr_backend' management command. """
    fixtures = ['dsmr_stats/electricity-consumption.json', 'dsmr_stats/gas-consumption.json']

    def _get_statistics_dict(self, target_date):
        """ Used multiple times to setup proper day statistics data. """
        return {
            'day': target_date.date(),
            'total_cost': 39,
            'electricity1': 100,
            'electricity1_cost': 1,
            'electricity1_returned': 11,
            'electricity2': 200,
            'electricity2_cost': 2,
            'electricity2_returned': 22,
            'gas': 300,
            'gas_cost': 3,
        }

    @mock.patch('django.utils.timezone.now')
    def test_analyze_service(self, now_mock):
        self.assertTrue(ElectricityConsumption.objects.exists())
        self.assertFalse(DayStatistics.objects.exists())
        self.assertFalse(HourStatistics.objects.exists())

        # This should delay statistics generation.
        now_mock.return_value = timezone.make_aware(
            timezone.datetime(2015, 12, 13, hour=1, minute=5)
        )
        dsmr_stats.services.analyze()

        if dsmr_backend.services.get_capabilities(capability='gas'):
            self.assertEqual(DayStatistics.objects.count(), 0)
            self.assertEqual(HourStatistics.objects.count(), 0)
        else:
            self.assertEqual(DayStatistics.objects.count(), 1)
            self.assertEqual(HourStatistics.objects.count(), 3)

        # Now we exceed the delay threshold, causing stats to be generated.
        now_mock.return_value += timezone.timedelta(minutes=15)
        dsmr_stats.services.analyze()

        if dsmr_backend.services.get_capabilities(capability='gas'):
            self.assertEqual(DayStatistics.objects.count(), 1)
            self.assertEqual(HourStatistics.objects.count(), 3)
        else:
            self.assertEqual(DayStatistics.objects.count(), 2)
            self.assertEqual(HourStatistics.objects.count(), 4)

        # Second run should skip first day.
        dsmr_stats.services.analyze()
        self.assertEqual(DayStatistics.objects.count(), 2)
        self.assertEqual(HourStatistics.objects.count(), 4)

        # Third run should have no effect, as our fixtures are limited to a few days.
        dsmr_stats.services.analyze()
        self.assertEqual(DayStatistics.objects.count(), 2)
        self.assertEqual(HourStatistics.objects.count(), 4)

    def test_analyze_service_without_data(self):
        first_consumption = ElectricityConsumption.objects.all().order_by('read_at')[0]
        first_consumption.read_at = first_consumption.read_at + timezone.timedelta()
        dsmr_stats.services.analyze()

    @mock.patch('django.utils.timezone.now')
    def test_analyze_service_skip_current_day(self, now_mock):
        """ Tests whether analysis postpones current day. """
        now_mock.return_value = timezone.make_aware(
            timezone.datetime(2016, 1, 1)
        )

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
        HourStatistics.objects.create(
            # This should be stored with local timezone, so +1.
            hour_start=timezone.make_aware(timezone.datetime(2016, 1, 1, 12)),
            electricity1=1,
            electricity2=0,
            electricity1_returned=0,
            electricity2_returned=0,
        )
        hour_stat = dsmr_stats.services.average_consumption_by_hour()[0]

        # @see "Trends are always shown in UTC #76", only PostgreSQL can fix this.
        if connection.vendor == 'postgresql':
            # Regression, Django defaults to UTC, so '11' here.
            self.assertEqual(hour_stat['hour_start'], 12)
        else:
            return self.skipTest('Test cannot be fixed for backends other than PostgreSQL')

    def test_range_statistics(self):
        target_date = timezone.make_aware(timezone.datetime(2016, 1, 1, 12))
        statistics_dict = self._get_statistics_dict(target_date)
        DayStatistics.objects.create(**statistics_dict)

        # Fetch inside our expected range.
        statistics = dsmr_stats.services.range_statistics(
            start=target_date, end=target_date + timezone.timedelta(days=1)
        )
        self.assertEqual(statistics['total_cost'], 39)
        self.assertEqual(statistics['electricity1'], 100)
        self.assertEqual(statistics['electricity1_cost'], 1)
        self.assertEqual(statistics['electricity1_returned'], 11)
        self.assertEqual(statistics['electricity2'], 200)
        self.assertEqual(statistics['electricity2_cost'], 2)
        self.assertEqual(statistics['electricity2_returned'], 22)
        self.assertEqual(statistics['gas'], 300)
        self.assertEqual(statistics['gas_cost'], 3)

        # Now we fetch one outside our range.
        no_statistics = dsmr_stats.services.range_statistics(
            target_date - timezone.timedelta(days=1), target_date
        )
        self.assertIsNone(no_statistics['total_cost'])

    def test_month_statistics(self):
        target_date = timezone.make_aware(timezone.datetime(2016, 1, 1, 12))

        # Create statistics for multiple days in month, and beyond.
        for x in range(0, 40):
            DayStatistics.objects.create(
                **self._get_statistics_dict(target_date + timezone.timedelta(days=x))
            )

        monthly = dsmr_stats.services.month_statistics(target_date=target_date)
        daily = self._get_statistics_dict(target_date)
        days_in_month = 31

        # Now we just verify whether the expected amount of days is fetched and summarized.
        # Since January only has 31 days and we we've generated 40, we should multiply by 31.
        self.assertEqual(monthly['total_cost'], daily['total_cost'] * days_in_month)
        self.assertEqual(monthly['electricity1'], daily['electricity1'] * days_in_month)
        self.assertEqual(monthly['electricity1_cost'], daily['electricity1_cost'] * days_in_month)
        self.assertEqual(monthly['electricity1_returned'], daily['electricity1_returned'] * days_in_month)
        self.assertEqual(monthly['electricity2'], daily['electricity2'] * days_in_month)
        self.assertEqual(monthly['electricity2_cost'], daily['electricity2_cost'] * days_in_month)
        self.assertEqual(monthly['electricity2_returned'], daily['electricity2_returned'] * days_in_month)
        self.assertEqual(monthly['gas'], daily['gas'] * days_in_month)
        self.assertEqual(monthly['gas_cost'], daily['gas_cost'] * days_in_month)


class TestServicesWithoutGas(TestServices):
    fixtures = ['dsmr_stats/electricity-consumption.json']
