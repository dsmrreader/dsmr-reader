from datetime import datetime
from decimal import Decimal

from django.test import TestCase
import pytz

from dsmr_backend.tests.mixins import InterceptStdoutMixin
from dsmr_datalogger.models.reading import DsmrReading
from dsmr_datalogger.models.statistics import MeterStatistics
from dsmr_datalogger.models.settings import DataloggerSettings
from dsmr_datalogger.tests.datalogger.mixins import FakeDsmrReadingMixin


class TestDatalogger(FakeDsmrReadingMixin, InterceptStdoutMixin, TestCase):
    """ Landis+Gyr 350 DSMR v4.2. """

    def _dsmr_dummy_data(self):
        return [
            "/XMX5LGBBFFB123456789\r\n",
            "\r\n",
            "1-3:0.2.8(42)\r\n",
            "0-0:1.0.0(160210203034W)\r\n",
            "0-0:96.1.1(xxxxxxxxxxxxxxxxxxxxxxxxxxxxxx)\r\n",
            "1-0:1.8.1(000756.849*kWh)\r\n",
            "1-0:2.8.1(000000.000*kWh)\r\n",
            "1-0:1.8.2(000714.405*kWh)\r\n",
            "1-0:2.8.2(000000.000*kWh)\r\n",
            "0-0:96.14.0(0002)\r\n",
            "1-0:1.7.0(00.111*kW)\r\n",
            "1-0:2.7.0(00.000*kW)\r\n",
            "0-0:96.7.21(00003)\r\n",
            "0-0:96.7.9(00000)\r\n",
            "1-0:99.97.0(0)(0-0:96.7.19)\r\n",
            "1-0:32.32.0(00002)\r\n",
            "1-0:52.32.0(00002)\r\n",
            "1-0:72.32.0(00000)\r\n",
            "1-0:32.36.0(00000)\r\n",
            "1-0:52.36.0(00000)\r\n",
            "1-0:72.36.0(00000)\r\n",
            "0-0:96.13.1()\r\n",
            "0-0:96.13.0()\r\n",
            "1-0:31.7.0(111*A)\r\n",
            "1-0:51.7.0(222*A)\r\n",
            "1-0:71.7.0(333*A)\r\n",
            "1-0:21.7.0(00.123*kW)\r\n",
            "1-0:41.7.0(00.456*kW)\r\n",
            "1-0:61.7.0(00.789*kW)\r\n",
            "1-0:22.7.0(00.222*kW)\r\n",
            "1-0:42.7.0(00.444*kW)\r\n",
            "1-0:62.7.0(00.666*kW)\r\n",
            "0-1:24.1.0(003)\r\n",
            "0-1:96.1.0(xxxxxxxxxxxxxxxxxxxxxxxxxxxxxx)\r\n",
            "0-1:24.2.1(160210200000W)(01197.484*m3)\r\n",
            "!8774\n",
        ]

    def test_reading_creation(self):
        """ Test whether dsmr_datalogger can insert a reading for Landis+Gyr 350 DSMR v4.2. """
        self.assertFalse(DsmrReading.objects.exists())
        self._fake_dsmr_reading()
        self.assertTrue(DsmrReading.objects.exists())

    def test_reading_values(self):
        """ Test whether dsmr_datalogger reads the correct values. """
        DataloggerSettings.get_solo()

        self._fake_dsmr_reading()
        self.assertTrue(DsmrReading.objects.exists())
        reading = DsmrReading.objects.get()
        self.assertEqual(reading.timestamp, datetime(2016, 2, 10, 19, 30, 34, tzinfo=pytz.UTC))
        self.assertEqual(reading.electricity_delivered_1, Decimal('756.849'))
        self.assertEqual(reading.electricity_returned_1, Decimal('0'))
        self.assertEqual(reading.electricity_delivered_2, Decimal('714.405'))
        self.assertEqual(reading.electricity_returned_2, Decimal('0'))
        self.assertEqual(reading.electricity_currently_delivered, Decimal('0.111'))
        self.assertEqual(reading.electricity_currently_returned, Decimal('0'))
        self.assertEqual(reading.extra_device_timestamp, datetime(2016, 2, 10, 19, 0, 0, tzinfo=pytz.UTC))
        self.assertEqual(reading.extra_device_delivered, Decimal('1197.484'))
        self.assertEqual(reading.phase_currently_delivered_l1, Decimal('0.123'))
        self.assertEqual(reading.phase_currently_delivered_l2, Decimal('0.456'))
        self.assertEqual(reading.phase_currently_delivered_l3, Decimal('0.789'))
        self.assertEqual(reading.phase_currently_returned_l1, Decimal('0.222'))
        self.assertEqual(reading.phase_currently_returned_l2, Decimal('0.444'))
        self.assertEqual(reading.phase_currently_returned_l3, Decimal('0.666'))
        self.assertIsNone(reading.phase_voltage_l1)
        self.assertIsNone(reading.phase_voltage_l2)
        self.assertIsNone(reading.phase_voltage_l3)
        self.assertEqual(reading.phase_power_current_l1, 111)
        self.assertEqual(reading.phase_power_current_l2, 222)
        self.assertEqual(reading.phase_power_current_l3, 333)

        # Different data source.
        meter_statistics = MeterStatistics.get_solo()
        self.assertEqual(meter_statistics.dsmr_version, '42')
        self.assertEqual(meter_statistics.electricity_tariff, 2)
        self.assertEqual(meter_statistics.power_failure_count, 3)
        self.assertEqual(meter_statistics.long_power_failure_count, 0)
        self.assertEqual(meter_statistics.voltage_sag_count_l1, 2)
        self.assertEqual(meter_statistics.voltage_sag_count_l2, 2)
        self.assertEqual(meter_statistics.voltage_sag_count_l3, 0)
        self.assertEqual(meter_statistics.voltage_swell_count_l1, 0)
        self.assertEqual(meter_statistics.voltage_swell_count_l2, 0)
        self.assertEqual(meter_statistics.voltage_swell_count_l3, 0)
