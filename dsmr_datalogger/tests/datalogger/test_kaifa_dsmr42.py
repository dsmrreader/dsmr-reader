from datetime import datetime
from decimal import Decimal

from django.test import TestCase
import pytz

from dsmr_backend.tests.mixins import InterceptCommandStdoutMixin
from dsmr_datalogger.models.reading import DsmrReading
from dsmr_datalogger.models.statistics import MeterStatistics
from dsmr_datalogger.models.settings import DataloggerSettings
from dsmr_datalogger.tests.datalogger.mixins import FakeDsmrReadingMixin


class TestDatalogger(FakeDsmrReadingMixin, InterceptCommandStdoutMixin, TestCase):
    """Kaifa DSMR v4.2, without gas support."""

    def _dsmr_dummy_data(self):
        return [
            "/KFM5KAIFA-METER\r\n",
            "\r\n",
            "1-3:0.2.8(42)\r\n",
            "0-0:1.0.0(160303164347W)\r\n",
            "0-0:96.1.1(xxxxxxxxxxxxxxxxxxxxxxxxxxxxxx)\r\n",
            "1-0:1.8.1(001073.079*kWh)\r\n",
            "1-0:1.8.2(001263.199*kWh)\r\n",
            "1-0:2.8.1(000000.000*kWh)\r\n",
            "1-0:2.8.2(000000.000*kWh)\r\n",
            "0-0:96.14.0(0002)\r\n",
            "1-0:1.7.0(00.143*kW)\r\n",
            "1-0:2.7.0(00.000*kW)\r\n",
            "0-0:96.7.21(00006)\r\n",
            "0-0:96.7.9(00003)\r\n",
            "1-0:99.97.0(1)(0-0:96.7.19)(000101000001W)(2147483647*s)\r\n",
            "1-0:32.32.0(00000)\r\n",
            "1-0:32.36.0(00000)\r\n",
            "0-0:96.13.1()\r\n",
            "0-0:96.13.0()\r\n",
            "1-0:31.7.0(000*A)\r\n",
            "1-0:21.7.0(00.143*kW)\r\n",
            "1-0:22.7.0(00.321*kW)\r\n",
            "!0422\n",
        ]

    def test_reading_creation(self):
        """Test whether dsmr_datalogger can insert a reading for Kaifa DSMR v4.2."""
        self.assertFalse(DsmrReading.objects.exists())
        self._fake_dsmr_reading()
        self.assertTrue(DsmrReading.objects.exists())

    def test_reading_values(self):
        """Test whether dsmr_datalogger reads the correct values."""
        DataloggerSettings.get_solo()

        self._fake_dsmr_reading()
        self.assertTrue(DsmrReading.objects.exists())
        reading = DsmrReading.objects.get()
        self.assertEqual(
            reading.timestamp, datetime(2016, 3, 3, 15, 43, 47, tzinfo=pytz.UTC)
        )
        self.assertEqual(reading.electricity_delivered_1, Decimal("1073.079"))
        self.assertEqual(reading.electricity_returned_1, Decimal("0"))
        self.assertEqual(reading.electricity_delivered_2, Decimal("1263.199"))
        self.assertEqual(reading.electricity_returned_2, Decimal("0"))
        self.assertEqual(reading.electricity_currently_delivered, Decimal("0.143"))
        self.assertEqual(reading.electricity_currently_returned, Decimal("0"))
        self.assertIsNone(reading.extra_device_timestamp)
        self.assertIsNone(reading.extra_device_delivered)
        self.assertEqual(reading.phase_currently_delivered_l1, Decimal("0.143"))
        self.assertIsNone(reading.phase_currently_delivered_l2)
        self.assertIsNone(reading.phase_currently_delivered_l3)
        self.assertEqual(reading.phase_currently_returned_l1, Decimal("0.321"))
        self.assertIsNone(reading.phase_currently_returned_l2)
        self.assertIsNone(reading.phase_currently_returned_l3)
        self.assertIsNone(reading.phase_voltage_l1)
        self.assertIsNone(reading.phase_voltage_l2)
        self.assertIsNone(reading.phase_voltage_l3)
        self.assertEqual(reading.phase_power_current_l1, 0)
        self.assertEqual(reading.phase_power_current_l2, None)
        self.assertEqual(reading.phase_power_current_l3, None)

        meter_statistics = MeterStatistics.get_solo()
        self.assertEqual(meter_statistics.dsmr_version, "42")
        self.assertEqual(meter_statistics.electricity_tariff, 2)
        self.assertEqual(meter_statistics.power_failure_count, 6)
        self.assertEqual(meter_statistics.long_power_failure_count, 3)
        self.assertEqual(meter_statistics.voltage_sag_count_l1, 0)
        self.assertIsNone(meter_statistics.voltage_sag_count_l2)
        self.assertIsNone(meter_statistics.voltage_sag_count_l3)
        self.assertEqual(meter_statistics.voltage_swell_count_l1, 0)
        self.assertIsNone(meter_statistics.voltage_swell_count_l2)
        self.assertIsNone(meter_statistics.voltage_swell_count_l3)
