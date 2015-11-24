from unittest import mock
from datetime import datetime
import warnings

import pytz
from django.core.management import call_command, CommandError
from django.conf import settings
from django.test import TestCase
from django.utils import timezone

from dsmr_stats.models import DsmrReading, ElectricityConsumption, GasConsumption,\
    ElectricityStatistics
from decimal import Decimal


class TestDsmrStatsDatalogger(TestCase):
    """ Test 'dsmr_stats_datalogger' management command. """
    def _dummy_data(self):
        return [
            "/XMX5LGBBFFB231117727\n",
            "\n",
            "\n",
            "1-3:0.2.8(40)\n",
            "0-0:1.0.0(151110192959W)\n",
            "0-0:96.1.1(xxxxxxxxxxxxx)\n",
            "1-0:1.8.1(000510.747*kWh)\n",
            "1-0:2.8.1(000000.000*kWh)\n",
            "1-0:1.8.2(000500.013*kWh)\n",
            "1-0:2.8.2(000000.000*kWh)\n",
            "0-0:96.14.0(0001)\n",
            "1-0:1.7.0(00.192*kW)\n",
            "1-0:2.7.0(00.000*kW)\n",
            "0-0:17.0.0(999.9*kW)\n",
            "0-0:96.3.10(1)\n",
            "0-0:96.7.21(00003)\n",
            "0-0:96.7.9(00000)\n",
            "1-0:99.97.0(0)(0-0:96.7.19)\n",
            "1-0:32.32.0(00002)\n",
            "1-0:52.32.0(00002)\n",
            "1-0:72.32.0(00000)\n",
            "1-0:32.36.0(00000)\n",
            "1-0:52.36.0(00000)\n",
            "1-0:72.36.0(00000)\n",
            "0-0:96.13.1()\n",
            "0-0:96.13.0()\n",
            "1-0:31.7.0(000*A)\n",
            "1-0:51.7.0(000*A)\n",
            "1-0:71.7.0(001*A)\n",
            "1-0:21.7.0(00.000*kW)\n",
            "1-0:41.7.0(00.000*kW)\n",
            "1-0:61.7.0(00.192*kW)\n",
            "1-0:22.7.0(00.000*kW)\n",
            "1-0:42.7.0(00.000*kW)\n",
            "1-0:62.7.0(00.000*kW)\n",
            "0-1:24.1.0(003)\n",
            "0-1:96.1.0(xxxxxxxxxxxxx)\n",
            "0-1:24.2.1(151110190000W)(00845.206*m3)\n",
            "0-1:24.4.0(1)\n",
            "!D19A\n",
        ]

    @mock.patch('serial.Serial.open')
    @mock.patch('serial.Serial.readline')
    def _poll_reading(self, serial_readline_mock, serial_open_mock):
        serial_open_mock.return_value = None
        serial_readline_mock.side_effect = self._dummy_data()

        call_command('dsmr_stats_datalogger')

    def test_reading_creation(self):
        self._poll_reading()
        self.assertGreater(DsmrReading.objects.all().count(), 0)

    def test_reading_values(self):
        self._poll_reading()
        reading = DsmrReading.objects.get(pk=1)
        self.assertEqual(
            reading.timestamp,
            datetime(2015, 11, 10, 18, 29, 59, tzinfo=pytz.UTC)
        )
        self.assertEqual(reading.electricity_delivered_1, Decimal('510.747'))
        self.assertEqual(reading.electricity_returned_1, Decimal('0'))
        self.assertEqual(reading.electricity_delivered_2, Decimal('500.013'))
        self.assertEqual(reading.electricity_returned_2, Decimal('0'))
        self.assertEqual(reading.electricity_tariff, Decimal('1'))
        self.assertEqual(reading.electricity_currently_delivered, Decimal('0.192'))
        self.assertEqual(reading.electricity_currently_returned, Decimal('0'))
        self.assertEqual(reading.power_failure_count, 3)
        self.assertEqual(reading.long_power_failure_count, 0)
        self.assertEqual(reading.voltage_sag_count_l1, 2)
        self.assertEqual(reading.voltage_sag_count_l2, 2)
        self.assertEqual(reading.voltage_sag_count_l3, 0)
        self.assertEqual(reading.voltage_swell_count_l1, 0)
        self.assertEqual(reading.voltage_swell_count_l2, 0)
        self.assertEqual(reading.voltage_swell_count_l3, 0)

        self.assertEqual(
            reading.extra_device_timestamp,
            datetime(2015, 11, 10, 18, 0, 0, tzinfo=pytz.UTC)
        )
        self.assertEqual(reading.extra_device_delivered, Decimal('845.206'))


class TestDsmrStatsPoller(TestCase):
    """ Deprecated legacy support for data poller compatiblity. """
    @mock.patch('serial.Serial.open')
    def test(self, serial_patch):
        # By using this side effect we can verify whether 'dsmr_stats_datalogger' is called.
        serial_patch.side_effect = RuntimeError("Test")

        with self.assertRaises(RuntimeError):
            call_command('dsmr_stats_poller')

        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")

            try:
                call_command('dsmr_stats_poller')
            except RuntimeError:
                pass

            self.assertEqual(len(w), 1)
            self.assertTrue(issubclass(w[-1].category, DeprecationWarning))
            self.assertEqual(
                w[-1].message,
                'dsmr_stats_poller is DEPRECATED, please use dsmr_stats_datalogger'
            )


class TestDsmrStatsCompactor(TestCase):
    """ Test 'dsmr_stats_compactor' management command. """
    fixtures = ['test_dsmrreading.json']

    def setUp(self):
        self.assertEqual(DsmrReading.objects.all().count(), 2)
        self.assertTrue(DsmrReading.objects.unprocessed().exists())

    def test_processing(self):
        call_command('dsmr_stats_compactor')

        self.assertTrue(DsmrReading.objects.processed().exists())
        self.assertFalse(DsmrReading.objects.unprocessed().exists())
        self.assertEqual(ElectricityConsumption.objects.count(), 2)
        self.assertEqual(GasConsumption.objects.count(), 1)

    def test_grouping(self):
        call_command('dsmr_stats_compactor', group_by_minute=True)

        self.assertTrue(DsmrReading.objects.processed().exists())
        self.assertEqual(ElectricityConsumption.objects.count(), 1)
        self.assertEqual(GasConsumption.objects.count(), 1)

    def test_creation(self):
        self.assertFalse(ElectricityStatistics.objects.exists())
        self.assertFalse(ElectricityConsumption.objects.exists())
        self.assertFalse(GasConsumption.objects.exists())

        call_command('dsmr_stats_compactor')

        self.assertTrue(ElectricityStatistics.objects.exists())
        self.assertTrue(ElectricityConsumption.objects.exists())
        self.assertTrue(GasConsumption.objects.exists())

    def test_purge(self):
        call_command('dsmr_stats_compactor')
        self.assertTrue(ElectricityStatistics.objects.exists())
        self.assertTrue(ElectricityConsumption.objects.exists())
        self.assertTrue(GasConsumption.objects.exists())
        self.assertFalse(DsmrReading.objects.unprocessed().exists())

        with self.assertRaises(CommandError):
            call_command('dsmr_stats_compactor', purge=True)

        self.assertFalse(ElectricityStatistics.objects.exists())
        self.assertFalse(ElectricityConsumption.objects.exists())
        self.assertFalse(GasConsumption.objects.exists())
        self.assertTrue(DsmrReading.objects.unprocessed().exists())


class TestDsmrStatsCleanup(TestCase):
    """ Test 'dsmr_stats_cleanup' management command. """
    fixtures = ['test_dsmrreading.json']

    def setUp(self):
        self.assertEqual(DsmrReading.objects.all().count(), 2)

        # Check fixture date, as we keep moving forward every day.
        now = timezone.now().astimezone(settings.LOCAL_TIME_ZONE).date()
        self.days_diff = (now - DsmrReading.objects.get(pk=1).timestamp.date()).days

    def test_ignore_range(self):
        call_command('dsmr_stats_cleanup', no_input=True, days=self.days_diff + 1)
        self.assertEqual(DsmrReading.objects.all().count(), 2)

    def test_cleanup(self):
        call_command('dsmr_stats_cleanup', no_input=True, days=self.days_diff - 1)
        self.assertEqual(DsmrReading.objects.all().count(), 0)
